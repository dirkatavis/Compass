Automation Strategy Outline: Adaptive Web Login for Compass PWA

1. Executive Summary & Goals

Objective: To establish a reliable, high-performance, and resilient end-to-end (E2E) automation solution for the Compass PWA login process using Python/Selenium.

Core Challenge: Implementing a dynamic login workflow that correctly handles the initial one-time setup (First Login) versus the standard recurring process (Subsequent Logins) without back-end access. This logic must be state-adaptive based purely on observed UI elements.

Success Metric: 99% reliability of the LoginFlow.login_handler method across all test cycles.

2. Technology Stack & Architecture Alignment

Component

Technology/Standard

Alignment with Compass Automation

Language

Python 3.13

Aligns with Project Overview.

Framework

Selenium WebDriver

Core technology of the project.

Architecture

Page Object Model (POM)

Logic is separated into pages/ and flows/.

Configuration

Centralized config.json

Used for all credentials and application settings.

3. Adaptive Login Strategy (Core Implementation)

3.1. State Detection Mechanism

The LoginFlow.login_handler method is responsible for dynamically detecting the current state post-initial credentials submission. Detection is executed via non-critical WebDriverWait checks.

Detection Method

Rationale

Timeout Setting

Presence of Unique Element (Primary)

Check for an element unique to the "First Login" setup page (e.g., "Accept Terms" button). Failure (TimeoutException) gracefully signals Workflow 2.

5 seconds (CRITICAL). Fast failure ensures speedy execution of Workflow 2.

3.2. Workflow 1: First Login (One-Time Setup)

This path is executed only when the unique setup UI is detected.

Standard Credentials: Enter Username/Password. (This part should already work with the existing code).

Authentication Submission: Click "Login." (This part should already work with the existing code).

NEW DEVELOPMENT SCOPE: Wait for and interact with unique setup UI elements (e.g., set security questions, accept terms, complete profile setup).

Shared Element: Click "Compass Mobile" button.

Shared Element: Enter WWID.

Verification: Verify final redirection to the main application dashboard.

3.3. Workflow 2: Subsequent Login (Recurring)

This path is executed when the SSO flow is required (the majority of test executions).

Standard Credentials: Enter Username/Password. (This part should already work with the existing code).

Authentication Submission: Click "Login." (This part should already work with the existing code).

CRITICAL STEP 1: Handle Microsoft SSO Account Selection:

NEW DEVELOPMENT SCOPE: Wait for the Microsoft Online "Pick an account" page.

NEW DEVELOPMENT SCOPE: Use a robust, text-based XPath locator (based on the user's stable email/ID) via MicrosoftSSOPage.py to select the correct account tile.

Shared Element: Click the "Compass Mobile" button.

Shared Element: Enter the WWID.

Verification: Verify final redirection to the main application dashboard.

4. Framework Architecture and Design

4.1. Page Object Implementation (pages/)

MicrosoftSSOPage.py: Dedicated POM for the Microsoft "Pick an account" screen (CRITICAL STEP 1 of Workflow 2). Must use resilient locators.

FirstLoginSetupPage.py: POM for the unique elements and actions of the one-time setup (Workflow 1).

4.2. Core Logic Flow (flows/)

LoginFlow.py: Contains the central login_handler method which orchestrates the state detection and conditional execution of the two workflows.

5. Data Management Strategy

Centralized Source: All test data (Username, Password, WWID, SSO Email) must be loaded from config/config.json.

Test Account Requirements: Ensure two dedicated, testable accounts are available: one that forces the First Login state (for Workflow 1) and one that is established and immediately enters the Subsequent Login SSO flow (for Workflow 2).

6. Robustness, Error Handling, and Logging

6.1. Resilient Element Location (Strategy)

All locators for external services (SSO) and critical state elements must prioritize stable text, name attributes, or robust XPath/CSS selectors over short, brittle IDs.

6.2. Structured Reporting (Best Practice)

The LoginFlow.login_handler method will utilize the LoginReport class (utils/LoginResult.py) to return a structured outcome, ensuring clean and unambiguous pass/fail status for pytest.

6.3. Logging

INFO: The LoginFlow.py must log an INFO message clearly stating which workflow (SUCCESS_WORKFLOW_1 or SUCCESS_WORKFLOW_2) was ultimately executed.

ERROR: Implement granular try...except blocks within the workflow steps to raise meaningful errors (e.g., FAILURE_SSO_ERROR) rather than generic WebDriverExceptions, allowing for faster debugging.

7. Maintenance and Future-Proofing

Modularity: The compartmentalization of MicrosoftSSOPage.py ensures that changes to the external SSO UI do not affect the internal application Page Objects, minimizing maintenance effort.

Traceability: Clear logging of the detected state and executed workflow path provides a strong audit trail for every test run, aiding in quick diagnosis of intermittent failures.