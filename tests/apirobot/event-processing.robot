*** Settings ***
Library          Process
Library          OperatingSystem
Library          Collections
Library          RequestsLibrary
Library          String
Force Tags       api
Variables        ../../variables/${env}.py

*** Variables ***

${apitest}    ${CURDIR}/scripts/compare-clips.sh -d ${API_DOMAIN}
${path}       ${CURDIR}/scripts

*** Test Cases ***
Event-process and verify the massage response
    [Tags]                         apistreaming                                  clip
    Log                            ${path}
    Log                            ${apitest}
    List Files In Directory        ${path}
    ${rc}                          ${output} =                                Run And Return Rc And Output    ${path}/create-event.sh
    sleep                          5s
    Should Be Equal As Integers    ${rc}                                      0
    log                            ${output}
    Should Contain                 ${output}                                  ${resp}
    log                            ${resp}

new and old video clip validation using api testing
    [Tags]                         apistreaming                                  clip
    ${out}                         ${outputs} =                               Run And Return Rc And Output    ${apitest}
    Sleep                          200s
    Log To Console                 ${out}
    Log To Console                 ${outputs}

Cross validation of mp4 videos
    [Tags]                         apistreaming                                  clip
    ${rc}                          ${outputs} =                               Run And Return Rc And Output    ${path}/cross.sh
    sleep                          120s
    Split String                   string, separator=SSIM Y:, max_split=-1
    ${result} =                    Fetch From Right                           ${outputs}                      SSIM Y:
    @{value} =                     Split String                               ${result}                       ${SPACE}
    Log                            ${outputs}
    Log                            ${result}
    Log                            @{value}[${0}]
    Should Be True                 @{value}[${0}] >= 0.95                     Return code greater than .95
    ${value2} =                    Split String                               @{value}[${2}]                  U:
    Log                            ${value2}[${1}]
    Should Be True                 ${value2}[${1}] >= 0.95                    Return code greater than .95
    ${value4} =                    Split String                               @{value}[${4}]                  V:
    Log                            ${value4}[${1}]
    Should Be True                 ${value4}[${1}] >= 0.95                    Return code greater than .95

