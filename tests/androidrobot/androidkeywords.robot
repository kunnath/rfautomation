*** Settings ***
Documentation    WebApp test
Library          AppiumLibrary
Library          Collections
Library          DateTime
Library          BuiltIn
Library          String
Library          Process
Library          OperatingSystem


*** Keywords ***

connect adb device with robotsuite
    ${result}=                                                Run Process                                                                                                           ${CURDIR}/adbautoconnect.sh	${port}
    Log To Console                                            ${result} connected device id is ${Device_id}

start appium with no reset
    [Arguments]                                               ${appiumserverip}
    ${frt}=                                                   Start Process                                                                                                         ${CURDIR}/appiumstart.sh                                                                                           ${appiumserverip}
    Sleep                                                     10s
    Log To Console                                            [${frt}]

stop appium server
     ${handle}=                                               Start Process                                                                                                         ${CURDIR}/appiumstop.sh | command2.sh                                                                              shell=True                                                                                                         cwd=/Users
    Log To Console                                            ${result}

Choose environment to test
    [Arguments]                                               ${androidenv}
    Open Application                                          ${Appium_server}                                                                                                      deviceName=${Device_id}                                                                                            platformName=Android                                                                                               platformVersion=${platfrom1}    app=${appandroid}    automationName=${automationName2}    appActivity=${appActivity}    appPackage=${appPackage}
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/logo_animated')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/logo_animated')]
    Sleep                                                     5s
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.TextView[contains(@text,'Environment')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Click Element                                                                                                      xpath=//android.widget.TextView[contains(@text,'Environment')]
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot
    Click Element                                             xpath=//android.widget.CheckedTextView[contains(@text,'${androidenv}')]
    Sleep                                                     5s
    Close Application
    
Open_smartfrog mobapp
     Open Application                                          ${Appium_server}                                                                                                      deviceName=${Device_id}                                                                                            platformName=Android                                                                                               platformVersion=${platfrom1}    app=${appandroid}    automationName=${automationName2}    appActivity=${appActivity}    appPackage=${appPackage}
     Sleep                                                     10s

Input Credentials
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.ImageView[contains(@resource-id,'android:id/up')]   
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Click signout to start begin test
    Sleep                                                     5s
    Input Username and password                               ${username}                                                                                                           ${password}
    Submit Credentials

Get Network Connection Status in wifi network
    ${Attribute}                                              Get Network Connection Status
    log                                                       ${Attribute}

Smartfrog Camera overview and record
    Click on preview
    Allow record audio
    Sleep                                                     5s
    # Start recording
    Click on event back                                       ${camid}

Input Username and password
    [Arguments]                                               ${username}                                                                                                           ${password}
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Log in')]                                                               100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Log in')]
    Sleep                                                     5s
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@text,'Email')]                                                              ${username}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/password_text')]                          ${password}
    # Sleep                                                     5s

Input Username and password in iOS
    [Arguments]                                               ${username}                                                                                                           ${password}
    AppiumLibrary.Wait Until Page Contains Element            xpath=//[contains(@label=’Log in’)]                                                                                   100s
    AppiumLibrary.Click Element                               xpath=//[contains(@label=’Log in’)]
    Sleep                                                     5s
    AppiumLibrary.Input Text                                  xpath=//(@Value,'Email')]                                                                                             ${username}
    AppiumLibrary.Input Text                                  xpath=//(@Value,'Password')]                                                                                          ${password}
    Sleep                                                     5s

Submit Credentials
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Log in')]                                                               100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Log in')]
    Sleep                                                     10s
    # AppiumLibrary.Capture Page Screenshot
 
Verify the smartfrog home
    :FOR  ${i}  IN RANGE  9999
    \    ${home}=                                             AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'Camera Overview')]
    \    ${menu}=                                             AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.ListView[contains(@resource-id,'com.smartfrog.app:id/menu_list')]
    \    Exit For Loop If                                     '${home}' == '1' or '${menu}' == '1'
    \    Log                                                  ${i}

Click on Connect further Smartfrog Cam
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.Button)[2]                                                                                    20s
    AppiumLibrary.Click Element                               xpath=(//android.widget.Button)[2]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Click to the camera overview menu
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Camera overview')]                                                    20s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Camera overview')]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Verify the camera Overview
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'Camera Overview')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Click to the camera Overview

Click to the camera Overview
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Camera Overview')]                                                      40s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Camera Overview')]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Click on preview
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Preview')]                                                            30s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Preview')]
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot

