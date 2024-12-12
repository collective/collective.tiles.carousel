# ============================================================================
# EXAMPLE ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s collective.tiles.carousel -t test_example.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src collective.tiles.carousel.testing.COLLECTIVE_TILES_CAROUSEL_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/collective/tiles/carousel/tests/robot/test_example.robot
#
# See the https://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/browser.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: As a member I want to be able to log into the website
  [Documentation]  Example of a BDD-style (Behavior-driven development) test.
  Given a login form
   When I enter valid credentials
   Then I am logged in


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a login form
  Go To  ${PLONE_URL}/login_form
  Get Text    //body    contains    Login Name
  Get Text    //body    contains    Password


# --- WHEN -------------------------------------------------------------------

I enter valid credentials
  Type Text    //input[@name="__ac_name"]    admin
  Type Text    //input[@name="__ac_password"]    secret
  Click    //button[contains(text(), "Log in")]


# --- THEN -------------------------------------------------------------------

I am logged in
  Get Text    //body    contains    You are now logged in
