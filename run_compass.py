import os
import time

from selenium.webdriver.common.by import By

from config.config_loader import get_config
from core import driver_manager
from flows import work_item_flow
from flows.LoginFlow import LoginFlow
from pages.mva_input_page import MVAInputPage
from utils.data_loader import load_mvas
from utils.logger import log
from utils.ui_helpers import is_mva_known, navigate_back_to_home

def main():
    print("Starting Compass automation...")

    driver = driver_manager.get_or_create_driver()
    login_flow = LoginFlow(driver)

    username = get_config("username")
    password = get_config("password")
    login_id = get_config("login_id")

    login_result = login_flow.login_handler(
        username,
        password,
        login_id,
    )
    if login_result.get("status") != "ok":
        log.error(f"[LOGIN] Failed to initialize session → {login_result}")
        return

    settle_delay = get_config("delay_seconds", default=2)
    entry_delay = get_config("mva_entry_delay_seconds", default=5)
    time.sleep(settle_delay)

    camera_selector = (By.XPATH, "//button[contains(@class,'fleet-operations-pwa__camera-button')]")

    def ensure_home_ready() -> bool:
        """Make sure the Compass Mobile landing screen is active."""
        if driver.find_elements(*camera_selector):
            return True
        if navigate_back_to_home(driver):
            return True

        log.warning("[NAV] Back navigation failed, rerunning login flow to recover home screen")
        retry = login_flow.login_handler(username, password, login_id)
        if retry.get("status") != "ok":
            log.error(f"[NAV] Login retry failed → {retry}")
            return False
        time.sleep(settle_delay)
        return bool(driver.find_elements(*camera_selector))

    project_root = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(project_root, "data", "mva.csv")
    mvas = load_mvas(csv_path)
    if not mvas:
        log.warning(f"[MVA] No MVA values found in {csv_path}")
        return

    mva_page = MVAInputPage(driver)

    for mva in mvas:
        log.info("=" * 80)
        log.info(f">>> Starting MVA {mva}")
        log.info("=" * 80)

        if not ensure_home_ready():
            log.error(f"[NAV] Unable to reach home screen before MVA {mva}; aborting run")
            break

        field = mva_page.find_input()
        if not field:
            log.error(f"[MVA] {mva} — input field not found; skipping")
            continue

        field.clear()
        field.send_keys(mva)
        time.sleep(entry_delay)

        if not is_mva_known(driver, mva):
            log.warning(f"[MVA] {mva} — invalid/unknown, skipping")
            continue

        result = work_item_flow.handle_pm_workitems(driver, mva)
        status = result.get("status")

        if status in {"ok", "closed", "created"}:
            log.info(f"[WORKITEM] {mva} — flow completed successfully ({status})")
        elif status == "skipped_no_complaint":
            log.info(f"[WORKITEM] {mva} — navigating back home after skip")
            navigate_back_to_home(driver)
            time.sleep(5)
        elif status == "skipped_lighthouse_rentable":
            log.info(f"[WORKITEM] {mva} — skipped due to Lighthouse status 'Rentable'")
        elif status == "skipped_cdk_pm":
            log.info(f"[WORKITEM] {mva} — PM must be closed in CDK; returning home")
            navigate_back_to_home(driver)
            time.sleep(5)
        else:
            log.warning(f"[WORKITEM] {mva} — unexpected status {status}: {result}")

    print("Automation run complete.")

if __name__ == "__main__":
    main()
