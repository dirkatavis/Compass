import time
import os

from selenium.webdriver.common.by import By
from utils.logger import log
from utils.ui_helpers import (click_element, find_element , find_elements, take_screenshot)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from utils.ui_helpers import click_element
from flows.opcode_flows import select_opcode    
from flows.mileage_flows import complete_mileage_dialog



def handle_existing_complaint(driver, mva: str) -> dict:
    """Select an existing complaint tile and advance."""
    log.debug(f"[COMPLAINT] {mva} - Handling existing complaint.")
    if click_element(driver, (By.XPATH, "//button[normalize-space()='Next']")):
        log.info(f"[COMPLAINT] {mva} - Next clicked after selecting existing complaint")
        return {"status": "ok"}

    else:
        log.debug(f"[WORKITEM][WARN] {mva} - could not advance with existing complaint")
        return {"status": "failed", "reason": "existing_complaint_next"}

def handle_new_complaint(driver, mva: str) -> dict:
    """Create and submit a new PM complaint."""
    log.debug(f"[COMPLAINT] {mva} - Handling new complaint.")
    
    # Use a more precise locator targeting the text container if it's nested
    add_btn_xpath = "//button[descendant-or-self::*[normalize-space()='Add New Complaint']]"
    
    # DIAGNOSTIC LOCATORS: Targeting internal elements as suggested
    # We will try clicking the text container directly (span or p) to see which triggers the UI
    # FINALIZED LOCATOR (Winning element from diagnostic run)
    add_complaint_xpath = "//button[descendant-or-self::*[normalize-space()='Add New Complaint']]"
    drivable_dialog_xpath = "//*[contains(text(), 'Is vehicle drivable?')]"
    dialog_container_xpath = "//div[contains(@class, 'bp6-dialog')] | //div[contains(@class, 'pwa-dialog')]"

    log.info(f"[WORKITEM] {mva} - Attempting to click 'Add New Complaint'...")

    # Stricter transition: verify we aren't seeing a ghost element before we even start
    initial_presence = driver.find_elements(By.XPATH, drivable_dialog_xpath)
    visible_ghosts = [el for el in initial_presence if el.is_displayed()]
    if visible_ghosts:
        log.warning(f"[WORKITEM] {mva} - Ghost drivability text detected before click. Attempting to clear state...")

    # Pillar 2: State-matched interaction.
    try:
        # We need to re-locate to ensure we have the fresh element
        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, add_complaint_xpath)))
        
        # Action
        btn.click()
        log.info(f"[WORKITEM] {mva} - Add New Complaint clicked. Waiting for UI transition...")

        # Shorter, more frequent polling for transition to avoid finding ghosts in the same second
        WebDriverWait(driver, 15).until(
            lambda d: any(el.is_displayed() for el in d.find_elements(By.XPATH, drivable_dialog_xpath))
        )
        
        # Double check: the button we just clicked should typically be gone or obscured
        if driver.find_elements(By.XPATH, add_complaint_xpath):
            btns = driver.find_elements(By.XPATH, add_complaint_xpath)
            if any(b.is_displayed() for b in btns):
                 log.error(f"[WORKITEM][ERROR] {mva} - TRANSITION FAIL: 'Add New Complaint' is still visible. Dialog text detected but button NOT obscured. EXITING.")
                 return {"status": "failed", "reason": "dialog_shadow_transition"}

        log.info(f"[WORKITEM] {mva} - SUCCESS: Drivability dialog transition verified.")
    except Exception as e:
        log.error(f"[WORKITEM][ERROR] {mva} - TRANSITION FAIL: Standard click did not open Drivability dialog ({e}). Retrying via JS force-click...")
        try:
            target = driver.find_element(By.XPATH, add_complaint_xpath)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", target)
            
            WebDriverWait(driver, 15).until(
                lambda d: any(el.is_displayed() for el in d.find_elements(By.XPATH, drivable_dialog_xpath))
            )
            log.info(f"[WORKITEM] {mva} - SUCCESS: JS click triggered Drivability dialog.")
        except Exception as js_e:
            log.error(f"[WORKITEM][ERROR] {mva} - TRANSITION FAIL: Could not open dialog even with JS: {js_e}")
            take_screenshot(driver, prefix=f"add_complaint_fail_{mva}")
            return {"status": "failed", "reason": "dialog_never_opened"}

    # Drivability -> Yes
    log.info(f"[DRIVABLE] {mva} - answering drivability question: Yes")
    if not click_element(driver, (By.XPATH, "//button[descendant-or-self::*[normalize-space()='Yes']]")):
        log.warning(f"[WORKITEM][WARN] {mva} - Drivable=Yes button not found")
        return {"status": "failed", "reason": "drivable_yes"}
    log.info(f"[COMPLAINT] {mva} - Drivable=Yes")


    # Complaint Type -> PM
    if not click_element(driver, (By.XPATH, "//button[descendant-or-self::*[normalize-space()='PM']]")):
        log.warning(f"[WORKITEM][WARN] {mva} - Complaint type PM not found")
        return {"status": "failed", "reason": "complaint_pm"}
    log.info(f"[COMPLAINT] {mva} - PM complaint selected")


    # Submit
    if not click_element(driver, (By.XPATH, "//button[descendant-or-self::*[normalize-space()='Submit Complaint']]")):

        log.warning(f"[WORKITEM][WARN] {mva} - Submit Complaint not found")
        return {"status": "failed", "reason": "submit_complaint"}
    log.info(f"[COMPLAINT] {mva} - Submit Complaint clicked")
    
    # Wait for the "Next" button to actually be clickable and visible after submission
    log.info(f"[WORKITEM] {mva} - Waiting for Next button to enable...")
    
    next_btn_xpath = "//button[descendant-or-self::*[normalize-space()='Next']]"
    complaint_tile_xpath = "//div[contains(@class,'complaintItem')]"
    
    for attempt in range(15):
        try:
            # Check for blocking overlays or loading spinners
            spinners = driver.find_elements(By.XPATH, "//*[contains(@class, 'spinner') or contains(@class, 'loading')]")
            if spinners:
                log.info(f"[WORKITEM] {mva} - UI is busy (loading spinner detected)")
                time.sleep(2)
                continue

            # Check if we have visible complaint tiles now (meaning submission likely succeeded)
            tiles = driver.find_elements(By.XPATH, complaint_tile_xpath)
            if tiles:
                # Find the PM one
                pm_tiles = [t for t in tiles if "PM" in t.text]
                if pm_tiles:
                    log.info(f"[WORKITEM] {mva} - PM complaint tile detected. Ensuring it is selected...")
                    # Sometimes you must click it to "check" it before Next enables
                    try:
                        driver.execute_script("arguments[0].click();", pm_tiles[0])
                    except: pass

            # Find buttons and log their state
            btns = driver.find_elements(By.XPATH, next_btn_xpath)
            if btns:
                # Pick the most likely "Next" button (usually the last/topmost one in the dialog)
                btn = btns[-1]
                
                if btn.is_displayed():
                    cls = btn.get_attribute("class") or ""
                    is_disabled = "disabled" in cls.lower() or not btn.is_enabled()
                    
                    if not is_disabled:
                        log.info(f"[WORKITEM] {mva} - Next button is ENABLED. Clicking now...")
                        try:
                            btn.click()
                        except:
                            driver.execute_script("arguments[0].click();", btn)
                        
                        # Verify transition
                        time.sleep(3)
                        if driver.find_elements(By.XPATH, "//*[contains(text(), 'Odometer') or contains(text(), 'Mileage')]"):
                            log.info(f"[WORKITEM] {mva} - SUCCESS: Flow advanced to Mileage page.")
                            return {"status": "ok"}
                        else:
                            log.error(f"[WORKITEM][ERROR] {mva} - TRANSITION FAIL: Next button click did not land on Mileage page. UI is frozen. EXITING.")
                            return {"status": "failed", "reason": "next_button_frozen"}
                    else:
                        log.debug(f"[WORKITEM] {mva} - Next button found but still disabled (Attempt {attempt+1})")
                        # Try a JS re-click of Submit if it's still there
                        submit_xpath = "//button[descendant-or-self::*[normalize-space()='Submit Complaint']]"
                        submits = driver.find_elements(By.XPATH, submit_xpath)
                        if submits and submits[0].is_displayed():
                            log.info(f"[WORKITEM] {mva} - Submit button still visible, re-clicking via JS...")
                            driver.execute_script("arguments[0].click();", submits[0])
            
            time.sleep(3)
        except Exception as e:
            log.warning(f"[WORKITEM] {mva} - Error during Next button poll: {e}")
            time.sleep(1)

    # Final attempt using the robust helper if the custom loop failed
    log.info(f"[WORKITEM] {mva} - Custom poll failed, attempting final click via click_next_in_dialog...")
    from utils.ui_helpers import click_next_in_dialog
    if click_next_in_dialog(driver, timeout=10):
        # Even here, we should double check the state
        time.sleep(3)
        if driver.find_elements(By.XPATH, "//*[contains(text(), 'Odometer') or contains(text(), 'Mileage')]"):
             log.info(f"[WORKITEM] {mva} - SUCCESS: click_next_in_dialog advanced to Mileage.")
             return {"status": "ok"}
        else:
             log.error(f"[WORKITEM][ERROR] {mva} - TRANSITION FAIL: click_next_in_dialog claimed success but Mileage page NOT detected. EXITING.")
             return {"status": "failed", "reason": "next_dialog_failure"}
    
    return {"status": "failed", "reason": "new_complaint_next"}
    log.info(f"[COMPLAINT] {mva} - Next clicked after new complaint")

    return {"status": "ok"}

