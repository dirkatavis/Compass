# tests/test_smoke_mva_find_single.py
# tabs, not spaces
import json
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core import driver_manager
from pages.login_page import LoginPage


def _find_wwid_input(driver):
    """Locate the WWID/User field after login."""
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.bp6-input.fleet-operations-pwa__text-input__102pjhm")
        )
    )



# --- Config & test data -------------------------------------------------------
CONFIG_PATH = r"C:\temp\Python\config\config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

USERNAME = config.get("username")
PASSWORD = config.get("password")
LOGIN_ID = config.get("login_id")

# Use a known-good MVA that should exist
TEST_MVA_FOUND = "51009066"  # change if needed

# If your MVA input selector is different, edit here (we try several fallbacks)
MVA_INPUT_CANDIDATES = [
    (By.CSS_SELECTOR, "input[placeholder*='MVA']"),
    (By.CSS_SELECTOR, "input[aria-label*='MVA']"),
    (By.CSS_SELECTOR, "input[aria-label*='Vehicle']"),
    (By.XPATH, "//input[@type='text' and (contains(@placeholder,'MVA') or contains(@aria-label,'Vehicle'))]"),
]


def _find_mva_input(driver):
    """
    Probe a few likely locators to find the MVA input.
    Edit MVA_INPUT_CANDIDATES above if your app differs.
    """
    for by, sel in MVA_INPUT_CANDIDATES:
        try:
            return WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, sel)))
        except Exception:
            continue
    # As a last resort, try the first visible text input on the page
    try:
        return WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and not(@disabled)]"))
        )
    except Exception:
        raise AssertionError("Could not locate the MVA input. Update MVA_INPUT_CANDIDATES in the test.")


def _enter_mva_and_wait_for_hit(driver, mva: str, timeout: int = 20):
    """
    Types the MVA (8-digit) and waits for a hit tile that echoes the MVA.
    App auto-searches as you type; no submit button.
    Success if we find a div that repeats the MVA value.
    """
    time.sleep(5)  # Small delay to ensure page is ready
    box = _find_mva_input(driver)
    box.clear()
    box.send_keys(mva)

    # Result tile repeats the MVA when found
    elem = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//div[contains(@class,'fleet-operations-pwa__vehicle-property-value')][contains(.,'{mva}')]"
        ))        
    )
    time.sleep(9)  # Allow time for the UI to update
    print(f"[MVA] Verification passed — {mva} echoed in vehicle pane")
    return elem



@pytest.mark.smoke
def test_smoke_mva_find_single():
    # 1) Ensure full pretest context: login + Compass Mobile + WWID
    driver = driver_manager.get_or_create_driver()
    lp = LoginPage(driver)
    lp.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)

    lp.enter_wwid(LOGIN_ID)

    # 2) Enter MVA and expect a FOUND result
    hit = _enter_mva_and_wait_for_hit(driver, TEST_MVA_FOUND)
    assert hit is not None, "Expected to find a matching vehicle tile for the test MVA."

