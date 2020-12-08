*** Settings ***
Documentation     A test suite with a three test for Verivox
# Library           Selenium2Library    timeout=10
Library           SeleniumLibrary
Resource         ../../keywords/mainkeyword.robot
Variables        ../../variables/${env}.py
Force Tags       practice

*** Variables ***
${BROWSER}    chrome
${SLEEP}      3



# User story
#  AS A          Verivox user
#  I WANT TO     use the DSL calculator and tariff search pages
#  SO THAT       I can select the best available internet tariff for my need

*** Test Cases ***

Scenario 1: Verify the DSL calculator
    [Tags]                                     smoke              DSL
    GIVEN I can open www.verivox.de
   
    WHEN I navigate to the DSL calculator page

    AND I enter 030 for my area code

    AND I select the 100 Mbit/s bandwidth option

    AND I click the Jetzt vergleichen button

    THEN I should see a page that lists the available tariffs for my selection

Scenario 2: Load multiple tariff result pages
    [Tags]                                           smoke            DSL
    GIVEN the same tariff calculation criteria from scenario 1

    WHEN I display the tariff Result List page

    THEN I should see the total number of available tariffs listed in the Ermittelte Tarife section WHEN I scroll to the end of the Result List page

    THEN I should see only the first 20 tariffs displayed

    WHEN I click on the button labeled 20 weitere Tarife laden

    THEN I should see the next 20 tariffs displayed

    AND I can continue to load any additional tariffs until all tariffs have been displayed

Scenario 3: Verify offer details for a selected tariff
    [Tags]                                          smoke                DSL
    GIVEN the same tariff calculation criteria from scenario 1

    AND I display the tariff result list page

    WHEN I click on any Zum Angebot button to select a tariff offer

    THEN I should see the corresponding offer page for the selected tariff
