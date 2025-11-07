from core import driver_manager
from pages.login_page import LoginPage
from config.config_loader import get_config
from flows import work_item_flow
import csv
import os
from utils.logger import log

def load_mvas(path="data/mva.csv"):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return [row[0] for row in csv.reader(f) if row]

from flows.LoginFlow import LoginFlow

def main():
    print("Starting Compass automation...")

    driver = driver_manager.get_or_create_driver()
    login_flow = LoginFlow(driver)
    login_flow.login_handler(
        get_config("username"),
        get_config("password"),
        get_config("login_id"),
    )

    mvas = load_mvas()
    for mva in mvas:
        # Call handle_pm_workitems and check its status
        result = work_item_flow.handle_pm_workitems(driver, mva)
        if result.get("status") == "skipped_lighthouse_rentable":
            log.info(f"[MVA] {mva} - Skipped due to 'Rentable' Lighthouse status.")
        # You might want to add other status checks here as well
        # else:
        #     log.info(f"[MVA] {mva} - Processing complete with status: {result.get('status')}")

    print("Automation run complete.")

if __name__ == "__main__":
    main()