Click on extended video storage
    [Arguments]                                               ${camid}
    Sleep                                                     10s
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'${camid}')]                                                           20s
    Click Element                                             xpath=//android.widget.TextView[contains(@text,'${camid}')]

Click on stop preview
    AppiumLibrary.Wait Until Page Contains Element            xpath=//ImageButton[contains(@resource-id,'com.inovotecs.smartfrog.dev:id/device_cell_record_button')]                20s
    AppiumLibrary.Click Element                               xpath=//ImageButton[contains(@resource-id,'com.inovotecs.smartfrog.dev:id/device_cell_record_button')]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Click on start preview
    AppiumLibrary.Wait Until Page Contains Element            xpath=//ImageButton[contains(@resource-id,'com.inovotecs.smartfrog.dev:id/device_cell_record_button')]                20s
    AppiumLibrary.Click Element                               xpath=//ImageButton[contains(@resource-id,'com.inovotecs.smartfrog.dev:id/device_cell_record_button')]
    Sleep                                                     3s

Start recording
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'Yes')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.Button[contains(@text,'Yes')]
    Sleep                                                     3s

Allow record audio
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'ALLOW')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.Button[contains(@text,'ALLOW')]
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'Yes')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.Button[contains(@text,'Yes')]
    # Sleep                                                     200s
    # AppiumLibrary.Capture Page Screenshot

Verify main menu to click
    Sleep                                                     5s
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.ListView[contains(@resource-id,'com.smartfrog.app:id/menu_list')]
    Run Keyword If                                            '${elm_present}' != '1'                                                                                               Click main menu

Click main menu
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageView[contains(@resource-id,'android:id/up')]                                              20s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageView[contains(@resource-id,'android:id/up')]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Click on Settings to change motion
    Sleep            1s
    AppiumLibrary.Click Element                               xpath=(//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/device_cell_settings_button')])[1]
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Motion detection')]                                        50s
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Motion detection')]
    Sleep                                                     30s
    AppiumLibrary.Capture Page Screenshot
    Click main menu

Click on connect another Smartfrog Cam
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Connect another Smartfrog Cam')]                                      20s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Connect another Smartfrog Cam')]
    Sleep                                                     3s
    AppiumLibrary.Capture Page Screenshot

Click on alert
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/alert_button')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/alert_button')]

Click on allow alert
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@resource-id,'com.android.packageinstaller:id/permission_allow_button')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               AppiumLibrary.Click Element                                                                                        xpath=//android.widget.Button[contains(@resource-id,'com.android.packageinstaller:id/permission_allow_button')]

Click on Continue
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Continue')]                                                             100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Continue')]
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot

Enter the wifi data
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_ssid')]                             30s
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_ssid')]                             ${wifiusername}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@text,'Password')]                                                           ${wifiPassword}
    Click on Continue
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@text,'Still continue')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Click on Still continue
    Sleep                                                     20s
    AppiumLibrary.Capture Page Screenshot

Click on Still continue
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Still continue')]

Verify wifi connect status
    :FOR  ${i}  IN RANGE  999999
    \    ${error}=                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.TextView[contains(@text,'Connection error')]
    \    ${sucess}=                                           AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_display_name')]
    \    Exit For Loop If                                     '${error}' == '1' or '${sucess}' == '1'
    \    Log                                                  ${i}
    AppiumLibrary.Capture Page Screenshot
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.TextView[contains(@text,'Connection error')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Click on close in error

Click on wifi network continue
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/negativeButton')]
    Sleep                                                     100s

Click on close in error
    Sleep                                                     5s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/action_close')]
    Sleep                                                     5s
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/positiveButton')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Abort camera setup

Abort camera setup
    Sleep                                                     5s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/positiveButton')]

wait for barcode
    AppiumLibrary.Wait Until Page Does Not Contain Element    xpath=//android.widget.TextView[contains(@text,'Connecting to Wi-Fi')]                                                300s
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot

Verify the camaraname
    ${error}=                                                 AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.TextView[contains(@text,'Connection error')]
    Run Keyword If                                            '${error}' == '1'                                                                                                     Test execution failed
    AppiumLibrary.Capture Page Screenshot
    ${elm_present}                                            AppiumLibrary.Get Matching Xpath Count                                                                                xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_display_name')]
    Run Keyword If                                            '${elm_present}' == '1'                                                                                               Enter the camera name

Enter the camera name
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_display_name')]                     100s
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'com.smartfrog.app:id/input_display_name')]                     ${camname}
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Camera overview')]
    AppiumLibrary.Capture Page Screenshot

Click on Shop
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Shop')]                                                               100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Shop')]
    AppiumLibrary.Capture Page Screenshot

