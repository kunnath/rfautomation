*** Settings ***
Documentation    keyword to run the main website
Library          SeleniumLibrary
Library          Collections
Library          DateTime
Library          BuiltIn
Library          String
Library          XvfbRobot
Variables        ../variables/${env}.py

*** Keywords ***
GIVEN I can open www.verivox.de
    Log To Console  ${BROWSER} 
    Open chrome browser    
    # Run Keyword If '${BROWSER}'=='firefox'               Open firefox browser    
    # Run Keyword If '${BROWSER}'=='ie'                    Open internet explore browser  

Open chrome browser 
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    ${prefs}    Create Dictionary   credentials_enable_service=${false}  
    Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
    Call Method    ${chrome_options}    add_argument    --disable-infobars 
    Create WebDriver    Chrome    chrome_options=${chrome_options}
    Open Browser    ${url}    ${BROWSER}
    Sleep   5s
    Capture Page Screenshot
    Accept cookies
    
Accept cookies
    Set Focus To Element    xpath=//button[@class="gdpr-button gdpr-accept-all first-layer"]
    ${Result}=     Page Should Contain Element      xpath=//button[@class="gdpr-button gdpr-accept-all first-layer"]
    Run Keyword Unless  '${RESULT}'=='PASS'         Click Element      xpath=//button[@class="gdpr-button gdpr-accept-all first-layer"]

Open firefox browser
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Capture Page Screenshot

Open internet explore browser
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Capture Page Screenshot

WHEN I navigate to the DSL calculator page
    Sleep     3s
    Page Should Contain Element    xpath=//span[@class="mps-label-text" and contains(text(),'DSL')]
    Click Element    xpath=//span[@class="mps-label-text" and contains(text(),'${mps_label}')]
    Wait for calculator
    Capture Page Screenshot

AND I enter 030 for my area code
    Input Text    xpath=//input[@name="phonePrefix"]        ${areacode}
   
