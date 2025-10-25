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

# Load config values
USERNAME = get_config("username")
PASSWORD = get_config("password")
LOGIN_ID = get_config("login_id")
DELAY = get_config("delay_seconds", default=2)


@pytest.mark.smoke
def test_mva_complaints_tab():
    print("Starting test_mva_complaints_tab...")

    # Initialize driver
    driver = driver_manager.get_or_create_driver()
    log.info(f"Driver initialized: {driver}")

    # Perform login
    login_page = LoginPage(driver)
    res = login_page.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)
    if res["status"] != "ok":
        pytest.skip(f"Login failed → {res}")
    time.sleep(DELAY)  # configurable settle

    # Load MVAs from CSV
    mvas = load_mvas(r"C:\temp\Python\data\mva.csv")
    assert mvas, "Expected at least one MVA in CSV"

    # Loop through MVAs
    for mva in mvas:
        log.critical("")
        log.critical("")
        log.critical("=" * 80)
        log.critical(f">>> Starting MVA {mva}")
        log.critical("=" * 80)

        # Enter the MVA into the input field
        mva_page = MVAInputPage(driver)
        field = mva_page.find_input()
        if not field:
            res = {"status": "failed", "reason": "mva_input_not_found"}
            log.error(f"[MVA] {mva} — input field not found")
            assert res["status"] == "ok", f"Flow failed: {res}"

        field.clear()
        field.send_keys(mva)

        # Handle PM Work Items in one call
        from flows.work_item_flow import handle_pm_workitems
        res = handle_pm_workitems(driver, mva)

        if res.get("status") in ("ok", "closed"):
            log.critical(f"[WORKITEM] {mva} — flow completed successfully")
        elif res.get("status") == "skipped_no_complaint":
            log.critical(f"[WORKITEM] {mva} — navigating back home after skip")
            navigate_back_to_home(driver)
            time.sleep(5)
        else:
            log.critical(f"[WORKITEM] {mva} — failed flow: {res}")
    print("[FIXTURE] All tests complete - quitting singleton driver...")