Click on upgrade options
    Sleep                                                     10s
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.Button)[2]                                                                                    100s
    AppiumLibrary.Click Element                               xpath=(//android.widget.Button)[2]
    AppiumLibrary.Capture Page Screenshot
    Sleep                                                     5s

Click on the procced to Checkout
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.EditText)[1]
    AppiumLibrary.Input Text                                  xpath=(//android.widget.EditText)[1]                                                                                  1
    AppiumLibrary.Click Element                               xpath=(//android.widget.Image)[1]
    Swipe Up                                                  xpath=(//android.widget.Image)[1]
    Repeat Keyword                                            1 times                                                                                                               Swipe Up                                                                                                           xpath=(//android.widget.Button)[2]
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.Button)[5]                                                                                    200s
    AppiumLibrary.Click Element                               xpath=(//android.widget.Button)[5]
    Sleep                                                     5s

Click on next
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.EditText)[1]                                                                                  500s
    Swipe Up                                                  xpath=//android.widget.Spinner
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Weiter')]                                                               100s
    AppiumLibrary.Click Element                               xpath=(//android.widget.Button)[5]
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot

Click on Buy now in Check page
    AppiumLibrary.Wait Until Page Contains Element            xpath=(//android.widget.Button)[1]                                                                                    500s
    Swipe Up                                                  xpath=(//android.widget.Button)[2]
    AppiumLibrary.Capture Page Screenshot
    Swipe Up                                                  xpath=(//android.view.View)[1]
    Swipe Up                                                  xpath=(//android.view.View)[2]
    Sleep                                                     3s
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    Sleep                                                     4s
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click A Point                               344                                                                                                                   1312                                                                                                               100
    AppiumLibrary.Tap                                         xpath=//FrameLayout[1]/ViewGroup[1]/FrameLayout[2]/RelativeLayout[1]//View//CheckBox[0]
    AppiumLibrary.Click A Point                               75                                                                                                                    602                                                                                                                100
    Repeat Keyword                                            1 times                                                                                                               Click A Point                                                                                                      75                                                                                                                 615
    Swipe                                                     500                                                                                                                   500                                                                                                                500                                                                                                                0                               500
    Sleep                                                     3s
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@resource-id,'buy-now')]                                                       100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'buy-now')]

Get Order number
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.view.View[contains(@resource-id,'order-number')]                                                      100s
    ${ordernumber}                                            AppiumLibrary.Get text                                                                                                xpath=//android.view.View[contains(@resource-id,'order-number')]
    Log                                                       ${ordernumber}
    AppiumLibrary.Capture Page Screenshot

Click Alert and Events
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Alerts and Events')]                                                  100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Alerts and Events')]

Click on filter
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/action_filter_camera_activities')]          100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/action_filter_camera_activities')]
    Sleep                                                     15s
camera event enable
    [Arguments]                                               ${camid}
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'${camid}')]                                                           100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'${camid}')]
    AppiumLibrary.Capture Page Screenshot

Click on Apply
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/filter_ok_button')]                         100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/filter_ok_button')]
    AppiumLibrary.Capture Page Screenshot

Click on event preview
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/event_cell_preview_image')]              100s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/event_cell_preview_image')]
    AppiumLibrary.Capture Page Screenshot

Click on event back
    [Arguments]                                               ${camid}
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'${camid}')]                                                           100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'${camid}')]
    AppiumLibrary.Capture Page Screenshot

Click on Saved Clips
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'Saved Clips')]                                                        100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Saved Clips')]
    AppiumLibrary.Capture Page Screenshot

Click on Saved Clip review
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/clip_cell_preview_image')]               100s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageView[contains(@resource-id,'com.smartfrog.app:id/clip_cell_preview_image')]
    AppiumLibrary.Capture Page Screenshot

Click on Saved Clip back
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageView[contains(@resource-id,'android:id/up')]                                              100s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageView[contains(@resource-id,'android:id/up')]
    AppiumLibrary.Capture Page Screenshot

Swipe Up
    [Arguments]                                               ${locator}
    ${element_size}=                                          Get Element Size                                                                                                      ${locator}
    ${element_location}=                                      Get Element Location                                                                                                  ${locator}
    ${start_x}=                                               Evaluate                                                                                                              ${element_location['x']} + (${element_size['width']} * 0.5)
    ${start_y}=                                               Evaluate                                                                                                              ${element_location['y']} + (${element_size['height']} * 0.7)
    ${end_x}=                                                 Evaluate                                                                                                              ${element_location['x']} + (${element_size['width']} * 0.5)
    ${end_y}=                                                 Evaluate                                                                                                              ${element_location['y']} + (${element_size['height']} * 0.3)
    Swipe                                                     ${start_x}                                                                                                            ${start_y}                                                                                                         ${end_x}                                                                                                           ${end_y}                        500
    Sleep                                                     1

