****Settings ***
Library      device_token.py
Variables    test_device_token_variables.py
Force Tags      testdatastep

****Test Case ***

Test Wifi Token
    [Tags]                        libraries-unit-test
    FOR                           ${item}                  IN                         @{sample_networks}
    Log                           ${item}
    ${token}=                     Generate Wifi Token      ${item["ssid"]}            ${item["psk"]}
    Should Be Equal As Strings    ${token}                 ${item["token"]}
    END

Test Secure Token
    [Tags]                        libraries-unit-test
    FOR                           ${item}                  IN                         @{sample_url_paths}
    Log                           ${item}
    ${token}=                     Generate Secure Token    ${item["key"]}             ${item["url_path"]}
    Should Be Equal As Strings    ${token}                 ${item["secure_token"]}
    END