AND I select the 100 Mbit/s bandwidth option
    Wait Until Element Is Visible     xpath=//div[@class="calc-toggles toggle-two-lines"]
    Click Element    xpath=//div[@class="calc-toggles toggle-two-lines"]
    Set Focus To Element    xpath=(//div[@class="calc-toggles toggle-two-lines"]/label)[3]
    Click Element    xpath=(//div[@class="calc-toggles toggle-two-lines"]/label)[3]
    Capture Page Screenshot

AND I click the Jetzt vergleichen button
    Click Element    xpath=(//button[@class="page-button" and contains(text(),'Jetzt vergleichen')])[4]
    Sleep    5s
    Capture Page Screenshot

THEN I should see a page that lists the available tariffs for my selection
    Reload Page
    Capture Page Screenshot
    ${count1}=    Get Element Count    xpath=//button[@class="button-secondary w-100 tariff-details-toggle"]     
    Run Keyword If   ${count1} >= 5      Run Keywords     PassedExecution
    ${count2}=    Get Element Count    xpath=//div[@class="d-flex internet-speed internet-speed-download"]//b[contains(text(),'100')]
    Run Keyword If   ${count2} < 5      Run Keywords     FailedExecution         

Scenario 1: Verify the DSL calculator
    GIVEN I can open www.verivox.de
   
    WHEN I navigate to the DSL calculator page

    AND I enter 030 for my area code

    AND I select the 100 Mbit/s bandwidth option

    AND I click the Jetzt vergleichen button

    THEN I should see a page that lists the available tariffs for my selection

GIVEN the same tariff calculation criteria from scenario 1
    GIVEN I can open www.verivox.de
   
    WHEN I navigate to the DSL calculator page

    AND I enter 030 for my area code

    AND I select the 100 Mbit/s bandwidth option

    AND I click the Jetzt vergleichen button

WHEN I display the tariff Result List page
    Page Should Contain Element     xpath=//h1[@class="pt-xl-4 pt-2 pt-xl-0 text-center text-xl-left"]
    ${tarrifcount} =    Get Text    xpath=//h1[@class="pt-xl-4 pt-2 pt-xl-0 text-center text-xl-left"]

THEN I should see the total number of available tariffs listed in the Ermittelte Tarife section WHEN I scroll to the end of the Result List page
    ${tarrifcount} =    Get Text    xpath=//h2[@class="summary-tariff"]
    ${count} =        Get Element Count     xpath=//div[@class="col-sm comparison-rank font-weight-bold ml-md-1"]
    Scroll Page To Location    0    6000
    Capture Page Screenshot


THEN I should see only the first 20 tariffs displayed
    ${pagecount} =    Get Text     xpath=//button[@class="btn btn-primary text-uppercase"]
    ${count} =        Get Element Count     xpath=//div[@class="col-sm comparison-rank font-weight-bold ml-md-1"]
    Run Keyword If   ${count} == 20    Run Keywords        PassedExecution
    Capture Page Screenshot

WHEN I click on the button labeled 20 weitere Tarife laden
    Click Element     xpath=//button[@class="btn btn-primary text-uppercase"]
    Sleep    5s

THEN I should see the next 20 tariffs displayed
    Scroll Page To Location    0    36000
    ${count} =        Get Element Count     xpath=//div[@class="col-sm comparison-rank font-weight-bold ml-md-1"]
    Run Keyword If   ${count} == 40    Run Keywords        PassedExecution
    Capture Page Screenshot

AND I can continue to load any additional tariffs until all tariffs have been displayed
    Click Element     xpath=//button[@class="btn btn-primary text-uppercase"]
    Sleep        5s  
    Scroll Page To Location    0    36000
    ${count} =        Get Element Count     xpath=//div[@class="col-sm comparison-rank font-weight-bold ml-md-1"]
    Page Should Contain Element     xpath=//button[@class="btn btn-primary text-uppercase"]
    Run Keyword If   ${count} == 60    Run Keywords        PassedExecution
    Capture Page Screenshot

AND I display the tariff result list page
    Sleep    3s
    Capture Page Screenshot
    Page Should Contain Element     xpath=//h1[@class="pt-xl-4 pt-2 pt-xl-0 text-center text-xl-left"]

WHEN I click on any Zum Angebot button to select a tariff offer
    Click Element     xpath=(//a[@class="button-primary w-100"])[${tariffid}]
    Capture Page Screenshot

THEN I should see the corresponding offer page for the selected tariff
    Sleep     5s
    Page Should Contain Element     xpath=(//*[@class="centered-content effective-price-wrapper"])[1]
    ${price} =       Get Text   xpath=(//*[@class="centered-content effective-price-wrapper"])[1]
    ${offer} =   Get Text   xpath=//h3[@class="group-header"] 
    ${count} =	Get Count	${price}    	${priceset}     
    Run Keyword If   ${count}==1    Run Keywords     PassedExecution     ELSE   Fail   failed Execution
    ${count} =	Get Count	${offer}    	${offertext}    
    Run Keyword If   ${count}==1    Run Keywords     PassedExecution     ELSE   Fail   failed Execution

Scroll Page To Location
    [Arguments]    ${x_location}    ${y_location}
    Execute JavaScript    window.scrollTo(${x_location},${y_location})


PassedExecution
    Set Suite Variable   ${Executionsstep}      1
    Log                  ${Executionsstep}
    Capture Page Screenshot

FailedExecution
    Set Suite Variable   ${Executionsstep}	     0
    Log                 ${Executionsstep}
    Capture Page Screenshot

Report Execution status
    log                 ${Executionsstep}
    Run Keyword If    ${Executionsstep}!=0  Pass Execution      Test Execution passed   ELSE     Fail     Test Execution failed

Go to the home page.
     Open Browser    ${url}    ${BROWSER}
     Maximize Browser Window
     Capture Page Screenshot

Wait for calculator
    Capture Page Screenshot
    ${elm_present} =                    Get Element Count                                                            xpath=//div[@class="calculator-headline" and contains(text(),'Internet+Telefon')]
    Run Keyword if                      '${elm_present}' >= '1'                                                      Sleep                                                      10s
    Sleep                                5s