from selenium.webdriver.common.by import By

from utils.logger import log
from utils.ui_helpers import find_element, find_elements


def find_dialog(driver):
    """Return the main dialog container element."""
    locator = (By.CSS_SELECTOR, "div.bp6-dialog, div[class*='dialog']")
    return find_element(driver, locator)


def dbg_dialog(driver):
    """Debug: print dialog button labels and save screenshot."""
    try:
        dlg = find_dialog(driver)
    except Exception:
        dlg = driver
    btns = dlg.find_elements(
        By.XPATH,
        ".//button//*[self::span or self::div or self::p or self::strong]|.//button",
    )
    labels = [b.text.strip() for b in btns if b.text.strip()]
    log.debug(f" dialog buttons -> {labels[:12]}")
    try:
        driver.save_screenshot("debug_drivable.png")
        print("[DBG] screenshot -> debug_drivable.png")
    except Exception:
        pass


def find_next_buttons(driver):
    """Return all 'Next' buttons currently visible in dialogs."""
    locator = (
        By.XPATH,
        "//button[.//span[normalize-space()='Next'] or normalize-space()='Next']",
    )
    return find_elements(driver, locator, timeout=8)


def _dbg_dialog(driver):
    try:
        dlg = find_dialog(driver)
    except Exception:
        dlg = driver
    btns = dlg.find_elements(
        By.XPATH,
        ".//button//*[self::span or self::div or self::p or self::strong]|.//button",
    )
    labels = [b.text.strip() for b in btns if b.text.strip()]
    log.debug(f" dialog buttons -> {labels[:12]}")
    try:
        driver.save_screenshot("debug_drivable.png")
        print("[DBG] screenshot -> debug_drivable.png")
    except Exception:
        pass
