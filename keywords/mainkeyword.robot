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
Go to the home page.
     Open Browser    ${url}    ${BROWSER}
     Maximize Browser Window
     Capture Page Screenshot
    
Click Sign in button.
     Click Link    xpath=//a[@title="Log in to your customer account"]
     Capture Page Screenshot

Fill Email address in Already registered block.
    Input Text    xpath=//input[@name="email"]     ${username}
    Capture Page Screenshot   

Fill Password in Already registered block.
    Input Text    xpath=//input[@name="passwd"]    ${password}
    Capture Page Screenshot

Click on Sign in button.
    Click Element    xpath=//p[@class='submit']//span[1]
    Capture Page Screenshot

Verify User details.
    Page Should Not Contain Element   xpath=//li[contains(text(),'Authentication failed.')]
    Capture Page Screenshot

Verify details on home page after successful login.
    Page Should Contain Element     xpath=//span[contains(text(),'${firstname} ${lastname}')]
    Capture Page Screenshot

Fill Email address to create an account.
    Input Text    xpath=//input[@name="email_create"]     ${username}
    Click Button   xpath=//button[@id='SubmitCreate']
    Sleep           5s
    Capture Page Screenshot

Fill all fields with correct data.
    [Arguments]                         ${mrmrs}
    Click Element   xpath=//label[@for="id_gender${${mrmrs}}"]
    Input Text    xpath=//input[@name="customer_firstname"]     ${firstname}
    Input Text    xpath=//input[@name="customer_lastname"]      ${lastname}
    Input Text    xpath=//input[@name="email"]                  ${username}
    Input Text    xpath=//input[@name="passwd"]                 ${password}
    Select From List By Value    xpath=//select[@name="days"]     ${day}
    Select From List By Value    xpath=//select[@name="months"]   ${month}
    Select From List By Value    xpath=//select[@name="years"]    ${year}
    Input Text    xpath=//input[@name="address1"]        ${address}
    Input Text    xpath=//input[@name="city"]    ${city}
    Select From List By Label   xpath=//select[@name="id_state"]       ${state}
    Input Text    xpath=//input[@name="postcode"]     ${postcode}
    Input Text    xpath=//textarea[@name="other"]     ${other}
    Input Text    xpath=//input[@name="phone"]     ${phone}
    Input Text    xpath=//input[@name="phone_mobile"]     ${phone_mobile}
    Click Element    xpath=//div[@class="columns-container"]  
    Input Text    xpath=//input[@name="alias"]     ${alias}
    Capture Page Screenshot

Click Register button.   
    Click Element    xpath=//span[contains(text(),'Register')]
    Wait for pageloading
    Element Should Contain   //a[@class='logout']        Sign out
  
Click Women button in the header.
    Click Link    //a[@title="Women"]
    Capture Page Screenshot

Click the product.
    Execute Javascript    $(document).scrollTop(${x})
    Set Focus To Element  xpath=(//img[@alt=${product_title}])[1]
    Click Image    xpath=(//img[@alt=${product_title}])[1]
    Wait for pageloading
    Capture Page Screenshot

Click on Add to cart.
    Set Focus To Element    xpath=//*[@id="add_to_cart"]
    Click Element    xpath=//*[@id="add_to_cart"]
    Click Element    xpath=//span[contains(text(),'Add to cart')]
    Wait for pageloading
    Capture Page Screenshot

Click Proceed to checkout.
    Click Element    xpath=//span[contains(text(),'Proceed to checkout')]
    Wait for pageloading
    Capture Page Screenshot

Click Proceed to checkout from Summary.
    Execute Javascript    $(document).scrollTop(${x})
    Set Focus To Element   xpath=(//span[contains(text(),'Proceed to checkout')])[2]
    Click Element    xpath=(//a[@title="Proceed to checkout"])[2]
    Wait for pageloading
    Capture Page Screenshot

Click Proceed to checkout from address.
    Execute Javascript    $(document).scrollTop(${x})
    Click Element    xpath=//button[@name="processAddress"]
    Wait for pageloading

Click by Terms of service to agree.
    Select Checkbox    xpath=//input[@id='cgv']
    Capture Page Screenshot

Click Proceed to checkout from shipping.
    Execute Javascript    $(document).scrollTop(${x})
    Click Element    xpath=//button[@name="processCarrier"]
    Wait for pageloading

Select the payment method.
    Click Link    xpath=//a[@title="Pay by bank wire"]
    Wait for pageloading

Click on I confirm my order.
    Click Element   xpath=//span[contains(text(),'I confirm my order')]


Wait for pageloading
    Capture Page Screenshot
    ${elm_present} =                    Get Element Count                                                            xpath=//div[@id='fancybox-loading']//div
    Run Keyword if                      '${elm_present}' >= '1'                                                      Sleep                                                      20s
    Sleep                                15s