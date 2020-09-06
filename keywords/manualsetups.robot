*** Settings ***
Documentation
Library    BuiltIn
Library    Dialogs

*** Keywords ***
MT
    [Arguments]        ${test_name}            @{test_arg}
    Run Keyword If     ${ENV.IS_MANUAL}        Execute Manual Step    Manual Test: ${test_name} < args: @{test_arg} >
    Run Keyword If     not ${ENV.IS_MANUAL}    ${test_name}           @{test_arg}

# @warning you cannot use this for the function which returns multiple-values
MT_IN
    [Arguments]        ${test_name}            @{test_arg}
    ${user_input} =    Run Keyword If          ${ENV.IS_MANUAL}       Get Value From User                                Manual Test: ${test_name} < args: @{test_arg} >
    Run Keyword If     not ${ENV.IS_MANUAL}    ${test_name}           @{test_arg}
    [Return]           ${user_input}
