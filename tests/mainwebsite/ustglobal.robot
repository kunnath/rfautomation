*** Settings ***
Documentation     A test suite with a three test for My Store
# Library           Selenium2Library    timeout=10
Library           SeleniumLibrary
Resource         ../../keywords/mainkeyword.robot
Variables        ../../variables/${env}.py
Force Tags       practice

*** Variables ***
${BROWSER}    chrome
${SLEEP}      3

*** Test Cases ***
Scenario 1 : User Registration
    [Tags]                                     smoke              registration
   Go to the home page.
   Click Sign in button.
   Fill Email address to create an account. 
   Fill all fields with correct data.         mr
   Click Register button.
   Verify User details.
   Verify details on home page after successful login.
   Close all browsers

Scenario 2 : Login Test
    [Tags]                                     smoke             Login
    Go to the home page.
    Click Sign in button.
    Fill Email address in Already registered block.
    Fill Password in Already registered block.
    Click on Sign in button.
    Verify User details.
    Verify details on home page after successful login.
    Close all browsers

Scenario 3 : Checkout
    [Tags]                                     smoke             checkout
   Go to the home page.
   Click Sign in button.
   Fill Email address in Already registered block.
   Fill Password in Already registered block.
   Click on Sign in button.
   Verify User details.
   Verify details on home page after successful login.
   Click Women button in the header.
   Click the product.
   Click on Add to cart.
   Click Proceed to checkout.
   Click Proceed to checkout from Summary.
   Click Proceed to checkout from address.
   Click by Terms of service to agree.
   Click Proceed to checkout from shipping.
   Select the payment method.
   Click on I confirm my order.
   Verify details on final confirmation page.
   Close all browsers