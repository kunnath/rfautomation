## a helper script to trigger specified CC(cloud connector) version
##
## To use it, you have to set following environmental variables.
##
## export base_url=api.dir.sf-dev1.com ## up to environment
## export env_vc_access_token=b254efc8-9415-4144-8602-2789adf32e80 # access token against VC(videocloud) in the target environment

export REDIRECTOR_URL=camadmin.dir.smartfrog.com
alias curl='2>/dev/null curl -w "\n" -L'

cr_get_devices(){
    local page=0
    local rows=10;
    local params=;
    [[ $# -eq 1 ]] && page=$1
    [[ $# -eq 2 ]] && page=$1 && rows=$2
    [[ $# -eq 0 ]] && params="page=$page&rows=$rows"
    curl -X GET "http://${REDIRECTOR_URL}/api/devices?${params}"
}

cr_get_device(){
    local serialNumber="$1"
    curl -X GET "http://${REDIRECTOR_URL}/api/devices/${serialNumber}"
}

cr_delete_device(){
    local serialNumber="$1"
    curl -X DELETE "http://${REDIRECTOR_URL}/api/devices/${serialNumber}"
}

cr_create_device(){
    local params=""
    params="${params}serialNumber=$1"
    params="${params}&baseUri=https://$2"
    params="${params}&firmwareUri=$3"
    params="${params}&firmwareVersion=$4"
    params="${params}&count=0"
    params="${params}&assignmentUri=https://$2"
    curl -X POST "http://${REDIRECTOR_URL}/api/devices" --data "${params}"
}

qa_cr_set_device(){
    local serialNumber="$1"
    local firmwareVersion="$2"
    local firmwareUri="$3"
    local is_exist=$(cr_get_device $serialNumber)
    [[ -z ${is_exist} ]] && cr_delete_device $serialNumber
    cr_create_device "${serialNumber}" "${base_url}" "${firmwareUri}" "${firmwareVersion}"
}

vc_get_device_info(){
    local serialNumber=$1 # i.e. M045C06110CE6
    curl -X GET --header 'Accept: application/json' 'https://'"${base_url}"'/v1/admin/devices?serialNumber='"${serialNumber}"'&max=1024&access_token='"${env_vc_access_token}" | jq 'if .status == "SUCCESS" and .response.totalCount then .response.items[0] else {} end'
}

vc_get_device_details(){
    local serialNumber=$1 # i.e. M045C06110CE6
    local deviceUuid=$( vc_get_device_info $serialNumber | jq '.uuid?' | sed -e 's#"##g')
    [[ null = $deviceUuid ]] && return 1
    curl -X GET --header 'Accept: application/json' 'https://'"${base_url}"'/v1/admin/devices/'${deviceUuid}'?access_token='"${env_vc_access_token}" | jq 'if .status == "SUCCESS" then .response.device else {} end'
}

vc_get_fw_info(){
    local dest_fw_ver=$1 # i.e. 1.2.48
    curl -X GET --header 'Accept: application/json' 'https://'"${base_url}"'/v1/admin/camFwVersions?max=1024&access_token='"${env_vc_access_token}" 2>/dev/null \
        | jq '.response[] | select((.fwVersion == "'${dest_fw_ver}'") and (.deliveryType == "BASE_CONFIG") and (.hwDeviceName == "SF-SH72D001"))'
}

vc_reboot(){
    local serialNumber=$1 # i.e. M045C06110CE6
    curl -X POST --header 'Accept: application/json' 'https://'"${base_url}"'/v1/admin/devices/'"${serialNumber}"'/reboot?access_token='"${env_vc_access_token}"
}

vc_trigger_fw_update(){
    local target_device_uuid=$1
    local target_fw_uuid=$2
    curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' 'https://'${base_url}'/v1/admin/devices/'${target_device_uuid}'/fw-updates?fwVersionUuid='${target_fw_uuid}'&access_token='${env_vc_access_token}
}

vc_get_fw_update_results(){
    local serialNumber=$1
    local rows=$2
    curl -X GET --header 'Accept: application/json' 'https://'${base_url}'/v1/admin/devices/fw-updates?serialNumber='${serialNumber}'&size='$rows'&access_token='${env_vc_access_token}
}

trigger_cc_update(){
    local serialNumber=$1 # i.e. M045C06110CE6
    local dest_fw_ver=$2 # i.e. 1.2.48
    local timeout_base_config_cc_update_sec=$3

    ## parse info
    target_device_uuid=$(vc_get_device_info $serialNumber | jq '.uuid?' | sed -e "s#\"##g" )
    [[ null = ${target_device_uuid} ]] && return 1;
    target_fw_uuid=$(vc_get_fw_info $dest_fw_ver | jq '.uuid?' | sed -e "s#\"##g")
    [[ null = ${target_fw_uuid} ]] && return 2;
    target_fw_fwUrl=$(vc_get_fw_info $dest_fw_ver | jq '.fwUrl?' | sed -e "s#\"##g")
    [[ null = ${target_fw_fwUrl} ]] && return 3;

    ## register the device to cam redirector
    qa_cr_set_device "${serialNumber}" "${dest_fw_ver}" "${target_fw_fwUrl}"

    ## Reboot to hit at least once to the redirect environment
    ## Otherwise it will raise fw_update.fw_update_process_values_mismatch
    local current_version=$(vc_get_device_details ${serialNumber} | jq '.softwareVersion' | sed -e 's#"##g')
    if [[ null = $current_version ]]; then
        vc_reboot "${serialNumber}" | tee 1>&2 | jq -e '.status == "SUCCESS"' >/dev/null

        ## monitor timeout
        local start=$(date +"%s") # I ignore the clock change in the runner of this script
        local now=$start
        local current_version=$(vc_get_device_details ${serialNumber} | jq '.softwareVersion' | sed -e 's#"##g')
        local monitor_loop_sleep_sec=1.5

        ## monitoring loop
        while [[ $((${now} - ${start})) -lt ${timeout_base_config_cc_update_sec} ]] && [[ null = ${current_version} ]]
        do
            sleep ${monitor_loop_sleep_sec}
            current_version=$(vc_get_device_details ${serialNumber} | jq '.softwareVersion' | sed -e 's#"##g')
            now=$(date +"%s")
        done

        ## monitoring result
        >&2 echo "redirect at once: process time: "$((${now} - ${start}))
        if [[ $((${now} - ${start})) -gt ${timeout_base_config_cc_update_sec} ]]; then
            cr_delete_device ${serialNumber}
            >&2 echo "redirect at once: error, timeout"
            return 4
        fi
    fi

    ## trigger update
    vc_trigger_fw_update ${target_device_uuid} ${target_fw_uuid} | tee 1>&2 | jq -e '.status == "SUCCESS"' > /dev/null
    [[ $? -ne 0 ]] && { >&2 echo "error in triggering update"; cr_delete_device "${serialNumber}" &>/dev/null ; return 5 ;}

    ## reboot may not be necessary, but for sure
    vc_reboot "${serialNumber}" | tee 1>&2 | jq -e '.status == "SUCCESS"' >/dev/null
    [[ $? -ne 0 ]] && { >&2 echo "error in rebooting"; cr_delete_device "${serialNumber}" &>/dev/null ; return 5 ;}

    ## monitor timeout
    local start=$(date +"%s") # I ignore the clock change in the runner of this script
    local now=$start
    local current_version=$(vc_get_device_details ${serialNumber} | jq '.softwareVersion' | sed -e 's#"##g')
    local monitor_loop_sleep_sec=1.5

    ## monitoring loop
    while [[ $((${now} - ${start})) -lt ${timeout_base_config_cc_update_sec} ]] && [[ ${dest_fw_ver} != ${current_version} ]]
    do
        sleep ${monitor_loop_sleep_sec}
        current_version=$(vc_get_device_details ${serialNumber} | jq '.softwareVersion' | sed -e 's#"##g')
        now=$(date +"%s")
    done

    ## monitoring result
    >&2 echo "base_config_cc_update: process time: "$((${now} - ${start}))
    cr_delete_device ${serialNumber}
    if [[ ${dest_fw_ver} == ${current_version} ]]; then
        return 0;
    else
        >&2 echo "error, timeout"
        return 4
    fi
}

qa_trigger_cc_update(){
    trigger_cc_update $1 $2 600
}

qa_trigger_next_signature_cc_update(){
    [[ ${base_url} != api.dir.sf-dev1.com ]] && { >&2 echo "Environment is not developoment, you cannot try this case in other environment."; return 1; }

    local serialNumber=$1 # i.e. M045C06110CE6
    local dest_fw_ver=$2 # i.e. 1.2.48
    local timeout_base_config_cc_update_sec=300
    local next_signature_ver=${dest_fw_ver}0000002

    qa_trigger_cc_update $serialNumber $next_signature_ver $timeout_base_config_cc_update_sec
}

qa_trigger_wrong_signature_cc_update(){
    [[ ${base_url} != api.dir.sf-dev1.com ]] && { >&2 echo "Environment is not developoment, you cannot try this case in other environment."; return 1; }

    local serialNumber=$1 # i.e. M045C06110CE6
    local dest_fw_ver=$2 # i.e. 1.2.48
    local timeout_base_config_cc_update_sec=300
    local next_signature_ver=${dest_fw_ver}0000001

    qa_trigger_cc_update $serialNumber $next_signature_ver $timeout_base_config_cc_update_sec
}
