#!/bin/bash -x
export API_DOMAIN="sf-test1.com"
export API_USER="test.user+dev1@smartfrog.com"
export API_PASSWORD="Test123!!!"
export API_TOKEN=$(curl -X POST \
    --data-urlencode "grant_type=password" \
    --data-urlencode "device=Browser" \
    --data-urlencode "password=${API_PASSWORD}" \
    --data-urlencode "scope=Standard" \
    --data-urlencode "username=${API_USER}" \
    "https://app.${API_DOMAIN}/oauth/token" 2>/dev/null | jq --raw-output ".access_token")
export DEVICE_ID=$(curl -X GET "https://app.${API_DOMAIN}/v1/user/devices?access_token=${API_TOKEN}" 2>/dev/null | \
                    jq --raw-output '.response[] | select(.deviceClass == "IPCam" and .operatingStatus == "Publishing") | .uuid' | head -1)
export CLIP_DURATION=120
export CLIP_END=$(date +%s)
export CLIP_START=$(($CLIP_END-$CLIP_DURATION))
export CLIP_ID="${CLIP_START}:${CLIP_END}"
curl -X POST \
    -H 'content-type: application/json;charset=UTF-8' \
    -d "$(jq -n --arg s "${CLIP_START}000" --arg e "${CLIP_END}000" --arg d "${CLIP_ID}" '{start: $s, end: $e, userDescription: $d, type: "USER_CLIP"}')" \
    "https://app.${API_DOMAIN}/v1/user/devices/${DEVICE_ID}/userClips?access_token=${API_TOKEN}"
export TIME_LIMIT=$(($CLIP_DURATION+5))
while [ -z "${NEW_CLIP}" ] && [ "$TIME_LIMIT" -gt 0 ];
do
    echo "Polling Video Services clip. Seconds left ${TIME_LIMIT}";
    export NEW_CLIP=$(curl -X GET \
        "https://clip-api.k8s.${API_DOMAIN}/v2/user/userClips?devices=${DEVICE_ID}&access_token=${API_TOKEN}" 2>/dev/null | \
        jq --raw-output ".response.items[] | select(.userDescription == \"${CLIP_ID}\")")
    sleep 1;
    TIME_LIMIT=$(($TIME_LIMIT-1));
done

curl -L -o /opt/robotframework/artifact_store/new_clip.mp4 $(echo ${NEW_CLIP} | jq --raw-output .playUrls.https | head -1)
