"""
test_get_vin_from_mva.py
Purpose: Extract VIN numbers for MVA numbers using Selenium
Based on: test_VerifyCompassStatus.py structure
"""

# ============================================================================
# FILE PATHS - EDIT THESE AS NEEDED
# ============================================================================
MVA_INPUT_FILE = r"C:\Temp\Python\data\glass_mva.csv"              # Input: CSV file with MVA numbers
VIN_OUTPUT_FILE = r"C:\Temp\Python\logs\VIN_Results.log"     # Output: VIN log file
# ============================================================================

import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config_loader import get_config
from core import driver_manager
from pages.login_page import LoginPage
from pages.mva_input_page import MVAInputPage
from utils.data_loader import load_mvas
from utils.logger import log
from utils.ui_helpers import navigate_back_to_home, is_mva_known

# Load config values
USERNAME = get_config("username")
PASSWORD = get_config("password")
LOGIN_ID = get_config("login_id")
DELAY = get_config("delay_seconds", default=1.0)  # Increased back to 1 second for stability
FAST_MODE = get_config("fast_mode", default=False)  # Disabled fast mode by default for reliability
MVA_TIMEOUT = get_config("mva_timeout_seconds", default=15)  # Timeout for slow UIs
UI_TIMEOUT = get_config("ui_element_timeout", default=8)  # Consistent timeout for UI elements (5-9 secs)


