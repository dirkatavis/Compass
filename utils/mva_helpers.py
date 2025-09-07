from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def wait_for_mva_match(driver, mva, timeout=30):
    """Waits for the MVA details to appear on the page, confirming successful lookup."""
    WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, "fleet-operations-pwa__vehicle-property-value__nwt5x3"), mva
        )
    )


def click_add_new_complaint_button(driver, timeout=15):
    """Clicks the 'Add New Complaint' button if visible."""
    try:
        Btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Add New Complaint')]")
            )
        )
        print("Found 'Add New Complaint' button, clicking it...")
        Btn.click()
        print("[DEBUG] Clicked 'Add New Complaint' button.")
    except TimeoutException:
        print("[ERROR] 'Add New Complaint' button not found or not clickable.")
        raise


def select_pm_complaint(driver, timeout=30):
    """Selects the first complaint tile containing 'PM'. Returns True if selected, else False."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "fleet-operations-pwa__complaintItem__153vo4c")
            )
        )
    except TimeoutException:
        print("[DEBUG] No complaint tiles found within timeout.")
        return False

    complaint_tiles = driver.find_elements(
        By.CLASS_NAME, "fleet-operations-pwa__complaintItem__153vo4c"
    )
    for tile in complaint_tiles:
        try:
            content = tile.find_element(
                By.CLASS_NAME, "fleet-operations-pwa__tileContent__153vo4c"
            ).text
            if "PM" in content:
                tile.click()
                log.info(f"Selected complaint with type: {content}")
                return True
        except Exception:
            log.info(f"[DEBUG] Skipped a tile due to error: {e}")

    print("No 'PM' complaint found.")
    return False
