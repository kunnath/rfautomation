*** Settings ***
Documentation    Integration Test for 2019-01 Release for SF-SH72D001
...              Feature: Verbose FLASH update log
...              Feature: Double Signature check in update CC/FLASH image
...              Bugfix: fix a bug where event is suspended only 5 sec, not 5 min
...              This update becomes FLASH update.
Resource         testkeywords.robot
Force Tags       manualstep    

# variables not to be hardcoded
Variables        localtest.secure.yaml

# variables changed by test environment
Variables        localtest.env.yaml

# variables for target components of this test
Variables        localtest.component.yaml

*** Test Cases ***

Login username and password
    [Documentation]       Test case documentation
    ...                   Test case details
    [Tags]                manuals                        
    [Setup]               Collect Environmental Condition       
    [TearDown]            Abnormal Firmware Update Scenario   232                                              
    MT                    Verify the Login username           sreelesh                                                                                                                                        
    MT                    Verify the login password           Test123!!!
    Run Keyword Unless    ${TARGET.CURRENT_FLASH_VERSION} == ${TARGET.RELEASE_FLASH_VERSION}     MT           Verify FLASH Update starts            ${ENV.DEVICE.CONSOLE_HOST}          ${TARGET.CURRENT_FLASH_VERSION}
  