def handle_complaint(driver, mva: str, found_existing: bool) -> dict:
    """Route complaint handling to existing or new complaint flows."""
    log.debug(f"[COMPLAINT] {mva} - Routing complaint handling. Found existing: {found_existing}")
    if found_existing:
        return handle_existing_complaint(driver, mva)
    else:
        return handle_new_complaint(driver, mva)

def find_dialog(driver):
    locator = (By.CSS_SELECTOR, "div.bp6-dialog, div[class*='dialog']")
    return find_element(driver, locator)

def detect_existing_complaints(driver, mva: str):
    """Detect complaint tiles containing 'PM' in their text."""
    try:
        time.sleep(3)  # wait for tiles to load
        tiles = driver.find_elements(
            By.XPATH, "//div[contains(@class,'fleet-operations-pwa__complaintItem__')]"
        )
        log.debug(f"[COMPLAINT] {mva} — found {len(tiles)} total complaint tile(s)")

        valid_tiles = [t for t in tiles if "PM" in t.text.strip()]
        log.debug(
            f"[COMPLAINT] {mva} — filtered {len(valid_tiles)} PM-type complaint(s): "
            f"{[t.text for t in valid_tiles]}"
        )

        return valid_tiles
    except Exception as e:
        log.error(f"[COMPLAINT][ERROR] {mva} — complaint detection failed → {e}")
        return []

