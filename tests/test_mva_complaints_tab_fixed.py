import time
import pytest

from core import driver_manager
from pages.login_page import LoginPage
from pages.mva_input_page import MVAInputPage
from utils.data_loader import load_mvas
from flows.work_item_flow import process_workitem
from config.config_loader import get_config

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
    print(f"Driver initialized: {driver}")

    # Perform login
    login_page = LoginPage(driver)
    login_page.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)
    login_page.enter_wwid(LOGIN_ID)
    time.sleep(DELAY)  # configurable settle

    # Load MVAs from CSV
    mvas = load_mvas(r"C:\temp\Python\data\mva.csv")
    assert mvas, "Expected at least one MVA in CSV"

    # Loop through MVAs
    for mva in mvas:
        print(f"[MVA] start → {mva}")

        # Enter the MVA into the input field
        mva_page = MVAInputPage(driver)
        field = mva_page.find_input()
        field.clear()
        field.send_keys(mva)
        time.sleep(DELAY)  # configurable settle

        # Process the work item flow
        res = process_workitem(driver, mva)

        if res.get("status") == "created":
            print(f"[MVA] completed → {mva}")
        elif res.get("status") == "skipped":
            print(f"[MVA] skipped → {mva} (already has open PM)")
        else:
            print(f"[WORKITEM][WARN] {mva} — failed → {res.get('reason')}")
            continue

    print("[FIXTURE] All tests complete — quitting singleton driver...")