Select payment type
    AppiumLibrary.Click Element                               xpath=//android.widget.RadioButton[contains(@text,'Kreditkarte')]

Enter the card details
    Swipe Up                                                  xpath=//android.widget.EditText[contains(@resource-id,'card.cardNumber')]
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'card.cardNumber')]                                             ${AccNum}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'card.cardHolderName')]                                         ${AccName}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@resource-id,'card.cvcCode')]                                                ${cvv}

Click on smartphone as camera
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Use this smartphone as camera')]
    Allow record audio

Verify the light
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_flash')]                   100s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_flash')]
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_flash')]

Verify the camera
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_switch_cam')]              100s
    Sleep                                                     20s
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_switch_cam')]
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click Element                               xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_switch_cam')]

Verify the record
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.ImageButton[contains(@resource-id,'com.smartfrog.app:id/recorder_ib_record')]                  100s
    AppiumLibrary.Capture Page Screenshot
    Sleep                                                     10s

Click on start low power mode
    Sleep                                                     5s
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Start low power mode')]                                                 100s
    AppiumLibrary.Capture Page Screenshot

Click on user Account page
    Sleep                                                     5s
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TextView[contains(@text,'User Account')]                                                       100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'User Account')]

Click on Signoff and wait for login
    Sleep                                                     5s
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Sign off')]                                                             100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Sign off')]
    Sleep                                                     5s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Yes')]
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Log in')]                                                               100s
    AppiumLibrary.Capture Page Screenshot

Click on sign up now
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Sign up now')]                                                          100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Sign up now')]
    AppiumLibrary.Capture Page Screenshot

Enter the email and password
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.EditText[contains(@text,'Email')]
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@text,'Email')]                                                              ${email-id}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@text,'Confirm Email')]                                                      ${email-id}
    AppiumLibrary.Input Text                                  xpath=//android.widget.EditText[contains(@text,'Password')]                                                           ${password}
    AppiumLibrary.Capture Page Screenshot

Enter the country
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Country')]
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click Element                               xpath=//android.widget.TextView[contains(@text,'Germany')]

Click on Sign up for free
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Sign up for Free')]

Close smartfrog shop
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@resource-id,'com.smartfrog.app:id/action_close')]
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.Button[contains(@text,'Yes')]                                                                  100s
    AppiumLibrary.Click Element                               xpath=//android.widget.Button[contains(@text,'Yes')]
    AppiumLibrary.Capture Page Screenshot

Click on Privacy Policy
    AppiumLibrary.Click Element                               xpath=//android.widget.TableRow[contains(@resource-id,'com.smartfrog.app:id/privacy_policy_row')]
    Sleep                                                     10s
    AppiumLibrary.Capture Page Screenshot
    AppiumLibrary.Click Element                               xpath=//android.widget.LinearLayout

Click on Terms of Service
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TableRow[contains(@resource-id,'com.smartfrog.app:id/terms_service_row')]                      100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TableRow[contains(@resource-id,'com.smartfrog.app:id/terms_service_row')]
    AppiumLibrary.Capture Page Screenshot
    Sleep                                                     3s
    AppiumLibrary.Click Element                               xpath=//android.widget.LinearLayout

Click on Open Source
    AppiumLibrary.Wait Until Page Contains Element            xpath=//android.widget.TableRow[contains(@resource-id,'com.smartfrog.app:id/open_source_row')]                        100s
    AppiumLibrary.Click Element                               xpath=//android.widget.TableRow[contains(@resource-id,'com.smartfrog.app:id/open_source_row')]
    AppiumLibrary.Capture Page Screenshot
    Sleep                                                     3s
    AppiumLibrary.Click Element                               xpath=//android.widget.LinearLayout

Click on About Smartfrog menu
    Sleep                                                     5s
    AppiumLibrary.Click Element                               xpath=(//android.widget.LinearLayout)[20]
    Sleep                                                     5s
    AppiumLibrary.Capture Page Screenshot
    Sleep                                                     5s

Test execution failed
    Log                                                       "wifi connection failed or camera is not connected sucessfully"                                                       console=Failed

Test execution passed
    Log                                                       "camera connected sucessfully"                                                                                        console=Passed

Click signout to start begin test
    Click main menu
    Click on user Account page
    Click on Signoff and wait for login