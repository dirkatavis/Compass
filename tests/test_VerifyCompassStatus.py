"""
VerifyCompassStatus.py
Purpose: Verify and log Lighthouse status for MVA numbers using Selenium
Based on: test_mva_complaints_tab_fixed.py structure
"""

# ============================================================================
# FILE PATHS - EDIT THESE AS NEEDED
# ============================================================================
MVA_INPUT_FILE = r"C:\Temp\Python\data\mva.csv"              # Input: CSV file with MVA numbers
STATUS_OUTPUT_FILE = r"C:\Temp\Python\logs\CompassStatus.log"  # Output: Status log file
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


def test_verify_compass_status():
    """Main function to verify MVA status and log results"""
    print("Starting VerifyCompassStatus...")
    
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
        
    log.info(f"Processing {len(mvas)} MVAs for status verification...")
    
    # Clear/create output log file
    with open(STATUS_OUTPUT_FILE, 'w') as f:
        f.write("# Compass Status Verification Log\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Loop through MVAs
    for mva in mvas:
        log.info("=" * 60)
        log.info(f">>> Checking status for MVA {mva}")
        log.info("=" * 60)
        
        try:
            status = check_mva_status(driver, mva)
            log_mva_status(mva, status)
            log.info(f"[STATUS] {mva} → {status}")
            
        except Exception as e:
            status = f"ERROR: {str(e)}"
            log_mva_status(mva, status)
            log.error(f"[ERROR] {mva} → {e}")
        
        # Brief pause between MVAs (reduced since we now wait for status to appear)
        time.sleep(0.3 if FAST_MODE else 0.5)
    
    print(f"[COMPLETE] Status verification finished. Results in: {STATUS_OUTPUT_FILE}")
    log.info("All MVA status checks complete")


def check_mva_status(driver, mva):
    """Check the Lighthouse status for a single MVA"""
    
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
        time.sleep(0.5)  # Fallback delay if wait fails
    
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
                    d.find_elements(By.XPATH, "//div[text()='Lighthouse']")
                ])
            )
            log.info(f"MVA {mva} found via alternative detection")
        except TimeoutException:
            log.warning(f"MVA {mva} not found after alternative checks - likely invalid MVA")
            return "MVA_NOT_FOUND"
    
    # Add 5-second delay to ensure UI has fully refreshed with new MVA data
    log.info(f"Adding 5-second delay to allow UI to refresh for MVA {mva}")
    time.sleep(5)
    
    # Wait for Lighthouse status to appear and then extract it
    status = wait_for_lighthouse_status(driver, mva)
    
    return status


def wait_for_lighthouse_status(driver, mva):
    """Wait for Lighthouse status to appear, then extract it"""
    log.info(f"Waiting for Lighthouse status to appear for MVA {mva}...")
    
    # Lighthouse status selectors - same as extract function but for polling
    lighthouse_selectors = [
        "//div[text()='Lighthouse']/following-sibling::div[1]",
        "//div[contains(@class, 'property-name') and text()='Lighthouse']/following-sibling::div[contains(@class, 'property-value')]",
        "//div[contains(@class, 'property-name') and contains(@class, '__') and text()='Lighthouse']/following-sibling::div[contains(@class, 'property-value')]",
        "//*[normalize-space(text())='Lighthouse']/following-sibling::*[1]",
        "//*[text()='Lighthouse']/parent::*//*[contains(@class, 'value')]",
        "//div[text()='Lighthouse']/following-sibling::div[@tabindex]"
    ]
    
    # Poll for status to appear
    try:
        def check_lighthouse_status():
            for selector in lighthouse_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element and element.text.strip():
                        status = element.text.strip()
                        log.info(f"Found Lighthouse status: {status}")
                        return status.upper()
                except Exception:
                    continue
            return None
        
        # Wait up to UI_TIMEOUT seconds for status to appear
        WebDriverWait(driver, UI_TIMEOUT).until(
            lambda d: check_lighthouse_status() is not None
        )
        
        # Extract the final status
        return check_lighthouse_status()
        
    except TimeoutException:
        log.warning(f"Lighthouse status did not appear within {UI_TIMEOUT} seconds for MVA {mva}")
        return "STATUS_NOT_FOUND"


