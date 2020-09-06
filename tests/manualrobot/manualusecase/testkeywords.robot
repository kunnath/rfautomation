*** Settings ***
Resource    ../manualsetups.robot

*** Keywords ***

Collect Environmental Condition
    [Documentation]                        Test case
    [Tags]                                 warmup
    ${serial_number} =                     Run Keyword Unless                                                                                                "" != "${ENV.DEVICE.SERIAL_NUMBER}"    MT_IN                          Set Expected Serial Number
    Run Keyword Unless                     "" != "${ENV.DEVICE.SERIAL_NUMBER}"                                                                               Set Suite Variable                     ${ENV.DEVICE.SERIAL_NUMBER}    ${serial_number}
    ${lang} =                              Run Keyword Unless                                                                                                "" != "${ENV.DEVICE.LANG}"             MT_IN                          Set Expected Language
    Run Keyword Unless                     "" != "${ENV.DEVICE.LANG}"                                                                                        Set Suite Variable                     ${ENV.DEVICE.LANG}             ${lang}
    ${network_ssid} =                      Run Keyword Unless                                                                                                "" != "${SECURE.NETWORK.SSID}"         MT_IN                          Set Expected Network SSID
    Run Keyword Unless                     "" != "${SECURE.NETWORK.SSID}"                                                                                    Set Suite Variable                     ${SECURE.NETWORK.SSID}         ${network_ssid}
    ${network_psk} =                       Run Keyword Unless                                                                                                "" != "${SECURE.NETWORK.PSK}"          MT_IN                          Set Expected Network PSK
    Run Keyword Unless                     "" != "${SECURE.NETWORK.PSK}"                                                                                     Set Suite Variable                     ${SECURE.NETWORK.PSK}          ${network_psk}

Abnormal Firmware Update Scenario
    [Documentation]                        Test case
    [Arguments]                            ${console_id}  
    [Tags]                                 update
    MT                                     Reset Device                                                                                                      ${console_id}
    Forcely Update Firmware                ${console_id}    

Forcely Update Firmware
    [Documentation]                        Test case
    [Arguments]                            ${console_id}         
    [Tags]                                 update
    MT                                     Confirm Device mounts MMC                                                                                         ${console_id}
    MT                                     Confirm Rollback Firmware in MMC                                                                                  ${console_id}                         
    Run Keyword Unless                     ${TARGET.CURRENT_FLASH_VERSION} == ${TARGET.RELEASE_FLASH_VERSION}                                                MT                                     Device-local FLASH Update      ${console_id} 