"""Flows for creating, processing, and handling Compass Work Items."""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from flows.complaints_flows import associate_existing_complaint, handle_new_complaint
from flows.finalize_flow import finalize_workitem
from flows.mileage_flows import complete_mileage_dialog
from flows.opcode_flows import select_opcode
from utils.logger import log
from utils.ui_helpers import click_element, safe_wait
from pages.vehicle_properties_page import VehiclePropertiesPage
from config.config_loader import get_config

def get_work_items(driver, mva: str):
    """Collect all open PM work items for the given MVA."""
    log.debug(f"[WORKITEM] {mva} - Getting open work items.")
    time.sleep(2)  
    try:
        # Relaxed search for investigation
        xpath = "//div[contains(@class, 'fleet-operations-pwa__scan-record__')]"
        all_tiles = driver.find_elements(By.XPATH, xpath)
        
        open_pm_items = []
        for tile in all_tiles:
            text = tile.text
            if "Open" in text and "PM" in text:
                open_pm_items.append(tile)
                log.info(f"[WORKITEMS] {mva} - Found an matching OPEN PM item: {text!r}")
            elif "Open" in text:
                log.debug(f"[WORKITEMS][DEBUG] Found non-PM OPEN item: {text!r}")
                
        log.info(f"[WORKITEMS] {mva} - Final detected count: {len(open_pm_items)}")
        return open_pm_items
    except Exception as e:
        log.warning(f"[WORKITEM][WARN] {mva} - could not collect open work items -> {e}")
        return []


def get_recent_closed_pm_items(driver, mva: str, days: int = 30):
    """
    Collect closed PM work items and verify if they are recent.
    Returns a list of matching tile elements.
    """
    log.debug(f"[AUDITOR] {mva} - checking for recent closed PM records")
    try:
        # Broaden search to ANY scan record to investigate missing items
        xpath = "//div[contains(@class, 'fleet-operations-pwa__scan-record__')]"
        all_tiles = driver.find_elements(By.XPATH, xpath)
        log.info(f"[AUDITOR][DEBUG] {mva} - Total scan record tiles found: {len(all_tiles)}")
        
        # If we don't find many tiles, check if there's a "Show More" or if the page text contains 1/28
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "1/28/2026" in page_text:
            log.info(f"[AUDITOR][DEBUG] {mva} - The date '1/28/2026' IS on the page somewhere!")
            # Let's find exactly which element has it
            specific_element = driver.find_elements(By.XPATH, "//*[contains(text(), '1/28/2026')]")
            for el in specific_element:
                log.info(f"[AUDITOR][DEBUG] Found element with 1/28/2026: tag={el.tag_name}, text={el.text!r}")
        else:
            log.warning(f"[AUDITOR][DEBUG] {mva} - The date '1/28/2026' NOT found in page text. Taking diagnostic screenshot.")
            from utils.ui_helpers import take_screenshot
            take_screenshot(driver, prefix=f"auditor_gap_{mva}")

        recent_tiles = []
        from datetime import datetime, timedelta
        
        for tile in all_tiles:
            try:
                full_text = tile.text
                log.info(f"[AUDITOR][DEBUG] Examining Tile contents:\n{full_text!r}")
                
                # Check for PM relevance
                is_pm = "PM" in full_text
                # Check for "Complete" or "Closed" or "Open" - we want to see them all
                is_closed = "Complete" in full_text
                
                if not is_pm:
                    continue
                    
                date_part = None
                if "Created At" in full_text:
                    import re
                    match = re.search(r"Created At:\s*(\d{1,2}/\d{1,2}/\d{4})", full_text)
                    if match:
                        date_part = match.group(1)
                
                if date_part:
                    created_date = datetime.strptime(date_part, "%m/%d/%Y")
                    days_diff = (datetime.now() - created_date).days
                    
                    if days_diff <= days:
                        # If it's PM and recent, we care!
                        recent_tiles.append(tile)
                        status = "OPEN" if "Open" in full_text else "CLOSED"
                        log.info(f"[AUDITOR][PILLAR3] {mva} - Recognized recent Paperwork Reality ({status} PM from {date_part})")
                    else:
                        log.warning(f"[AUDITOR][PILLAR3] {mva} - Found PM, but it is too old ({date_part}) - {days_diff} days ago")
                else:
                    log.warning(f"[AUDITOR][PILLAR3] {mva} - PM tile found but could not parse 'Created At' date.")
            except Exception as e:
                log.error(f"[AUDITOR] {mva} - Error processing tile for recency: {e}")
                
        return recent_tiles
    except Exception:
        return []





