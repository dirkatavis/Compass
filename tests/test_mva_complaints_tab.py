import json
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core import driver_manager
#from pages.login_page import LoginPage
from pages.login_page import LoginPage
from utils.data_loader import load_mvas
from utils.ui_helpers import click_button
from utils.mva_helpers import click_add_new_complaint_button
from utils.ui_helpers import (
    click_work_items,
    get_work_items,
    has_open_of_type,
    has_complete_of_type,
    process_pm_workitem_flow,
    debug_list_work_items,
)

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


@pytest.mark.smoke
def test_mva_complaints_tab():
    driver = driver_manager.get_or_create_driver()
    try:
        login_page = LoginPage(driver)
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
                print(f"[WORKITEM] {mva} — found {len(items)} work items")
                input("Press Enter to continue or Ctrl+C to abort...")
            #debug_list_work_items(driver)

            # 3) If an OPEN PM exists, skip creation
            if has_open_of_type(items, "PM"):
                print(f"[WORKITEM] {mva} — PM work item already exists; skipping create")
                print(f"[MVA] completed → {mva}")
                continue

            # 4) No OPEN PM → run the built-in flow (it clicks Add Work Item and walks the dialog)
            time.sleep(2)  # allow UI to settle
            result = process_pm_workitem_flow(driver)
            print(f"[WORKITEM] {mva} → {result}")
            print(f"[MVA] completed → {mva}")


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
            drv.ensure_open()
            drv.select_drivable(True)  # or False
            drv.click_next()           # proceeds to ComplaintTypePage


                # 8) Select complaint type → PM (auto-advances)
            try:
                # Wait for complaint-type options to render (container or any known option text)
                WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//*[contains(@class,'damage-options') or contains(., 'Mechanical Issue') or contains(., 'Tire Damage') or contains(., 'Glass Damage') or contains(., 'Keys') or .//h1[normalize-space()='PM']]"
                    ))
                )
                # Try common labels first
                clicked = (
                    click_button(driver, text="PM", timeout=4)
                    or click_button(driver, text="Preventive Maintenance", timeout=3)
                )
                # Fallback to a robust XPath match on the PM tile
                if not clicked:
                    pm_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//button[contains(@class,'damage-option') or contains(@class,'damage-options')]"
                            "[.//h1[normalize-space()='PM'] or .//span[normalize-space()='PM'] or normalize-space()='PM']"
                        ))
                    )
                    # Scroll just in case, then click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pm_btn)
                    pm_btn.click()
                    clicked = True

                print(f"[COMPLAINT] {mva} — Complaint type 'PM' selected")
            except Exception as e:
                print(f"[COMPLAINT][WARN] {mva} — 'PM' complaint button not available ({e}); continuing")

            # 9) Wait for the PM complaint tile to appear
            # 9) Submit complaint (simple)
            time.sleep(2) # Allow UI to settle
            if click_button(driver, text="Submit Complaint", timeout=6):
                print(f"[COMPLAINT] {mva} — Submit button clicked")
            else:
                print(f"[COMPLAINT][WARN] {mva} — Submit button not found; continuing")


            # 10) Next screen
            if click_button(driver, text="Next", timeout=6):
                print(f"[COMPLAINT] {mva} — Next clicked")
            else:
                print(f"[COMPLAINT][WARN] {mva} — Next button not found; continuing")

            time.sleep(2)  # allow UI to settle

            # 11) Select op code: PM Gas
            try:
                pm_gas = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[contains(@class,'opCodeText')][normalize-space()='PM Gas']"
                    ))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pm_gas)
                pm_gas.click()
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
            else:
                print(f"[WORKITEM][WARN] {mva} — 'Complete Work Item' not found; continuing")







    finally:
        time.sleep(10)
