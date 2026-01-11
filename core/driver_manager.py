import logging
import os
import re
import subprocess
import winreg

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.edge.service import Service

try:
    # Optional dependency: enables automatic driver download + caching.
    from webdriver_manager.microsoft import EdgeChromiumDriverManager  # type: ignore
except Exception:  # pragma: no cover
    EdgeChromiumDriverManager = None


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_DRIVER_PATH = os.path.join(PROJECT_ROOT, "msedgedriver.exe")

log = logging.getLogger("mc.automation")

_driver = None  # singleton instance






def get_browser_version() -> str:
    """Return installed Edge browser version from Windows registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Edge\BLBeacon")
        value, _ = winreg.QueryValueEx(key, "version")
        return value
    except Exception as e:
        print(f"Error: {e}")
        return "unknown"










def get_driver_version(driver_path: str) -> str:
    """Return Edge WebDriver version (e.g., 140.0.x.x)."""
    if not os.path.exists(driver_path):
        log.warning(f"[DRIVER] Driver binary not found at {driver_path}")
        return "unknown"
    try:
        output = subprocess.check_output([driver_path, "--version"], text=True)
        return re.search(r"(\d+\.\d+\.\d+\.\d+)", output).group(1)
    except Exception as e:
        log.error(f"[DRIVER] Failed to get driver version from {driver_path} - {e}")
        return "unknown"


def _build_edge_options() -> webdriver.EdgeOptions:
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option(
        "prefs",
        {"profile.default_content_setting_values.geolocation": 2},
    )
    return options


def _resolve_driver_path() -> tuple[str, str]:
    """Return (driver_path, source) where source is 'webdriver-manager' or 'local'."""
    if EdgeChromiumDriverManager is not None:
        try:
            path = EdgeChromiumDriverManager().install()
            return path, "webdriver-manager"
        except Exception as e:
            log.warning(f"[DRIVER] webdriver-manager failed; falling back to local driver if present -> {e}")

    if os.path.exists(LOCAL_DRIVER_PATH):
        return LOCAL_DRIVER_PATH, "local"

    raise RuntimeError(
        "No Edge WebDriver available. Install 'webdriver-manager' (recommended) "
        "or place 'msedgedriver.exe' in the project root."
    )


def get_or_create_driver():
    """Return singleton Edge WebDriver, creating it if needed."""
    global _driver
    if _driver:
        return _driver

    browser_ver = get_browser_version()
    driver_path, source = _resolve_driver_path()
    driver_ver = get_driver_version(driver_path)
    log.info(f"[DRIVER] Using {source} driver at {driver_path}")
    log.info(f"[DRIVER] Detected Browser={browser_ver}, Driver={driver_ver}")

    # Preserve the old strict mismatch check only for the repo-local driver.
    # When using webdriver-manager, let Selenium/Edge decide compatibility.
    if source == "local" and browser_ver != "unknown" and driver_ver != "unknown":
        if browser_ver.split(".")[0] != driver_ver.split(".")[0]:
            log.error(f"[DRIVER] Version mismatch - Browser {browser_ver}, Driver {driver_ver}")
            raise RuntimeError("Edge/Driver version mismatch")

    try:
        log.info(f"[DRIVER] Launching Edge - Browser {browser_ver}, Driver {driver_ver}")
        options = _build_edge_options()
        service = Service(driver_path)
        _driver = webdriver.Edge(service=service, options=options)
        return _driver
    except SessionNotCreatedException as e:
        log.error(f"[DRIVER] Session creation failed: {e}")
        raise


def quit_driver():
    """Quit and reset the singleton driver."""
    global _driver
    if _driver:
        log.info("[DRIVER] Quitting Edge WebDriver...")
        _driver.quit()
        _driver = None