def create_new_workitem(driver, mva: str):
    """Create a new Work Item for the given MVA."""
    log.debug(f"[WORKITEM] {mva} - Creating new work item.")
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
    Fleet PM Data Integrity Auditor logic:
    Gate 1: Validate Status==RENTABLE and Buffer >= 4000.
    Gate 2: Audit existing Work Items and sync.
    """
    log.info(f"[AUDITOR] {mva} - starting PM processing")

    # Gate 1: Validation
    vpp = VehiclePropertiesPage(driver)
    status = vpp.get_lighthouse_status()
    odo = vpp.get_odometer()
    next_pm = vpp.get_next_pm_mileage()
    
    # Heuristic: Use PM Interval as the threshold for health. 
    # Fallback to config if scraping fails.
    interval = vpp.get_pm_interval()
    threshold = interval if interval else get_config("mileage_threshold", 4000)
    
    # Calculate Buffer
    buffer = -1
    if next_pm is not None and odo is not None:
        buffer = next_pm - odo
    
    log.info(f"[AUDITOR] {mva} - Status: {status}, Odo: {odo}, Next PM: {next_pm}, Interval: {interval}, Buffer: {buffer}")

    # Check Gate 1
    gate1_pass = True
    reason = ""
    
    if (status or "").upper() != "RENTABLE":
        gate1_pass = False
        reason = f"Status Lag ({status or 'Unknown'})"
    elif buffer < threshold:
        gate1_pass = False
        reason = f"Data Lag (Pending Legacy Entry). Buffer: {buffer} < {threshold}. Current: {odo}, Next: {next_pm}"
        
    if not gate1_pass:
        log.warning(f"[AUDITOR][WARN] {mva} - Gate 1 Lag detected ({reason}). Proceeding to verify Paperwork Pillar anyway.")
    else:
        log.info(f"[AUDITOR][PASS] {mva} - Gate 1 success, proceeding to documentation audit")

    # Gate 2: Documentation Audit
    # Use helper for more robust navigation
    from utils.ui_helpers import click_work_items
    if not click_work_items(driver):
        log.error(f"[AUDITOR][ERROR] {mva} - could not navigate to Work Items tab")
        return {"status": "failed", "reason": "navigation_work_items", "mva": mva}

    # Case: Existing open PM work items
    items = get_work_items(driver, mva)
    if items:
        log.info(f"[AUDITOR][PILLAR3] {mva} - Found Open Paperwork Trail, syncing status...")
        return complete_pm_workitem(driver, mva)

    # Case: Existing recent closed PM work items (Verified Pillar)
    closed_recent = get_recent_closed_pm_items(driver, mva, days=30)
    if closed_recent:
        log.info(f"[AUDITOR][SUCCESS] {mva} - Pillar 3 Verified. Recent closed PM record exists.")
        from utils.ui_helpers import navigate_back_to_home
        navigate_back_to_home(driver)
        return {"status": "ok", "reason": "verified_success", "mva": mva}
    
    # Case: No recent records found -> Create new PM to address paperwork gap.
    log.info(f"[AUDITOR][PILLAR3] {mva} - Paperwork Gap detected (no recent PM record), acting as Virtual Clerk...")

    if not click_element(driver, (By.XPATH, "//button[descendant-or-self::*[normalize-space()='Add Work Item']]"),
                     desc="Add Work Item", timeout=8):
        log.warning(f"[AUDITOR][WARN] {mva} - could not click Add Work Item")
        return {"status": "failed", "reason": "add_btn", "mva": mva}

    res = associate_existing_complaint(driver, mva)

    if res.get("status") == "associated":
        return finalize_workitem(driver, mva)
    elif res.get("status") == "skipped_no_complaint":
        log.info(f"[AUDITOR] {mva} - No existing complaint found. Addressing Paperwork Gap by creating new PM complaint.")
        
        # Step 1: Create New Complaint (Add New -> Drivability: Yes -> PM -> Submit -> Next)
        res = handle_new_complaint(driver, mva)
        if res.get("status") != "ok":
            log.error(f"[AUDITOR][ERROR] {mva} - handle_new_complaint failed: {res.get('reason')}")
            return res
            
        # Step 2: Mileage Dialog (Clicks Next)
        res = complete_mileage_dialog(driver, mva)
        if res.get("status") != "ok":
            log.error(f"[AUDITOR][ERROR] {mva} - complete_mileage_dialog failed: {res.get('reason')}")
            return res
            
        # Step 3: Opcode Selection (Clicks PM Gas)
        res = select_opcode(driver, mva)
        if res.get("status") != "ok":
            log.error(f"[AUDITOR][ERROR] {mva} - select_opcode failed: {res.get('reason')}")
            return res
            
        # Step 4: Finalize (Create Work Item -> Mark Complete -> Done)
        log.info(f"[AUDITOR] {mva} - New PM record drafted. Finalizing...")
        return finalize_workitem(driver, mva)

    return res







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
        # Step 1: Find the parent div that contains both the title and the 'PM' complaint
        log.info(f"[WORKITEM] {mva} - Searching for the PM work item card...")
        
        parent_card = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'fleet-operations-pwa__scan-record__') and ./div[contains(@class, 'fleet-operations-pwa__scan-record-header__')] and ./div[contains(@class, 'fleet-operations-pwa__scan-record-row-2__') and contains(., 'PM')]]"
        )
        
        log.info(f"[WORKITEM] {mva} - Found the parent card.")
        
        # Step 2: Find the title bar element within the parent card
        log.info(f"[WORKITEM] {mva} - Searching for the title bar within the found card...")
        
        title_bar = parent_card.find_element(
            By.XPATH,
            "./div[contains(@class, 'fleet-operations-pwa__scan-record-header__')]"
        )
        
        log.info(f"[WORKITEM] {mva} - Found the title bar.")
        
        # Step 3: Click the title bar
        title_bar.click()
        
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
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Complete Work Item']")),
            desc="Complete Work Item button"
        )
        time.sleep(5)


        complete_btn.click()
        log.info("[DIALOG] 'Complete Work Item' button clicked")
    

        # 4) Wait for dialog to close
        safe_wait(driver ,timeout, EC.invisibility_of_element(dialog), desc="Dialog to close")    

        log.info("[DIALOG] Correction dialog closed")

        # The issue might be that closing the UI short after clicking the button 
        # doesn't give enough time for the backend to process the completion.
        # Adding a longer wait here to ensure the process completes before proceeding.
        time.sleep(10)

        return {"status": "ok"}
    except Exception as e:
        log.error(f"[DIALOG][ERROR] complete_work_item_dialog -> {e}")
        return {"status": "failed", "reason": "dialog_exception"}



def mark_complete_pm_workitem(driver, mva: str, note: str = "Done", timeout: int = 8) -> dict:
    """Click 'Mark Complete', then complete the dialog with the given note."""
    if not click_element(driver, (By.XPATH, "//button[descendant-or-self::*[normalize-space()='Mark Complete']]")):
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
    time.sleep(5)  # wait for UI to stabilize
    res = open_pm_workitem_card(driver, mva, timeout=timeout)
    if res.get("status") != "ok":
        return res  # pass through failure dict
    time.sleep(5)  # wait for card to open
    res = mark_complete_pm_workitem(driver, mva, note="Done", timeout=timeout)
    time.sleep(5)  # wait for completion to process
    if res.get("status") == "ok":
        return {"status": "ok", "reason": "completed_open_pm", "mva": mva}
    else:
        return {"status": "failed", "reason": res.get("reason", "mark_complete"), "mva": mva}