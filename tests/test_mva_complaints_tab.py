import json
import time
import pytest
from selenium.webdriver.common.by import By
from pages.opcode_dialog import OpcodeDialog
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core import driver_manager
#from pages.login_page import LoginPage
from pages.login_page import LoginPage
from utils.data_loader import load_mvas
from utils.ui_helpers import click_button
from utils.mva_helpers import click_add_new_complaint_button
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.ui_helpers import (
    click_work_items,
    get_work_items,
    has_open_of_type,
    has_complete_of_type,
    process_pm_workitem_flow,
    debug_list_work_items,
    open_pm_workitem_card,
    mark_complete_pm_workitem,
    click_done,
)

# INSERT BELOW (helper):
from utils.ui_helpers import click_button

from selenium.webdriver.common.by import By  # ensure present

def create_pm_workitem(driver, mva: str):
    print(f"[WORKITEM] {mva} — creating new PM Work Item")

    # 1) Add Work Item
    if not click_button(driver, text="Add Work Item", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — add_btn"); return {"status":"failed","reason":"add_btn"}

    # 2) Entry: Add/Create New Complaint (flow-specific, but using generic helper)
    if not (click_button(driver, text="Add New Complaint", timeout=8)
            or click_button(driver, text="Create New Complaint", timeout=8)):
        print(f"[WORKITEM][WARN] {mva} — entry_step"); return {"status":"failed","reason":"entry_step"}
    time.sleep(4)  # allow UI to settle

    # 3) Drivability → Yes (click the <button> itself)
    try:
        btn = driver.find_element(By.XPATH, "//button[.//h1[normalize-space()='Yes']]")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
        print(f"[COMPLAINT] {mva} — Drivable=Yes")
    except Exception:
        print(f"[WORKITEM][WARN] {mva} — drivable_yes")
        return {"status": "failed", "reason": "drivable_yes"}
    
    time.sleep(4)  # allow UI to settle


    # 4) Complaint type → PM
    if not click_button(driver, text="PM", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — complaint_pm"); return {"status":"failed","reason":"complaint_pm"}
    else:
        print(f"[COMPLAINT] {mva} — PM complaint selected")
        #input("PM tile clicked: Press Enter to continue or Ctrl+C to abort...")  # pause for manual inspection

    time.sleep(4)  # allow UI to settle
    # 5) Submit Complaint
    if not click_button(driver, text="Submit Complaint", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — submit_complaint"); return {"status":"failed","reason":"submit_complaint"}
    else:
        print(f"[COMPLAINT] {mva} — Submit Complaint clicked")
        input("Submit Complaint clicked: Press Enter to continue or Ctrl+C to abort...")  # pause for manual inspection    

    # 6) Mileage → Next
    time.sleep(5)  # allow UI to settle
    if not click_button(driver, text="Next", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — mileage_next"); return {"status":"failed","reason":"mileage_next"}
    else:
        print(f"[COMPLAINT] {mva} — Mileage Next clicked")
        input("Mileage Next clicked: Press Enter to continue or Ctrl+C to abort...")

    time.sleep(4)  # allow UI to settle


    # 7) Opcode → PM Gas
    xp = ("//div[contains(@class,'opCodeItem')]"
        "[.//div[contains(@class,'opCodeText')][normalize-space()='PM Gas']]")
    print(f"[DBG] searching for PM Gas tile → {xp}")
    try:
        tile = driver.find_element(By.XPATH, xp)
        print(f"[DBG] found tile, class='{tile.get_attribute('class')}'")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tile)
        try:
            tile.click()
            print(f"[DBG] Selenium .click() attempted")
        except Exception:
            driver.execute_script("arguments[0].click();", tile)
            print(f"[DBG] JS click() attempted")
        cls = tile.get_attribute("class") or ""
        if "selected" in cls:
            print(f"[COMPLAINT] {mva} — Opcode 'PM Gas' selected")
        else:
            print(f"[WORKITEM][WARN] {mva} — opcode_pm_gas not selected after click")
            return {"status": "failed", "reason": "opcode_pm_gas"}
    except Exception as e:
        print(f"[WORKITEM][WARN] {mva} — opcode_pm_gas not found → {e}")
        return {"status": "failed", "reason": "opcode_pm_gas_not_found"}


    # 8) Create Work Item
    input("Create Work Item: Press Enter to continue or Ctrl+C to abort...")  # pause for manual inspection
    if not click_button(driver, text="Create Work Item", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — create_wi")
        return {"status":"failed","reason":"create_wi"}

    print(f"[WORKITEM] {mva} — PM Work Item created")
    return {"status":"created"}




def _dbg_dialog(driver):
	try:
		dlg = driver.find_element(By.CSS_SELECTOR, "div.bp6-dialog, div[class*='dialog']")
	except Exception:
		dlg = driver
	btns = dlg.find_elements(By.XPATH, ".//button//*[self::span or self::div or self::p or self::strong]|.//button")
	labels = [b.text.strip() for b in btns if b.text.strip()]
	print(f"[DBG] dialog buttons → {labels[:12]}")
	try:
		driver.save_screenshot("debug_drivable.png")
		print("[DBG] screenshot → debug_drivable.png")
	except Exception:
		pass



# Utility: enter MVA and wait for the echoed value in the vehicle pane
def _enter_mva_and_wait_for_hit(driver, mva: str, timeout: int = 12):
    # ensure we're focused on the Mobile Compass tab (new tab often opens)
    try:
        driver.switch_to.window(driver.window_handles[-1])
    except Exception:
        pass

    # Find the active vehicle search input (defensive locators)
    candidates = [
        (By.CSS_SELECTOR, "input.bp6-input[placeholder*='Enter MVA']"),
        (By.XPATH, "//input[@type='text' and contains(@placeholder,'MVA')]"),
        (By.XPATH, "//div[@role='tabpanel' and @aria-hidden='false']//input[@type='text']"),
    ]
    field = None
    for by, sel in candidates:
        try:
            field = WebDriverWait(driver, 4).until(
                EC.visibility_of_element_located((by, sel))
            )
            break
        except Exception:
            continue

    if not field:
        print("[MVA][ERROR] input field not found")
        return None

    # Clear and type the MVA (auto-search on 8+ digits)
    field.click()
    time.sleep(0.2)
    try:
        field.clear()
    except Exception:
        # some inputs don't support clear(); fallback to Ctrl+A then type
        try:
            field.send_keys("\ue009" "a")  # CTRL + A
        except Exception:
            pass

    for ch in str(mva):
        field.send_keys(ch)
        time.sleep(0.05)

    # Wait for the echoed MVA in the vehicle pane (success signal)
    # Use label "MVA" row and compare by last 8 digits to tolerate leading zeros
    last8 = str(mva)[-8:]
    try:
        xp_by_label = (
            "//div[contains(@class,'vehicle-properties-container')]"
            "//div[contains(@class,'vehicle-property__')]"
            "[div[contains(@class,'vehicle-property-name')][normalize-space()='MVA']]"
            "/div[contains(@class,'vehicle-property-value')][contains(normalize-space(), '" + last8 + "')]"
        )
        elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xp_by_label))
        )
    except Exception:
        # Fallback: any properties value cell that contains our last 8
        try:
            xp_any_value_contains = (
                "//div[contains(@class,'vehicle-properties-container')]"
                "//div[contains(@class,'vehicle-property-value')][contains(normalize-space(), '" + last8 + "')]"
            )
            elem = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xp_any_value_contains))
            )
        except Exception:
            print(f"[MVA][ERROR] echoed value not found (looked for last8='{last8}')")
            return None

    time.sleep(0.6)  # allow UI to settle
    print(f"[MVA] Verification passed — {mva} echoed in vehicle pane")
    return elem


