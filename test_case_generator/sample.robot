Here is the Robot Framework test code for the given UI:
```
*** Settings ***
Library           SeleniumLibrary
Library           Collections  # Optional for complex validations

# Variables
${URL}            https://example.com/login
${VALID_USER}     testuser
${VALID_PASS}     Test@123
${INVALID_USER}   wronguser
${INVALID_PASS}   Wrong@123

*** Test Cases ***
Test Login
    [Documentation]    Test login functionality
    [Tags]            Regression  Sanity
    [Setup]           Open Browser    ${URL}    chrome
    [Teardown]        Close Browser
    [Steps]
    # Valid Login Test
Open Login Page
Enter Valid Credentials
Verify Successful Redirect

    # Invalid Login Test
    Attempt Login With Wrong Credentials
    Verify Error Message Appears
    Attempt Login With Both Wrong Credentials
    Verify Error Message Appears

    # Field Validation
    Enter Empty Username
    Enter Empty Password
    Enter Both Empty Fields
    Verify Validation Messages

    # Password Masking
    Verify Password Field Obscures Text

*** Test Suite Setup ***
    Open Browser    ${URL}    chrome
    Close Browser

*** Test Suite Teardown ***
Close Browser

#*** Login Page ***
    Open Login Page
    Login Page Should Be Opened

*** Utility Functions ***
# Valid Login Functionality
    Open Login Page
    Login Page Should Be Opened

    Enter Valid Credentials
    Login to System with valid credentials: ${VALID_USER} and ${VALID_PASS}

    Verify Successful Redirect
    Page Should Contain Link: Welcome, ${VALID_USER}
    Page Should Contain Element: Logout Button

# Invalid Login Functionality
    Attempt Login With Wrong Credentials
    Login attempt failed with wrong username or password.

    Verify Error Message Appears
    Element Should Be Visible: Incorrect Username or Password Error Message

    Attempt Login With Both Wrong Credentials
    Login attempt failed with both wrong username and password.

    Verify Error Message Appears
    Element Should Be Visible: Incorrect Username or Password Error Message

# Field Validation Functionality
    Enter Empty Username
    Username field should be highlighted as required.

    Enter Empty Password
    Password field should be highlighted as required.

    Enter Both Empty Fields
    Username and password fields should be highlighted as required.

    Verify Validation Messages
    Page Should Contain Element: Username is required.
    Page Should Contain Element: Password is required.

# Password Masking Functionality
    Verify Password Field Obscures Text
    Password field should obscure text.

*** Keywords ***
    Open Login Page
    Login to System with valid credentials: ${VALID_USER} and ${VALID_PASS}
    Attempt Login With Wrong Credentials
    Attempt Login With Both Wrong Credentials
    Enter Empty Username
    Enter Empty Password
Enter Both Empty Fields

# Helper Functions for element locator
Get Element By ID
    ${element_id} = Get Element Locator id=${element_id}
    [Arguments]    {id}

Get Element By CSS
    ${class_name} = Get Element Locator css=.class_name
    [Arguments]    {css}

Get Element By XPath
    ${xpath_value} = Get Element Locator xpath=//tagname[@attribute='value']
    [Arguments]    {xpath}

# Helper Functions for page actions
Open Login Page
    Login to System with valid credentials: ${VALID_USER} and ${VALID_PASS}
    Attempt Login With Wrong Credentials
    Attempt Login With Both Wrong Credentials

Enter Valid Credentials
    Input Username: ${VALID_USER}
    Input Password: ${VALID_PASS}
    Click Login Button

Enter Empty Username
    Input Username:
    Click Username Field

Enter Empty Password
    Input Password:
    Click Password Field

Enter Both Empty Fields
    Input Username:
    Input Password:
    Click Username and Password Fields

Verify Successful Redirect
    Page Should Contain Link: Welcome, ${VALID_USER}
    Page Should Contain Element: Logout Button

Verify Error Message Appears
    Element Should Be Visible: Incorrect Username or Password Error Message

Verify Password Field Obscures Text
    Password field should obscure text.
```
Please note that the above code is a sample and may need to be modified based on your actual UI structure