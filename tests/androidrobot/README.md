# Testing steps for the Mob app test automation in real android devices or ios simulator

Description Summary: Objective of the this testing is add more test in the test automaiton and reduce the manual testing effort in different envirnoment

Testing scenario should run in various test conditions depending on camera and client connection configuration.

1. Clone the Git repository for the RobotSuite

    Git clone https://github.com/frogcam/RobotSuite

2. Install Homebrew

    ruby -e “\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)”

3. Install ADB

    brew cask install android-platform-tools

4. Check that ADB is working

    adb devices

5. Install Python3

    brew install python3

6. Install virtualenvwrapper

    pip3 install virtualenvwrapper


8. Add the following to your ~/.bashrc

    WORKON_HOME=~/python-envs

    VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3

    mkdir -p $WORKON_HOME

    source /usr/local/bin/virtualenvwrapper.sh


8. Add source point to bashrc

   source ~/.bashrc

9. Create a virtualenv for robot

    mkvirtualenv robotsuite

10. Install Java

    brew cask install java

11. Add the following to ~/.bashrc

    export JAVA_HOME=$(/usr/libexec/java_home)

    export PATH=$JAVA_HOME/bin:$PATH

12. Install node

    brew install nvm

13. Add the following to ~/.bashrc

    export NVM_DIR=~/.nvm

    mkdir -p $NVM_DIR

    source $(brew --prefix nvm)/nvm

14. Install Appium

    npm install -g appium

# Running the automation Tests

15. Use the virtualenv environment

    workon robotsuite

    robot -d reports/ -T -v Device_id:192.168.1.148:5555 -v platfrom1:8.0.0 -v username:test.user+dev1@smartfrog.com -v password:'Test123!!!' -v camid:M045C06108848 -v wifiusername:qa_cams 

    -v wifipassword:s3a4kjexk6di -v androidenv:Production --exclude=usbwificonnect tests/mobileapp-android/Android_mobile_app.robot

## To Run in the real Ios device :
comment to find the device udid in ios Device: instruments -s devices

    robot -d reports/ -T  -v Device_id:a5035f4a05f5e13ec62d5b032ba567e4b1ea2d41 -v platfrom1:11.4 -v username:test.user+live100@smartfrog.com -v password:'Test123!!!' -v camid:38839A9AD2F3  

    -v wifiusername:qa_cams -v wifipassword:s3a4kjexk6di -t *connect*  tests/mobileapp-android/ios_mobile_app.robot

## To Run in the android simulator

    robot -d reports/ -T  -v Device_id:emulator-5554 -v platfrom1:8.1.0 -v username:test.user+live100@smartfrog.com -v password:'Test123!!!' -v camid:38839A9AD2F3  -v wifiusername:qa_cams 
    
    -v wifipassword:s3a4kjexk6di -t *connect*  tests/mobileapp-android/Android_mobile_app.robot

## To Run in the android real device

    robot -d reports/ -T  -v Device_id:192.168.1.148:5555 -v platfrom1:8.0.0 -v username:test.user+dev1@smartfrog.com -v password:'Test123!!!' -v camid:M045C06108848  -v wifiusername:XXXX 

    -v wifipassword:XXX  -v androidenv:Production -t 2.* -t 4.*  -t 14.* tests/mobileapp-android/Android_mobile_app.robot