def test_get_vin_from_mva():
    """Main function to extract VIN numbers for MVAs and log results"""
    print("Starting VIN extraction from MVAs...")
    
    # Initialize driver
    driver = driver_manager.get_or_create_driver()
    log.info(f"Driver initialized: {driver}")
    
    # Perform login
    login_page = LoginPage(driver)
    res = login_page.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)
    if res["status"] != "ok":
        log.error(f"Login failed → {res}")
        return
    
    # Wait for login to complete instead of fixed delay
    try:
        WebDriverWait(driver, UI_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(0.2)  # Minimal settle
    except TimeoutException:
        time.sleep(DELAY)  # Fallback to configurable delay
    
    # Load MVAs from CSV
    mvas = load_mvas(MVA_INPUT_FILE)
    if not mvas:
        log.error("No MVAs found in CSV file")
        return
        
    log.info(f"Processing {len(mvas)} MVAs for VIN extraction...")
    
    # Clear/create output log file
    with open(VIN_OUTPUT_FILE, 'w') as f:
        f.write("# VIN Extraction Log\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Loop through MVAs
    for mva in mvas:
        log.info("=" * 60)
        log.info(f">>> Extracting VIN for MVA {mva}")
        log.info("=" * 60)
        
        try:
            vin = extract_vin_for_mva(driver, mva)
            log_mva_vin(mva, vin)
            log.info(f"[VIN] {mva} → {vin}")
            
        except Exception as e:
            vin = f"ERROR: {str(e)}"
            log_mva_vin(mva, vin)
            log.error(f"[ERROR] {mva} → {e}")
        
        # Brief pause between MVAs
        time.sleep(0.3 if FAST_MODE else 0.5)
    
    print(f"[COMPLETE] VIN extraction finished. Results in: {VIN_OUTPUT_FILE}")
    log.info("All MVA VIN extractions complete")


def extract_vin_for_mva(driver, mva):
    """Extract VIN for a single MVA"""
    
    # Navigate back to home/input page if needed
    navigate_back_to_home(driver)
    time.sleep(0.4 if FAST_MODE else 0.6)  # More conservative navigation timing
    
    # Enter the MVA into the input field
    mva_page = MVAInputPage(driver)
    field = mva_page.find_input()
    if not field:
        return "INPUT_FIELD_NOT_FOUND"
    
    field.clear()
    field.send_keys(mva)
    
    # Wait for page to respond instead of fixed delay
    try:
        WebDriverWait(driver, UI_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(0.2)  # Minimal settle time
    except TimeoutException:
        time.sleep(DELAY)  # Fallback to configurable delay
    
    # Check if MVA is valid/known (with extended timeout for slow UIs)
    log.info(f"Checking if MVA {mva} is known (timeout: {MVA_TIMEOUT}s)...")
    
    # Try once with extended timeout
    if not is_mva_known(driver, mva, timeout=MVA_TIMEOUT):
        log.warning(f"MVA {mva} not found on first attempt, trying alternative detection...")
        
        # Alternative check: look for any vehicle properties or content that indicates success
        try:
            WebDriverWait(driver, UI_TIMEOUT).until(
                lambda d: any([
                    d.find_elements(By.CSS_SELECTOR, "[class*='vehicle-property']"),
                    d.find_elements(By.CSS_SELECTOR, "[class*='properties-container']"),
                    d.find_elements(By.XPATH, "//div[text()='VIN']")
                ])
            )
            log.info(f"MVA {mva} found via alternative detection")
        except TimeoutException:
            log.warning(f"MVA {mva} not found after alternative checks - likely invalid MVA")
            return "MVA_NOT_FOUND"
    
    # Wait for VIN to appear and then extract it
    vin = wait_for_vin_data(driver, mva)
    
    return vin


# Global variable to track the last VIN seen
last_vin_seen = None

def wait_for_vin_data(driver, mva):
    """Wait for VIN data to appear and ensure it's different from the previous VIN"""
    global last_vin_seen
    log.info(f"Waiting for VIN data to appear for MVA {mva}...")
    
    # VIN selectors based on the provided HTML structure
    vin_selectors = [
        # Based on your provided HTML structure
        "//div[text()='VIN']/following-sibling::div[contains(@class, 'vehicle-property-value')]",
        "//div[contains(@class, 'vehicle-property-name') and text()='VIN']/following-sibling::div[contains(@class, 'vehicle-property-value')]",
        # More flexible selectors
        "//div[text()='VIN']/following-sibling::div[1]",
        "//div[normalize-space(text())='VIN']/following-sibling::div[@tabindex]",
        "//*[text()='VIN']/following-sibling::*[1]",
        # Handle dynamic class names
        "//div[contains(@class, 'property-name') and text()='VIN']/following-sibling::div[contains(@class, 'property-value')]",
        # Look within same parent container
        "//*[text()='VIN']/parent::*//*[contains(@class, 'value')]",
    ]
    
    # Poll for VIN to appear
    try:
        def check_vin_data():
            for selector in vin_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element and element.text.strip():
                        vin = element.text.strip()
                        # Basic VIN validation (17 characters, alphanumeric)
                        if len(vin) == 17 and vin.isalnum():
                            return vin
                        else:
                            log.debug(f"Found potential VIN but invalid format: {vin}")
                except Exception:
                    continue
            return None
        
        # Wait up to UI_TIMEOUT seconds for VIN to appear
        WebDriverWait(driver, UI_TIMEOUT).until(
            lambda d: check_vin_data() is not None
        )
        
        # Simple comparison approach: wait for VIN to be different from previous
        previous_vin = last_vin_seen
        current_vin = check_vin_data()
        
        # If this is not the first MVA and VIN is the same, wait a bit and check again
        if previous_vin is not None and current_vin == previous_vin:
            log.info(f"VIN matches previous ({previous_vin}), waiting for UI to refresh...")
            max_attempts = 3
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between attempts
                current_vin = check_vin_data()
                if current_vin != previous_vin:
                    log.info(f"VIN changed from {previous_vin} to {current_vin}")
                    break
                log.warning(f"Attempt {attempt + 1}/{max_attempts}: VIN still matches previous ({previous_vin})")
        
        # Store current VIN for next comparison
        if current_vin:
            log.info(f"Found VIN: {current_vin} for MVA {mva}")
            last_vin_seen = current_vin
        
        return current_vin
        
    except TimeoutException:
        log.warning(f"VIN data did not appear within {UI_TIMEOUT} seconds for MVA {mva}")
        return "VIN_NOT_FOUND"


def log_mva_vin(mva, vin):
    """Log MVA and VIN in the required format: <date/time>Mva: <mva> VIN: <vin>"""
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} Mva: {mva} VIN: {vin}"
    
    # Append to log file
    with open(VIN_OUTPUT_FILE, 'a') as f:
        f.write(f"{log_entry}\n")
    
    # Also log to console
    print(log_entry)


if __name__ == "__main__":
    try:
        test_get_vin_from_mva()
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Script stopped by user")
    except Exception as e:
        print(f"[ERROR] Script failed: {e}")
        log.error(f"Script failed: {e}")
    finally:
        # Cleanup
        try:
            driver_manager.quit_driver()
        except:
            pass