import os
import time

from selenium.webdriver.common.by import By

import os
import time

from selenium.webdriver.common.by import By

from core import driver_manager
from utils.logger import log, log_session_header


LANDING_URL = (
    "https://avisbudget.palantirfoundry.com/workspace/module/view/latest/"
    "ri.workshop.main.module.d62ba12c-018c-41c1-8214-0749f6591b30"
)

# Full explicit XPath provided by user
FULL_XPATH = (
    "/html/body/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/"
    "div[3]/div/div/div/div/div/div/span/div/div/span[2]/span/a"
)


def _dump_artifacts(driver, label: str):
    ts = time.strftime("%Y%m%d-%H%M%S")
    artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    png = os.path.join(artifacts_dir, f"{ts}_{label}.png")
    html = os.path.join(artifacts_dir, f"{ts}_{label}.html")
    try:
        driver.save_screenshot(png)
        log.info(f"Saved screenshot: {png}")
    except Exception as e:
        log.warning(f"Could not save screenshot: {e}")
    try:
        with open(html, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log.info(f"Saved page source: {html}")
    except Exception as e:
        log.warning(f"Could not save page source: {e}")


def main():
    # Log professional session header with date
    log_session_header()
    
    log.info(f"Opening landing page: {LANDING_URL}")
    driver = driver_manager.get_or_create_driver()
    driver.get(LANDING_URL)

    # Hard wait as requested
    log.info("Hard waiting 10s for page to stabilize before clicking")
    time.sleep(10)

    try:
        el = driver.find_element(By.XPATH, FULL_XPATH)
    except Exception:
        log.exception("Supply Chain element not found with full XPath")
        _dump_artifacts(driver, label="supply_chain_not_found_fullxpath")
        return

    try:
        el.click()
        log.info("Clicked Supply Chain element via direct click")
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", el)
            log.info("Clicked Supply Chain element via JS click")
        except Exception:
            log.exception("Failed to click Supply Chain element with both direct and JS click")
            _dump_artifacts(driver, label="supply_chain_click_failed_fullxpath")


if __name__ == "__main__":
    main()