def find_pm_tiles(driver, mva: str):
    """Locate complaint tiles of type 'PM' or 'PM Hard Hold - PM'."""
    try:
        # Relax the XPath to find anything that looks like a PM complaint tile
        xpath = (
            "//div[contains(@class,'tileContent') and contains(., 'PM')]"
            "/ancestor::div[contains(@id, 'complaint-item') or contains(@class,'complaintItem')]"
        )
        tiles = driver.find_elements(By.XPATH, xpath)
        
        # Log what we found to help debug
        if tiles:
            texts = [t.text.replace('\n', ' ') for t in tiles]
            log.info(f"[COMPLAINT] {mva} — Found these PM candidate tiles: {texts}")
        
        log.info(f"[COMPLAINT] {mva} — found {len(tiles)} PM candidate complaint tile(s)")
        return tiles
    except Exception as e:
        log.info(f"[COMPLAINT] {mva} — error searching for PM complaint tiles ({e})")
        return []

def associate_existing_complaint(driver, mva: str) -> dict:
    """
    Look for existing PM complaints and associate them.
    Flow: select complaint tile → Next (complaint) → Next (mileage) → Opcode (PM Gas) → Finalize Work Item.
    """
    log.debug(f"[COMPLAINT] {mva} - Associating existing complaint.")
    try:
        tiles = driver.find_elements(
            By.XPATH, "//div[contains(@class,'fleet-operations-pwa__complaintItem__')]"
        )
        time.sleep(3)  # wait for tiles to load
        if not tiles:
            log.info(f"[COMPLAINT][EXISTING] {mva} - no complaint tiles found")
            return {"status": "skipped_no_complaint", "mva": mva}

        # Filter PM complaints only
        pm_tiles = [t for t in tiles if any(label in t.text for label in ["PM", "PM Hard Hold - PM"])]
        if not pm_tiles:
            log.info(f"[COMPLAINT][EXISTING] {mva} - no PM complaints found")
            return {"status": "skipped_no_complaint", "mva": mva}

        if not pm_tiles:
            log.info(f"[COMPLAINT][EXISTING] {mva} - no PM complaints found")
            return {"status": "no_pm", "mva": mva}

        # Click first matching PM complaint
        tile = pm_tiles[0]
        try:
            tile.click()
            log.info(f"[COMPLAINT][ASSOCIATED] {mva} - complaint '{tile.text.strip()}' selected")
        except Exception as e:
            log.warning(f"[COMPLAINT][WARN] {mva} - failed to click complaint tile → {e}")
            return {"status": "failed", "reason": "tile_click", "mva": mva}

        # Step 1: Complaint → Next
        from utils.ui_helpers import click_next_in_dialog
        if not click_next_in_dialog(driver, timeout=8):
            return {"status": "failed", "reason": "complaint_next", "mva": mva}

        # Step 2: Mileage → Next
        res = complete_mileage_dialog(driver, mva)
        if res.get("status") != "ok":
            return {"status": "failed", "reason": "mileage", "mva": mva}

        # Step 3: Opcode → PM Gas
        res = select_opcode(driver, mva, code_text="PM Gas")
        if res.get("status") != "ok":
            return {"status": "failed", "reason": "opcode", "mva": mva}

        return {"status": "associated", "mva": mva}

    except Exception as e:
        log.warning(f"[COMPLAINT][WARN] {mva} - complaint association failed → {e}")
        return {"status": "failed", "reason": "exception", "mva": mva}

