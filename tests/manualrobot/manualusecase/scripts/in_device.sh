#
# How to use it
# - Create a microSD with its first partition is in vfat 32 format
# - Put this script in the partition (call it as <the script path in microSD>)
# - Insert the microSD to the Camera
# - Load it via "source /hdd00/p01/<the script path in microSD>"
# - Try "get_serial_numbre" and confirm
#   - "$?" shows 0, which means previous command succeeded
#   - it shows the serial number
#
# How to interpret the result
# - all the command shows its result via $? and 0 is success.
# - get_XXXX shows values to standard output
#
get_serial_number(){
    macaddr_file=/config/devicemac
    [ -r "${macaddr_file}" ] \
        && echo M$(head -c 6 "${macaddr_file}" | hexdump -v -e '/1 "%02X"') \
            || return 1
}

verify_serial_number(){
    _serial_number="$1"
    macaddr_file=/config/devicemac
    [ -r "${macaddr_file}" ] \
        && [ "${_serial_number}" = M$(head -c 6 "${macaddr_file}" | hexdump -v -e '/1 "%02X"') ]
}

verify_cc_version(){
    cc_file=/app/smartfrog/smartfrog
    query=$(echo "$1" | sed -e "s#\.#\\\.#g")
    [ -r "${cc_file}" ] \
        && strings "${cc_file}" | grep "${query}" > /dev/null
    res=$?
    export __cached_cc_version="$1"
    return $res
}

get_flash_version(){
    flash_version_file=/flashapp/global_ver
    cat ${flash_version_file}
}

verify_flash_version(){
    _expected_flash_version="$1"
    flash_version=$(get_flash_version)
    [[ ${flash_version} = ${_expected_flash_version} ]]
}

verify_firmware_version(){
    _expected_cc_version="$1"
    _expected_flash_version="$2"
    verify_cc_version "${_expected_cc_version}"
    res_cc=$?
    verify_flash_version "${_expected_flash_version}"
    res_flash=$?
    [[ ${res_cc} -eq 0 && ${res_flash} -eq 0 ]]
}

get_language(){
    lang_file=/flashapp/voice/lang
    cat ${lang_file}
}

verify_language(){
    lang_file=/flashapp/voice/lang
    _lang="$1"
    [ -r "${lang_file}" ] \
        && [ "${_lang}" = $(cat "${lang_file}") ]
}

is_device_setup(){
    config_file=/config/config.dvr
    [ -r "${config_file}" ] \
        && [ 00 -ne $(hexdump -s 0x234 -n 1 -v -e '/1 "%02X\n"' "${config_file}") ]
}

get_device_credential(){
    credential_file=/config/smartfrog.key
    [ -r "${credential_file}" ] \
        && cat "${credential_file}"
}

get_registered_network_ssid(){
    config_file=/config/config.dvr
    offset_ssid=$(printf "%d" 0x234)
    length_ssid=32
    if [ -r "${config_file}" ]; then
        res=$(head -c $((${offset_ssid} + ${length_ssid})) ${config_file} | tail -c ${length_ssid}  | tr -d '\000')
        [[ -z ${res} ]] && return 1 || return 0
    else
        return 1
    fi
}

get_registered_network_psk(){
    config_file=/config/config.dvr
    offset_psk=$(printf "%d" 0x254)
    length_psk=32
    if [ -r "${config_file}" ]; then
        res=$(head -c $((${offset_psk} + ${length_psk})) ${config_file} | tail -c ${length_psk}  | tr -d '\000')
        [[ -z ${res} ]] && return 1 || return 0
    else
        return 1
    fi
}

verify_network_registration(){
    _ssid="$1"
    _psk="$2"
    [[ ${_ssid} = "$(get_registered_network_ssid)" && ${_psk} = "$(get_registered_network_psk)" ]]
}

reset_device(){
    config_file=/config/config.dvr
    if [[ ! -z "$(get_registered_network_ssid)" && ! -z "$(get_registered_network_psk)" ]]; then
        mv ${config_file} ${config_file}.bkup
    fi
    reboot
}

reboot_device(){
    reboot
}

stop_cc(){
    pid=$(ps | grep start-smartfrog.sh | grep -v grep | awk '{printf $1}')
    [[ ! -z ${pid} ]] && kill -9 $pid
    if pgrep smartfrog > /dev/null; then
        kill -9 $(pgrep smartfrog)
    fi
}

stop_vendor_process(){
    app_name=App3518
    app_subprocess_names="wpa_supplicant udhcpc"
    if ! pgrep watchdog > /dev/null; then
        watchdog /dev/watchdog
    fi
    for iProc in ${app_name} ${app_subprocess_names}
    do
        if pgrep $iProc > /dev/null; then
            killall -9 $iProc
        fi
    done
}

confirm_device_mounts_mmc(){
    mmc_path=/hdd00/p01
    mount | grep "${mmc_path}" > /dev/null
}


confirm_rollback_firmware_in_mmc(){
    mmc_path=/hdd00/p01
    _rollback_cc_version="$1"
    _rollback_flash_version="$2"

    firmware_dir=/SF-SH72D001/released

    device_lang=$(get_language)

    expected_cc_file="${mmc_path}${firmware_dir}/smartfrog-${_rollback_cc_version}.tar.xz"
    expected_flash_file="${mmc_path}${firmware_dir}/zmodofw-${_rollback_flash_version}-${device_lang}.tar.xz"
    [[ -f ${expected_cc_file}  && -f ${expected_flash_file} ]]
}

devicelocal_flash_update(){
    mmc_path=/hdd00/p01
    _rollback_flash_version="$1"
    firmware_dir=/SF-SH72D001/released
    device_lang=$(get_language)
    flash_update_script=/SF-SH72D001/update-zmodo.sh
    expected_flash_update_script="${mmc_path}${flash_update_script}"
    expected_flash_file="${mmc_path}${firmware_dir}/zmodofw-${_rollback_flash_version}-${device_lang}.tar.xz"
    if [[ ! -f ${expected_flash_update_script} ]]; then
        echo >&2 "Please prepare udpate script at ${expected_flash_update_script}"
        return 1;
    fi
    ${expected_flash_update_script} ${expected_flash_file} ${_rollback_flash_version} "/config/log/smartfrog.log"
}

devicelocal_cc_update(){
    mmc_path=/hdd00/p01
    _rollback_cc_version="$1"
    firmware_dir=/SF-SH72D001/released
    flash_update_script=/SF-SH72D001/update-zmodo.sh
    expected_cc_file="${mmc_path}${firmware_dir}/smartfrog-${_rollback_cc_version}.tar.xz"

    cc_package_file=/flashapp/smartfrog/smartfrog.tar.xz

    cp "${expected_cc_file}" "${cc_package_file}"
}

verify_start_script_from_old_version(){
    cc_package_file=/flashapp/smartfrog/smartfrog.tar.xz
    start_script_file=/flashapp/app/start-smartfrog.sh
    cc_package_timestamp=$(date -d "$(stat -c "%y" ${cc_package_file} | head -c 19)" +"%s")
    start_script_timestamp=$(date -d "$(stat -c "%y" ${start_script_file} | head -c 19)" +"%s")
    [[ ${cc_package_timestamp} -ge ${start_script_timestamp} ]]
}
