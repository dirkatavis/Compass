"""Flows for creating, processing, and handling Compass Work Items."""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from flows.complaints_flows import associate_existing_complaint
from flows.finalize_flow import finalize_workitem
from utils.logger import log
from utils.ui_helpers import click_element, safe_wait

def get_work_items(driver, mva: str):
    """Collect all open PM work items for the given MVA.
    
    Args:
        driver: Selenium WebDriver instance
        mva: MVA identifier string
        
    Returns:
        list: Collection of WebElements representing open PM work item tiles
    """
    log.info(f"[WORKITEM] {mva} - waiting for Work Items to render...")
    
    try:
        # Wait for at least one matching tile to be present
        base_xpath = "//div[contains(@class,'scan-record-header')]"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, base_xpath))
        )
        
        # Then collect all tiles matching our criteria
        tiles = driver.find_elements(
            By.XPATH,
            base_xpath + 
            " and .//div[contains(@class,'scan-record-header-title')][contains(normalize-space(),'PM')]" +
            " and .//div[contains(@class,'scan-record-header-title-right__')][normalize-space()='Open']"
        )
        
        log.info(f"[WORKITEMS] {mva} - collected {len(tiles)} open PM item(s)")
        for t in tiles:
            log.debug(f"[DBG] {mva} - tile text = {t.text!r}")
        return tiles
        
    except Exception as e:
        log.warning(f"[WORKITEM][WARN] {mva} - could not collect work items -> {e}")
        return []





def create_new_workitem(driver, mva: str):
    """Create a new Work Item for the given MVA."""
    log.info(f"[WORKITEM] {mva} - starting CREATE NEW WORK ITEM workflow")

    # Step 1: Click Add Work Item
    try:
        time.sleep(5)  # wait for button to appear
        if not click_element(driver, (By.XPATH, "//button[normalize-space()='Add Work Item']")):
            log.warning(f"[WORKITEM][WARN] {mva} - add_btn not found")
            return {"status": "failed", "reason": "add_btn", "mva": mva}
        log.info(f"[WORKITEM] {mva} - Add Work Item clicked")
        time.sleep(5)

    except NoSuchElementException:
        log.warning(f"[WORKITEM][WARN] {mva} - add_btn failed -> {e}")
        return {"status": "failed", "reason": "add_btn", "mva": mva}

    # Step 2: Complaint handling
    try:
        res = associate_existing_complaint(driver, mva)
        if res["status"] == "associated":
            log.info(
                "[COMPLAINT][ASSOCIATED] {mva} - existing PM complaint linked to Work Item"
            )
        else:
            log.info(
                "[WORKITEM][SKIP] {mva} - no existing PM complaint, navigating back"
            )
            return {"status": "skipped_no_complaint", "mva": mva}
    except NoSuchElementException as e:
        log.warning(f"[WORKITEM][WARN] {mva} - complaint handling failed -> {e}")
        return {"status": "failed", "reason": "complaint_handling", "mva": mva}

    # Step 3: Finalize Work Item (call will be injected here in refactor later)
    log.warning(f"[WORKITEM][WARN] {mva} - finalize step skipped (refactor placeholder)")
    return {"status": "created", "mva": mva}


def handle_pm_workitems(driver, mva: str) -> dict:
    """
    Handle PM Work Items for a given MVA:
      1. If an open PM Work Item exists, complete it.
      2. Otherwise, start a new Work Item.
         - Try to associate an existing complaint.
         - If none, skip and return control to the test loop.
    """
    log.info(f"[WORKITEM] {mva} — handling PM work items")

    # Step 1: check for open PM Work Items
    items = get_work_items(driver, mva)
    if items:
        log.info(f"[WORKITEM] {mva} - open PM Work Item found, completing it")
        from flows.work_item_flow import complete_pm_workitem
        return complete_pm_workitem(driver, mva)

    # Step 2: no open WI → start a new one
    from selenium.webdriver.common.by import By
    if click_element(driver, (By.XPATH, "//button[normalize-space()='Add Work Item']"),
                     desc="Add Work Item", timeout=8):
        log.info(f"[WORKITEM] {mva} - Add Work Item clicked")

        # Required Action: immediately try to associate existing complaints
        from flows.complaints_flows import associate_existing_complaint
        res = associate_existing_complaint(driver, mva)

        if res.get("status") == "associated":
            from flows.finalize_flow import finalize_workitem
            return finalize_workitem(driver, mva)

        elif res.get("status") == "skipped_no_complaint":
            log.info(f"[WORKITEM] {mva} — navigating back home after skip")
            from utils.ui_helpers import navigate_back_to_home
            navigate_back_to_home(driver)
            return res

        return res

    else:
        log.warning(f"[WORKITEM][WARN] {mva} - could not click Add Work Item")
        return {"status": "failed", "reason": "add_btn", "mva": mva}