def create_new_complaint(driver, mva: str) -> dict:
    """Create a new complaint when no suitable PM complaint exists."""
    log.debug(f"[COMPLAINT] {mva} - Creating new complaint.")
    log.info(f"[COMPLAINT][NEW] {mva} - creating new complaint")

    try:
        # 1. Click Add New Complaint (Explicit locator)
        add_btn_xpath = "//button[descendant-or-self::*[normalize-space()='Add New Complaint']]"
        
        log.info(f"[COMPLAINT][NEW] {mva} - Attempting to click Add New Complaint...")
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, add_btn_xpath))
            )
            btn.click()
            time.sleep(1)
            # Fallback if standard click fails
            if not driver.find_elements(By.XPATH, "//*[contains(text(), 'Is the vehicle drivable?')]"):
                log.warning(f"[COMPLAINT][NEW] {mva} - Standard click failed to open dialog. trying JS click.")
                driver.execute_script("arguments[0].click();", btn)
        except Exception as e:
            log.warning(f"[COMPLAINT][NEW][WARN] {mva} - could not click Add New Complaint: {e}")
            return {"status": "failed", "reason": "add_btn"}
        
        # VERIFICATION: Wait for the Drivability Dialog text to confirm transition
        drivable_text_xpath = "//*[contains(text(), 'Is the vehicle drivable?')]"
        try:
            WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.XPATH, drivable_text_xpath))
            )
        except Exception:
            log.error(f"[COMPLAINT][ERROR] {mva} - Dialog did not open after clicking Add New Complaint")
            from utils.ui_helpers import take_screenshot
            take_screenshot(driver, prefix=f"failed_dialog_new_{mva}")
            return {"status": "failed", "reason": "dialog_transition"}

        # 2. Handle Drivability (Yes/No). Simplest case -> always Yes
        if not click_element(driver, (By.XPATH, "//button[normalize-space()='Yes']")):
            log.warning(
                f"[COMPLAINT][NEW][WARN] {mva} - could not click Yes in Drivability step"
            )
            return {"status": "failed", "reason": "drivability"}
        log.info(f"[COMPLAINT][NEW] {mva} - Drivability Yes clicked")
        time.sleep(1)

        # 3) Complaint Type = PM (auto-advances, no Next button here)
        if click_element(driver, (By.XPATH, "//button[normalize-space()='PM']")):
            log.info(f"[COMPLAINT] {mva} - Complaint type 'PM' selected")
            time.sleep(2)  # allow auto-advance to Additional Info screen
        else:
            log.warning(f"[COMPLAINT][WARN] {mva} - Complaint type 'PM' not found")
            return {"status": "failed", "reason": "complaint_type", "mva": mva}

        # 4) Additional Info screen -> Submit
        if click_element(driver, (By.XPATH, "//button[normalize-space()='Submit Complaint']")):
            log.info(f"[COMPLAINT] {mva} - Additional Info submitted")
            time.sleep(2)
        else:
            log.warning(f"[COMPLAINT][WARN] {mva} - could not submit Additional Info")
            return {"status": "failed", "reason": "submit_info", "mva": mva}

        return {"status": "created"}


    except Exception as e:
        log.error(f"[COMPLAINT][NEW][ERROR] {mva} - creation failed -> {e}")
        return {"status": "failed", "reason": "exception"}

def click_next_in_dialog(driver, timeout: int = 10) -> bool:
    """
    Click the 'Next' button inside the active dialog.
    Returns True if clicked, False if not found.
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        locator = (By.XPATH, "//button[normalize-space()='Next']")
        log.debug(f"[CLICK] attempting to click {locator} (dialog Next)")

        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        btn.click()

        log.info("[DIALOG] Next button clicked")
        return True

    except Exception as e:
        log.warning(f"[DIALOG][WARN] could not click Next button → {e}")
        return False