def extract_lighthouse_status(driver):
    """Extract Lighthouse status from the current page (legacy function - now replaced by wait_for_lighthouse_status)"""
    
    try:
        # Method 1: Target Lighthouse using flexible selectors that handle dynamic class names
        lighthouse_selectors = [
            # Look for any div with text "Lighthouse" and get the next sibling div
            "//div[text()='Lighthouse']/following-sibling::div[1]",
            # Look for div containing "Lighthouse" in any property-name class and get value sibling
            "//div[contains(@class, 'property-name') and text()='Lighthouse']/following-sibling::div[contains(@class, 'property-value')]",
            # Handle dynamic class names - look for pattern with property name/value
            "//div[contains(@class, 'property-name') and contains(@class, '__') and text()='Lighthouse']/following-sibling::div[contains(@class, 'property-value')]",
            # More flexible - any element with Lighthouse text, get next element
            "//*[normalize-space(text())='Lighthouse']/following-sibling::*[1]",
            # Look within the same parent container
            "//*[text()='Lighthouse']/parent::*//*[contains(@class, 'value')]",
            # Even more flexible - find Lighthouse and look for sibling with tabindex (like your example)
            "//div[text()='Lighthouse']/following-sibling::div[@tabindex]"
        ]
        
        for selector in lighthouse_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element and element.text.strip():
                    status = element.text.strip()
                    log.info(f"Found Lighthouse status: {status}")
                    return status.upper()
            except Exception as e:
                log.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        # Method 2: Fallback - look for common Lighthouse status values in the page
        lighthouse_keywords = [
            'TIRE DAMAGE', 'TIRE_DAMAGE', 'ACTIVE', 'INACTIVE', 'SUSPENDED', 
            'EXPIRED', 'CLOSED', 'VALID', 'INVALID', 'GOOD', 'BAD', 'FAIL', 'PASS'
        ]
        
        page_text = driver.page_source.upper()
        
        for keyword in lighthouse_keywords:
            if keyword in page_text:
                # Try to find if it's associated with Lighthouse
                if 'LIGHTHOUSE' in page_text and keyword in page_text:
                    log.info(f"Found potential Lighthouse status keyword: {keyword}")
                    return keyword
        
        # Method 3: Debug - capture page structure for troubleshooting
        try:
            # Look for all vehicle property elements to debug
            property_elements = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'vehicle-property') or contains(@class, 'property')]")
            
            log.info(f"Found {len(property_elements)} property elements for debugging")
            for i, element in enumerate(property_elements[:5]):  # Log first 5 for debugging
                try:
                    text = element.text.strip()
                    if 'lighthouse' in text.lower() and len(text) < 100:
                        log.info(f"Debug element {i}: {text}")
                        # If this element contains lighthouse, try to extract the value part
                        if 'lighthouse' in text.lower():
                            parts = text.split('\n')
                            if len(parts) >= 2:
                                return parts[1].strip().upper()  # Second part should be the value
                except:
                    continue
        except:
            pass
            
        return "LIGHTHOUSE_STATUS_NOT_FOUND"
        
    except Exception as e:
        log.warning(f"Error extracting Lighthouse status: {e}")
        return f"EXTRACTION_ERROR: {str(e)}"


def log_mva_status(mva, status):
    """Log MVA and status in the required format"""
    
    log_entry = f"MVA: {mva}: Status: {status}"
    
    # Append to log file
    with open(STATUS_OUTPUT_FILE, 'a') as f:
        f.write(f"{log_entry}\n")
    
    # Also log to console
    print(log_entry)


if __name__ == "__main__":
    try:
        test_verify_compass_status()
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