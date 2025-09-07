import atexit

from selenium import webdriver
from selenium.webdriver import EdgeOptions

from utils.logger import log

_driver = None


# ---------- Driver manager ----------
def get_or_create_driver():
    """Return the singleton Edge WebDriver instance (create if missing)."""
    global _driver
    if _driver is None:
        log.info("[DRIVER] Initializing Edge WebDriver...")

        options = EdgeOptions()
        options.use_chromium = True

        prefs = {"profile.default_content_setting_values.geolocation": 2}
        options.add_argument("--inprivate")
        options.add_argument("--start-maximized")
        options.add_argument("--log-level=3")
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        _driver = webdriver.Edge(options=options)
        log.debug("[DRIVER] Edge WebDriver started (InPrivate, maximized")

    return _driver


def quit_driver():
    """Quit the singleton Edge WebDriver instance if running."""
    global _driver
    if _driver is not None:
        log.debug("[DRIVER] Quitting Edge WebDriver...")
        try:
            _driver.quit()
        except Exception as e:
            log.error(f"[DRIVER] Error during quit: {e}")
        finally:
            _driver = None


# ---------- Teardown hook ----------
atexit.register(quit_driver)