# Load config
with open(r"C:\temp\Python\config\config.json", "r") as f:
    cfg = json.load(f)
USERNAME = cfg.get("username")
PASSWORD = cfg.get("password")
LOGIN_ID = cfg.get("login_id")

from pages.drivability_page import DrivabilityPage

@pytest.mark.smoke
def test_mva_complaints_tab():
    print("Starting test_mva_complaints_tab...")
    # Initialize the driver
    driver = driver_manager.get_or_create_driver()
    print(f"Driver initialized: {driver}")
    try:
        print("Navigating to the login page...")
        login_page = LoginPage(driver)
        print("Login page initialized.")
        # Ensures login + clicks "Compass Mobile" + waits for WWID UI
        login_page.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)
        login_page.enter_wwid(LOGIN_ID)
        time.sleep(0.5)  # brief settle

        # Load MVAs
        mvas = load_mvas(r"C:\temp\Python\data\mva.csv")
        assert mvas, "Expected at least one MVA in CSV"

        for mva in mvas:
            print(f"[MVA] start → {mva}")
            hit = _enter_mva_and_wait_for_hit(driver, mva)
            assert hit is not None, f"Expected to find a matching vehicle tile for MVA {mva}"

            # 1) Open Work Items tab
            time.sleep(2)  # allow UI to settle
            click_work_items(driver)
            time.sleep(2)  # allow UI to settle

            # 2) Collect items and optionally debug if empty
            items = get_work_items(driver)
            if not items:
                try:
                    debug_list_work_items(driver)
                except Exception:
                    pass
            if has_complete_of_type(items, "PM"):
                print(f"[WORKITEM] {mva} — PM work item already completed; skipping MVA")
                print(f"[MVA] completed → {mva}")
                continue
            else:
                if has_complete_of_type(items, "PM"):
                    print(f"[WORKITEM] {mva} — PM work item already completed; skipping MVA")
                    print(f"[MVA] completed → {mva}")
                    continue

                print(f"[WORKITEM] {mva} — found {len(items)} work items")


                # 3) If an OPEN PM exists, use it: open → mark complete → Done
                if has_open_of_type(items, "PM"):
                    print(f"[WORKITEM] {mva} — PM work item already exists; opening to process")
                    continue


                print(f"[WORKITEM] {mva} — found {len(items)} work items")
            #debug_list_work_items(driver)

            # 3) If an OPEN PM exists → process; otherwise create a new PM
            if has_open_of_type(items, "PM"):
                print(f"[WORKITEM] {mva} — PM work item already exists; opening to process")
                if open_pm_workitem_card(driver, timeout=8):
                    if mark_complete_pm_workitem(driver, note="Done", timeout=10):
                        click_done(driver, timeout=8)
                        print(f"[MVA] completed → {mva}")
                    else:
                        print(f"[WORKITEM][WARN] {mva} — failed to mark complete")
                else:
                    print(f"[WORKITEM][WARN] {mva} — could not open existing PM work item")
                continue
            else:
                print(f"[WORKITEM] {mva} — no PM found; creating one")
                res = create_pm_workitem(driver, mva) or {"status": "failed", "reason": "helper_returned_none"}
                if res.get("status") != "created":
                    print(f"[WORKITEM][WARN] {mva} — create failed → {res.get('reason')}")
                    continue

                print(f"[MVA] completed → {mva}")
                continue


            # 4) No OPEN PM → run the built-in flow (it clicks Add Work Item and walks the dialog)
            time.sleep(2)  # allow UI to settle
            result = process_pm_workitem_flow(driver)
            print(f"[WORKITEM] {mva} → {result}")
            print(f"[MVA] completed → {mva}")
            continue  # skip the rest of this loop iteration


            # 5) Add complaint to the Work Item (best-effort)
            try:
                time.sleep(2)  # allow UI to settle
                click_add_new_complaint_button(driver, timeout=8)
                print(f"[COMPLAINT] {mva} — Add New Complaint clicked")
            except Exception as e:
                print(f"[COMPLAINT][WARN] {mva} — Add New Complaint not available ({e}); continuing")

            # after Add Complaint → open Drivability
            from pages.drivability_page import DrivabilityPage
            drv = DrivabilityPage(driver)

            from selenium.webdriver.common.by import By

            # **DEBUG CODE
            # INSERT BEFORE drv.ensure_open()
            from selenium.common.exceptions import NoSuchElementException
            try:
                driver.find_element(By.XPATH, "//h1[normalize-space()='Is vehicle drivable?']")
                print("[DEBUG] Drivability heading found at top level")
            except NoSuchElementException:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                print(f"[DEBUG] iframe count: {len(iframes)}")
                found = False
                for idx, fr in enumerate(iframes[:5]):  # keep it minimal
                    driver.switch_to.frame(fr)
                    try:
                        from selenium.webdriver.common.by import By
                        from selenium.common.exceptions import NoSuchElementException
                        driver.find_element(By.XPATH, "//h1[normalize-space()='Is vehicle drivable?']")
                        print(f"[DEBUG] Found Drivability heading in iframe[{idx}]")
                        found = True
                        break
                    except NoSuchElementException:
                        pass
                    finally:
                        driver.switch_to.default_content()
                if not found:
                    print("[DEBUG] Drivability heading not found in any tested iframe")

            # *********************END DEBUG CODE

            #input("Press Enter to continue or Ctrl+C to abort...")


            from selenium.webdriver.common.by import By

            drv.ensure_open()

            print(f"[COMPLAINT] {mva} — Drivability dialog opened")

            # >>> INSERT PROBE BLOCK HERE (keep 4-space indents) >>>
            from pages.drivability_page import DrivabilityPage
            from selenium.webdriver.common.by import By

            print("[PROBE] YES_BTN hits:", len(driver.find_elements(*DrivabilityPage.S.YES_BTN)))
            print("[PROBE] NO_BTN  hits:", len(driver.find_elements(*DrivabilityPage.S.NO_BTN)))
            print("[PROBE] GT YES hits:", len(driver.find_elements(
                By.XPATH, "//div[contains(@class,'drivable-options-container')]//button[.//h1[normalize-space()='Yes']]"
            )))
            print("[PROBE] GT NO  hits:", len(driver.find_elements(
                By.XPATH, "//div[contains(@class,'drivable-options-container')]//button[.//h1[normalize-space()='No']]"
            )))







            print(f"[COMPLAINT] {mva} — Drivability dialog opened")
            drv.select_drivable(True)
            print(f"[COMPLAINT] {mva} — Drivability set to 'Yes' (drivable)")

            # Click Next only if we're still on Drivability (app may auto-advance)
            from pages.drivability_page import DrivabilityPage  # if not already imported here
            if driver.find_elements(*DrivabilityPage.S.NEXT_BTN):
                drv.click_next()

            time.sleep(1)

            # PROBE — Complaint Type tiles and Next
            from selenium.webdriver.common.by import By


            # Probe for "PM"
            pm_tiles = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'damage-option-button')]//h1[normalize-space()='PM']"
            )
            print(f"[PROBE] Found {len(pm_tiles)} PM tile(s)")

            # Probe for "PM Hard Hold - PM"
            pmhh_tiles = driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'damage-option-button')]//h1[normalize-space()='PM Hard Hold - PM']"
            )
            print(f"[PROBE] Found {len(pmhh_tiles)} PM Hard Hold - PM tile(s)")

            # Probe for "Next"
            next_buttons = driver.find_elements(
                By.XPATH,
                "//button[.//span[normalize-space()='Next'] or normalize-space()='Next']"
            )
            print(f"[PROBE] Found {len(next_buttons)} Next button(s)")





            input("Press Enter to continue or Ctrl+C to abort...")








            # 8) Complaint Type page — select PM tile (auto-forwards)
            from pages.complaint_type_page import ComplaintTypePage
            ComplaintTypePage(driver).select_pm_tile(mva)




            # 9) Submit complaint (simple)
            input("Now we submit the complaint. Press Enter to continue or Ctrl+C to abort...  ")

            if click_button(driver, text="Submit Complaint", timeout=6):
                print(f"[COMPLAINT] {mva} — Submit button clicked")
            else:
                print(f"[COMPLAINT][WARN] {mva} — Submit button not found; continuing")
            continue


            # 10) Opcode dialog — instantiate helper
            opcode = OpcodeDialog(driver)
            assert opcode.select_opcode("PM"), "[OPCODE] 'PM' not found"
            assert opcode.click_create_button(), "[OPCODE] 'Create Work Item' button not found"
            print(f"[COMPLAINT] {mva} — Op code 'PM Gas' selected")
            time.sleep(2)  # allow UI to settle

            # 11) Opcode dialog — select "PM Gas", then click Create
            try:
                pm_gas = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[contains(@class,'opCodeText')][normalize-space()='PM Gas']"
                    ))
                )
                assert opcode.click_create_button(), "[OPCODE] 'Create Work Item' button not found"

                print(f"[COMPLAINT] {mva} — Op code 'PM Gas' selected")
            except Exception as e:
                print(f"[COMPLAINT][WARN] {mva} — Op code 'PM Gas' not found ({e}); continuing")


            # 12) Create Work Item
            if click_button(driver, text="Create Work Item", timeout=6):
                print(f"[COMPLAINT] {mva} — 'Create Work Item' clicked")
            else:
                print(f"[COMPLAINT][WARN] {mva} — 'Create Work Item' not found; continuing")

            # 13) Open the new PM work item (click the record header)
            try:
                header = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//div[contains(@class,'scan-record__')][.//div[contains(@class,'scan-record-header-title__')][normalize-space()='PM']]//div[contains(@class,'scan-record-header__')][1]"
                    ))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", header)
                time.sleep(0.5)  # allow UI to settle
                header.click()
                time.sleep(1)  # allow UI to settle
                print(f"[WORKITEM] {mva} — PM record header clicked")
            except Exception as e:
                print(f"[WORKITEM][WARN] {mva} — PM record header not clickable ({e}); continuing")

            # 14) Mark Complete
            clicked = click_button(driver, text="Mark Complete", timeout=8)
            time.sleep(2)
            if not clicked:
                # fallback to class if the button text isn't reliably matched
                clicked = click_button(
                    driver,
                    css_class="fleet-operations-pwa__mark-complete-button__spuz8c",
                    timeout=6,
                )

            if clicked:
                print(f"[WORKITEM] {mva} — 'Mark Complete' clicked")
            else:
                print(f"[WORKITEM][WARN] {mva} — 'Mark Complete' not found; continuing")


            # 15) Enter correction and finish
            try:
                # textarea inside the confirmation dialog
                box = WebDriverWait(driver, 8).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.bp6-text-area"))
                )
                box.clear()
                box.send_keys("Done")
                time.sleep(2.5)  # allow UI to settle
                print(f"[WORKITEM] {mva} — typed 'Done' in textarea")
            except Exception as e:
                print(f"[WORKITEM][WARN] {mva} — textarea not found ({e}); continuing")

            # Click "Complete Work Item"
            clicked = click_button(driver, text="Complete Work Item", timeout=8)
            time.sleep(2)
            if not clicked:
                clicked = click_button(
                    driver,
                    css_class="fleet-operations-pwa__submit-button__1x8octw",
                    timeout=6,
                )

            if clicked:
                print(f"[WORKITEM] {mva} — 'Complete Work Item' clicked")
                continue
            else:
                print(f"[WORKITEM][WARN] {mva} — 'Complete Work Item' not found; continuing")
                continue







    finally:
        time.sleep(10)
