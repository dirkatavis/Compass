"""Flows for creating, processing, and handling Compass Work Items."""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
        empty list: If MVA is rentable or no work items found
    """
    log.info(f"[WORKITEM] {mva} - checking Lighthouse status...")
    
    try:
        # First check Lighthouse status
        lighthouse_label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "//div[contains(@class, 'vehicle-property-name') and normalize-space()='Lighthouse']"
            ))
        )
        lighthouse_value = lighthouse_label.find_element(
            By.XPATH, 
            "../div[contains(@class, 'vehicle-property-value')]"
        )
        status_text = lighthouse_value.text.strip()
        
        if status_text.lower() == "rentable":
            log.info(f"[WORKITEM] {mva} - Lighthouse status is 'Rentable', skipping review")
            return []
            
        log.info(f"[WORKITEM] {mva} - Lighthouse status: {status_text}, proceeding with review")
    except TimeoutException:
        log.warning(f"[WORKITEM][WARN] {mva} - Lighthouse status not found, continuing with normal flow")
    except Exception as e:
        log.warning(f"[WORKITEM][WARN] {mva} - Error checking Lighthouse status: {str(e)}")
    
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





def create_new_workitem(driver, mva: str) -> dict:
    """Create a new Work Item for the given MVA.
    
    Args:
        driver: Selenium WebDriver instance
        mva: MVA identifier string
        
    Returns:
        dict: Status object containing result of operation
            {
                'status': 'failed'|'success',
                'reason': str,
                'mva': str
            }
    """
    log.info(f"[WORKITEM] {mva} - starting CREATE NEW WORK ITEM workflow")

    try:
        # Wait for and click Add Work Item button
        add_btn_locator = (By.XPATH, "//button[normalize-space()='Add Work Item']")
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(add_btn_locator)
            )
        except TimeoutException:
            log.warning(f"[WORKITEM][WARN] {mva} - Add Work Item button not clickable after 10s")
            return {"status": "failed", "reason": "add_btn_not_clickable", "mva": mva}
            
        if not click_element(driver, add_btn_locator):
            log.warning(f"[WORKITEM][WARN] {mva} - Failed to click Add Work Item button")
            return {"status": "failed", "reason": "add_btn_click_failed", "mva": mva}
            
        log.info(f"[WORKITEM] {mva} - Add Work Item clicked successfully")
        
        # Wait for modal dialog to appear after click
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.bp6-dialog"))
            )
        except TimeoutException:
            log.warning(f"[WORKITEM][WARN] {mva} - Work Item dialog did not appear after click")
            return {"status": "failed", "reason": "dialog_not_shown", "mva": mva}

    except Exception as e:
        log.error(f"[WORKITEM][ERROR] {mva} - Unexpected error creating work item: {str(e)}")
        return {"status": "failed", "reason": f"unexpected_error: {str(e)}", "mva": mva}

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
      1. Check if MVA is rentable (skip if true)
      2. If an open PM Work Item exists, complete it.
      3. Otherwise, start a new Work Item.
         - Try to associate an existing complaint.
         - If none, skip and return control to the test loop.
    
    Args:
        driver: Selenium WebDriver instance
        mva: MVA identifier string
        
    Returns:
        dict: Status object containing result of operation
    """
    from selenium.webdriver.common.by import By  # Ensure By is in scope
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    
    log.info(f"[WORKITEM] {mva} — checking vehicle status")

    try:
        # Check Lighthouse status first
        try:
            # Wait for Lighthouse status value to be visible (10 second timeout)
            lighthouse_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'vehicle-property-name') and normalize-space()='Lighthouse']/following-sibling::div[contains(@class, 'vehicle-property-value')]"))
            )
            lighthouse_status = lighthouse_element.text.strip()
            log.info(f"[LIGHTHOUSE] {mva} — Vehicle Lighthouse status: {lighthouse_status}")
            
            # Skip rentable vehicles - move to next MVA in list
            if lighthouse_status.lower() == "rentable":
                log.info(f"[LIGHTHOUSE] {mva} — Vehicle is rentable, skipping to next MVA")
                return {"status": "skipped", "reason": "vehicle_rentable", "mva": mva}
            
            log.info(f"[WORKITEM] {mva} - Vehicle status: {lighthouse_status}, proceeding with work items")
                
        except TimeoutException:
            log.warning(f"[LIGHTHOUSE] {mva} — Could not find Lighthouse status element, proceeding with caution")
    except TimeoutException:
        log.warning(f"[WORKITEM][WARN] {mva} - Lighthouse status not found, continuing with normal flow")
    except Exception as e:
        log.warning(f"[WORKITEM][WARN] {mva} - Error checking Lighthouse status: {str(e)}")

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

def complete_work_item_dialog(driver, note: str = "Done", timeout: int = 10) -> dict:
    """Fill the work item completion dialog with a note and submit it.
    
    Args:
        driver: Selenium WebDriver instance
        note: Text to enter in the completion note field
        timeout: Maximum seconds to wait for each element
        
    Returns:
        dict: Status object containing result of operation
            {
                'status': 'ok'|'failed',
                'reason': str,
                'details': Optional[str]
            }
    
    Raises:
        AssertionError: If any required element is not found within timeout
    """
    try:
        # 1) Wait for visible dialog root
        try:
            dialog = safe_wait(
                driver,
                timeout,
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bp6-dialog")),
                desc="Work Item dialog"
            )
            log.info("[DIALOG] Work item completion dialog detected")
        except AssertionError:
            log.error("[DIALOG] Work item dialog not found or not visible")
            return {"status": "failed", "reason": "dialog_not_found"}

        # 2) Find and interact with textarea
        try:
            textarea = safe_wait(
                driver,
                timeout,
                EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.bp6-text-area")),
                desc="Correction textarea"
            )
            
            # Wait for textarea to be interactive
            WebDriverWait(driver, timeout).until(
                lambda d: textarea.is_enabled() and textarea.is_displayed()
            )
            
            textarea.click()
            textarea.clear()
            textarea.send_keys(note)
            log.info(f"[DIALOG] Entered completion note: {note!r}")
            
        except (AssertionError, TimeoutException) as e:
            log.error(f"[DIALOG] Failed to interact with textarea: {str(e)}")
            return {"status": "failed", "reason": "textarea_interaction_failed"}

        # 3) Find and click 'Complete Work Item' button
        try:
            complete_btn = safe_wait(
                driver,
                timeout,
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Complete Work Item']")),
                desc="Complete Work Item button"
            )
            
            complete_btn.click()
            log.info("[DIALOG] Clicked 'Complete Work Item' button")
            
        except AssertionError:
            log.error("[DIALOG] Complete button not found or not clickable")
            return {"status": "failed", "reason": "complete_button_failed"}
        
        # 4) Wait for dialog to close
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element(dialog)
            )
            log.info("[DIALOG] Work item completion dialog closed successfully")
            return {"status": "ok"}
            
        except TimeoutException:
            log.error("[DIALOG] Dialog did not close after completion")
            return {"status": "failed", "reason": "dialog_not_closed"}
            
    except Exception as e:
        log.error(f"[DIALOG][ERROR] Unexpected error in work item completion: {str(e)}")
        return {
            "status": "failed", 
            "reason": "unexpected_error",
            "details": str(e)
        }

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