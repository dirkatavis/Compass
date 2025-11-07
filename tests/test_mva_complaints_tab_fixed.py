import time

import pytest
from selenium.webdriver.common.by import By
from config.config_loader import get_config
from core import driver_manager
from flows.work_item_flow import process_workitem
from pages.login_page import LoginPage
from pages.mva_input_page import MVAInputPage
from utils.data_loader import load_mvas
from utils.logger import log
from utils.ui_helpers import navigate_back_to_home, is_mva_known
from flows.LoginFlow import LoginFlow

# Load config values
USERNAME = get_config("username")
PASSWORD = get_config("password")
LOGIN_ID = get_config("login_id")
DELAY = get_config("delay_seconds", default=2)
MVA_ENTRY_DELAY = get_config("mva_entry_delay_seconds", default=5)


@pytest.mark.smoke
def test_mva_complaints_tab():
    print("Starting test_mva_complaints_tab...")

    # Initialize driver
    driver = driver_manager.get_or_create_driver()
    log.info(f"Driver initialized: {driver}")

    # Perform login
    login_flow = LoginFlow(driver)
    res = login_flow.login_handler(USERNAME, PASSWORD, LOGIN_ID)
    if res["status"] != "ok":
        pytest.skip(f"Login failed → {res}")
    time.sleep(DELAY)  # configurable settle

    # Load MVAs from CSV (relative to project root)
    import os
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mva.csv")
    mvas = load_mvas(csv_path)
    assert mvas, "Expected at least one MVA in CSV"

    # Loop through MVAs
    for mva in mvas:
        log.info("=" * 80)
        log.info(f">>> Starting MVA {mva}")
        log.info("=" * 80)

              # Enter the MVA into the input field
        mva_page = MVAInputPage(driver)
        field = mva_page.find_input()
        if not field:
            res = {"status": "failed", "reason": "mva_input_not_found"}
            log.error(f"[MVA] {mva} — input field not found")
            assert res["status"] == "ok", f"Flow failed: {res}"

        field.clear()
        field.send_keys(mva)
        time.sleep(MVA_ENTRY_DELAY)

        from utils.ui_helpers import is_mva_known
        if not is_mva_known(driver, mva):
            log.warning(f"[MVA] {mva} — invalid/unknown MVA, skipping")
            continue

        # Handle PM Work Items in one call
        from flows.work_item_flow import handle_pm_workitems
        res = handle_pm_workitems(driver, mva)

        if res.get("status") in ("ok", "closed"):
            log.info(f"[WORKITEM] {mva} — flow completed successfully")
        elif res.get("status") == "skipped_no_complaint":
            log.info(f"[WORKITEM] {mva} — navigating back home after skip")
            navigate_back_to_home(driver)
            time.sleep(5)
        else:
            log.warning(f"[WORKITEM] {mva} — failed flow: {res}")

        continue
    print("[FIXTURE] All tests complete - quitting singleton driver...")



