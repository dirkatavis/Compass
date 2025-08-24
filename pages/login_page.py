import json
import os
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.ui_helpers import select_location


class LoginPage:
    def __init__(self, driver):
        self.driver = driver

        # Hardcoded config path
        config_path = r"C:\temp\Python\config\config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
            self.delay_seconds = config.get("delay_seconds", 4)

    def ensure_ready(self, username: str, password: str, login_id: str):
        """
        High-level pretest setup:
        1) ensure_logged_in
        2) go_to_mobile_home
        3) ensure_user_context(WWID)
        """
        self.ensure_logged_in(username, password, login_id)
        self.go_to_mobile_home()

        # Wait until WWID input is visible before proceeding
        try:
            WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[class*='fleet-operations-pwa__text-input__']")
                )
            )
            print("[CTX] Compass Mobile ready — WWID field visible.")
        except Exception:
            print("[CTX] WWID field not detected in wait window; proceeding anyway.")

    def enter_wwid(self, login_id: str):
        self.driver.switch_to.window(self.driver.window_handles[-1])

        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )


        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[class*='fleet-operations-pwa__text-input__']")
        if not inputs:
            raise AssertionError("WWID field not present yet. Is Compass Mobile fully loaded?")

        box = None
        for el in inputs:
            try:
                if el.is_displayed() and (el.get_attribute("type") or "").lower() == "text":
                    box = el
                    break
            except Exception:
                continue
        if box is None:
            raise AssertionError("No visible WWID text input found on the Compass Mobile tab.")

        box.clear()
        box.send_keys(str(login_id))
        time.sleep(3)  # Allow time for autocomplete

        submit_btn = self.driver.find_element(
            By.CSS_SELECTOR,
            "button.bp6-button.bp6-intent-success.fleet-operations-pwa__submit-button__1fbse6k"
        )
        submit_btn.click()
        time.sleep(9)  # Allow time for the next page to load
        
        # Now it’s safe to select the location
        from utils.ui_helpers import select_location
        select_location(self.driver, "GA4-A")

    def is_logged_in(self) -> bool:
        locators = [
            (By.XPATH, "//span[contains(text(), 'Compass Mobile')]"),
            (By.XPATH, "//button[contains(., 'Compass Mobile')]"),
        ]
        for by, sel in locators:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((by, sel))
                )
                print("[LOGIN] is_logged_in → True (found Compass Mobile)")
                return True
            except Exception:
                continue
        print("[LOGIN] is_logged_in → False")
        return False

    def ensure_logged_in(self, username: str, password: str, login_id: str):
        if self.is_logged_in():
            print("[LOGIN] Session already authenticated — reusing it.")
            return

        print("[LOGIN] No active session — performing login()...")
        self.login(username, password, login_id)

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'Compass Mobile')]")
                )
            )
            print("[LOGIN] Auth confirmed — session ready.")
        except Exception:
            raise RuntimeError("Login failed — post-login UI was not detected.")

    def go_to_mobile_home(self):
        try:
            elem = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((
                    By.XPATH, "//span[contains(text(),'Compass Mobile')] | //button[contains(.,'Compass Mobile')]"
                ))
            )
            try:
                elem.click()
                print("[CTX] Navigated to Compass Mobile.")
            except Exception:
                print("[CTX] Compass Mobile present; click skipped.")
        except Exception:
            print("[CTX] Compass Mobile control not found; assuming already on mobile home.")

    def login(self, username, password, login_id):
        print("Navigating to the login page...")
        self.driver.get("https://avisbudget.palantirfoundry.com/multipass/login")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Page loaded.")
        time.sleep(self.delay_seconds)

        print("Checking for 'Pick an account' screen...")
        try:
            use_another_account = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Use another account']"))
            )
            print("'Pick an account' screen found. Clicking 'Use another account'...")
            time.sleep(2)
            use_another_account.click()
            time.sleep(2)
        except:
            print("'Pick an account' screen not found. Continuing...")

        print("Waiting for email field...")
        email_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        print(f"Typing email: {username}")
        email_field.send_keys(username)
        time.sleep(1)
        self.driver.find_element(By.ID, "idSIButton9").click()

        print("Waiting for password page...")
        password_field = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.NAME, "passwd"))
        )
        print("Typing password.")
        time.sleep(2)
        #password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        self.driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(3)

        print("Waiting for 'Stay signed in' prompt...")
        try:
            stay_signed_in_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            stay_signed_in_button.click()
            time.sleep(9)
        except:
            print("'Stay signed in' prompt not found.")

        print("Verifying login success...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Compass Mobile')]"))
            )
            print("Login successful — Mobile Compass loaded.")
        except:
            raise Exception("Login failed — Mobile Compass page not detected.")

