*** Settings ***
Documentation          Android mobile app
Library                AppiumLibrary
Library                Collections
Library                DateTime
Library                BuiltIn
Library                Process
Library                String
Resource               androidkeywords.robot
Force Tags             mobile

*** Variables ***
${Device_name1}        9WV4C19326005968
${Device_name2}       ccdb1958
${Device_id}          10.11.3.235:5555
${Device_name4}       9WV7N18628003453
${Device_name5}       3300587190e43227
${Device_name6}       iPhone X
${appiumserverip}     127.0.0.1
${Appium_server}      http://127.0.0.1:4723/wd/hub
${appActivity}        com.inovotecs.frogcam.startup.StartupActivity
${appPackage}         com.smartfrog.app
#                      com.inovotecs.smartfrog.dev
${appandroid}         ${CURDIR}/../../app/smartfrog-rc-debug.apk
${BUNDLE_ID}          com.facebook.IntegrationApp-testnblog
${platfrom1}          8.1.0
${platfrom2}          4.4.2
${platfrom3}          6.0.1
${platfrom4}          9
${platfrom6}          11.3
${automationName1}    uiautomator2
${automationName2}    appium
${automationName3}    XCUITest
${username}           test.user+dev1@smartfrog.com
${password}           Test123!!!
${wifiusername}       it_cams
${wifipassword}       T2h.eXif5p
${camname}            arobot
${Mdelay}             3s
${code}               DE
${AccNum}             5101 1800 0000 0007
${AccName}            smartfrogauto
${cvv}                737
${email-id}           test.user+dev003@smartfrog.com
${camid}              arobot
${androidenv}         Staging
${port}               5555

# robot -d reports/                                                                                                                   -v Device_id:10.11.3.235:5555 -v username:tech-videoservice+ccv2-test-user-de@smartfrog.com -v password:DCAFCtuvh@yoVCHR8RvZeb0Ut17WCJ -v wifiusername:qa_cams -v wifipassword:s3a4kjexk6di -t *connect* tests/MobApp/Android_mobile_app.robot
# Copy and run below commend to run dev with real device
# robot -d reports/ -v Device_id:10.11.3.235:5555 -v username:test.user+dev1@smartfrog.com -v password:Test123!!! -v wifiusername:qa_cams -v wifipassword:s3a4kjexk6di -t *connect* tests/MobApp/Android_mobile_app.robot
# robot -d reports/ -T  -v Device_id:${Device_id} -v platfrom1:8.0.0 -v username:test.user+dev1@smartfrog.com -v password:'Test123!!!' -v camid:M045C06108848  -v wifiusername:qa_cams -v wifipassword:s3a4kjexk6di -v androidenv:Production --exclude=mobconnect   tests/MobApp/Android_mobile_app.robot
# copy below commend to run Simulator device
#robot -d reports/ -v Device_id:emulator-5554 -v platfrom1:8.1.0 -v username:test.user+dev1@smartfrog.com -v password:'Test123!!!'    -v wifiusername:qa_cams -v wifipassword:s3a4kjexk6di -t *connect* tests/MobApp/Android_mobile_app.robot

*** Test Cases ***

1.find adb device and connect device using same wifi port 5555
    [Tags]                                           usbwificonnect       android
    connect adb device with robotsuite

2.start appium server ip
    [Tags]                                           appiumstart          android
    start appium with no reset                       ${appiumserverip}

3.prepare testing environment before start andorid test
    [Tags]                                           envchange            android
    Choose environment to test                       ${androidenv}

4.Open_smartfrog and connect new smartfrog camera
    [Tags]                                           mobconnect           android
    Open_smartfrog mobapp
    Get Network Connection Status in wifi network
   
5.stop appium server ip
    [Tags]                                           appiumstop           android
    stop appium server