def process_workitem(driver, mva: str):
    """Main entry point for processing a Work Item for the given MVA."""
    log.info(f"[WORKITEM] {mva} - starting process")

    # Step 1: Gather existing Work Items
    tiles = get_work_items(driver, mva)
    total = len(tiles)
    log.info(f"[WORKITEM] {mva} - {total} total work items found")

    if total == 0:
        log.info(f"[WORKITEM][SKIP] {mva} - no PM work items found")
        return {"status": "skipped", "reason": "no_pm_workitems", "mva": mva}

    # Step 2: Handle existing Open PM Work Items
    res = complete_pm_workitem(driver, mva, timeout=8)
    return res



def open_pm_workitem_card(driver, mva: str, timeout: int = 8) -> dict:
    """Find and open the first Open PM Work Item card."""
    try:
        tile = driver.find_element(
            By.XPATH,
            (
                "//div[contains(@class,'scan-record-header') "
                "and .//div[contains(@class,'scan-record-header-title')]"
                "[normalize-space()='PM' or normalize-space()='PM Hard Hold - PM'] "
                "and .//div[contains(@class,'scan-record-header-title-right')][normalize-space()='Open']]"
            )
        )
        tile.click()
        log.info(f"[WORKITEM] {mva} - Open PM Work Item card clicked")
        return {"status": "ok", "reason": "card_opened", "mva": mva}
    except Exception as e:
        log.warning(f"[WORKITEM][WARN] {mva} - could not open Open PM Work Item card -> {e}")
        return {"status": "failed", "reason": "open_pm_card", "mva": mva}

def complete_work_item_dialog(driver, note: str = "Done", timeout: int = 10, observe: int = 0) -> dict:
    """Fill the correction dialog with note and click 'Complete Work Item'."""
    try:
        # 1) Wait for visible dialog root
        dialog = safe_wait(
            driver,
            timeout,
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bp6-dialog")),
            desc="Work Item dialog"
        )

        log.info("[DIALOG] Correction dialog opened")

        # 2) Find textarea (scoped to dialog)
        textarea = safe_wait(
            driver,
            timeout,
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.bp6-text-area")),
            desc="Correction textarea"
        )
        time.sleep(5)
        textarea.click()        
        time.sleep(5)
        textarea.clear()
        time.sleep(5)
        textarea.send_keys(note)
        time.sleep(5)
        log.info(f"[DIALOG] Entered note text: {note!r}")
        time.sleep(5)

        # 3) Click 'Complete Work Item'
        complete_btn = safe_wait(
            driver,
            timeout,
            EC.element_to_be_clickable((By.XPATH, ".//button[normalize-space()='Complete Work Item']")),
            desc="Complete Work Item button"
        )
        time.sleep(5)

        complete_btn.click()
        log.info("[DIALOG] 'Complete Work Item' button clicked")

        # 4) Wait for dialog to close
        safe_wait(driver ,timeout, EC.invisibility_of_element(dialog), desc="Dialog to close")

        log.info("[DIALOG] Correction dialog closed")

        return {"status": "ok"}
    except Exception as e:
        log.error(f"[DIALOG][ERROR] complete_work_item_dialog -> {e}")
        return {"status": "failed", "reason": "dialog_exception"}



def mark_complete_pm_workitem(driver, mva: str, note: str = "Done", timeout: int = 8) -> dict:
    """Click 'Mark Complete', then complete the dialog with the given note."""
    if not click_element(driver, (By.CSS_SELECTOR, "button.fleet-operations-pwa__mark-complete-button__spuz8c")):
        if not click_element(driver, (By.XPATH, "//button[normalize-space()='Mark Complete']")):
            return {"status": "failed", "reason": "mark_complete_button", "mva": mva}

    time.sleep(0.2)
    res = complete_work_item_dialog(driver, note=note, timeout=max(10, timeout), observe=1)
    log.info(f"[MARKCOMPLETE] complete_work_item_dialog -> {res}")

    if res and res.get("status") == "ok":
        return {"status": "ok", "reason": "dialog_complete", "mva": mva}
    else:
        return {"status": "failed", "reason": res.get("reason", "dialog_failed"), "mva": mva}




def complete_pm_workitem(driver, mva: str, timeout: int = 8) -> dict:
    """Open the PM Work Item card and mark it complete with note='Done'."""
    time.sleep(9)  # wait for UI to stabilize
    res = open_pm_workitem_card(driver, mva, timeout=timeout)
    if res.get("status") != "ok":
        return res  # pass through failure dict
    time.sleep(9)  # wait for card to open
    res = mark_complete_pm_workitem(driver, mva, note="Done", timeout=timeout)
    time.sleep(9)  # wait for completion to process
    if res.get("status") == "ok":
        return {"status": "ok", "reason": "completed_open_pm", "mva": mva}
    else:
        return {"status": "failed", "reason": res.get("reason", "mark_complete"), "mva": mva}