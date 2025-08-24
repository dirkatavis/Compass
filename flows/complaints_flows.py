import time
from selenium.webdriver.common.by import By
from utils.ui_helpers import click_element_by_text
from selenium.webdriver.common.by import By
from utils.ui_helpers import find_element, find_elements


def handle_existing_complaint(driver, mva: str) -> dict:
    """Select an existing complaint tile and advance."""
    if click_element_by_text(driver, tag="button", text="Next", timeout=8):
        print(f"[COMPLAINT] {mva} — Next clicked after selecting existing complaint")
        return {"status": "ok"}
    else:
        print(f"[WORKITEM][WARN] {mva} — could not advance with existing complaint")
        return {"status": "failed", "reason": "existing_complaint_next"}

def handle_new_complaint(driver, mva: str) -> dict:
    """Create and submit a new PM complaint."""
    if not (click_element_by_text(driver, tag="button", text="Add New Complaint", timeout=10) or
            click_element_by_text(driver, tag="button", text="Create New Complaint", timeout=10)):
        print(f"[WORKITEM][WARN] {mva} — Add/Create New Complaint not found")
        return {"status": "failed", "reason": "new_complaint_entry"}

    print(f"[WORKITEM] {mva} — Adding new complaint")
    time.sleep(2)

    # Drivability → Yes
    print(f"[DRIVABLE] {mva} — answering drivability question: Yes")
    if not click_element_by_text(driver, tag="button", text="Yes", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — Drivable=Yes button not found")
        return {"status": "failed", "reason": "drivable_yes"}
    print(f"[COMPLAINT] {mva} — Drivable=Yes")

    # Complaint Type → PM
    if not click_element_by_text(driver, tag="button", text="PM", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — Complaint type PM not found")
        return {"status": "failed", "reason": "complaint_pm"}
    print(f"[COMPLAINT] {mva} — PM complaint selected")

    # Submit
    if not click_element_by_text(driver, tag="button", text="Submit Complaint", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — Submit Complaint not found")
        return {"status": "failed", "reason": "submit_complaint"}
    print(f"[COMPLAINT] {mva} — Submit Complaint clicked")

    # Next → proceed to Mileage
    if not click_element_by_text(driver, tag="button", text="Next", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — could not advance after new complaint")
        return {"status": "failed", "reason": "new_complaint_next"}
    print(f"[COMPLAINT] {mva} — Next clicked after new complaint")

    return {"status": "ok"}

def handle_complaint(driver, mva: str, found_existing: bool) -> dict:
    """Route complaint handling to existing or new complaint flows."""
    if found_existing:
        return handle_existing_complaint(driver, mva)
    else:
        return handle_new_complaint(driver, mva)

def detect_existing_complaints(driver) -> bool:
    """Return True if any complaint tiles are present in the UI."""
    tiles = driver.find_elements(By.CSS_SELECTOR, "div.fleet-operations-pwa__complaintItem__153vo4c")
    found = len(tiles) > 0
    print(f"[DBG] detect_existing_complaints → {found} (tiles={len(tiles)})")
    return found

def find_dialog(driver):
    locator = (By.CSS_SELECTOR, "div.bp6-dialog, div[class*='dialog']")
    return find_element(driver, locator)

def detect_existing_complaints(driver) -> bool:
    locator = (By.CSS_SELECTOR, "div.fleet-operations-pwa__complaintItem__153vo4c")
    tiles = find_elements(driver, locator)
    found = len(tiles) > 0
    print(f"[DBG] detect_existing_complaints → {found} (tiles={len(tiles)})")
    return found

def find_pm_tiles(driver):
    """Return all 'PM' complaint tiles currently visible."""
    locator = (
        By.XPATH,
        "//button[contains(@class,'damage-option-button')]//h1[normalize-space()='PM']"
    )
    return find_elements(driver, locator, timeout=8)


def find_pm_hard_hold_tiles(driver):
    """Return all 'PM Hard Hold - PM' complaint tiles currently visible."""
    locator = (
        By.XPATH,
        "//button[contains(@class,'damage-option-button')]//h1[normalize-space()='PM Hard Hold - PM']"
    )
    return find_elements(driver, locator, timeout=8)
