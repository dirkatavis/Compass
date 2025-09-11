import subprocess
import re
import os
import logging
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.edge.service import Service


# Logger
log = logging.getLogger("mc.automation")

_driver = None  # singleton instance





import winreg

def get_browser_version() -> str:
    """Return installed Edge browser version from Windows registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Edge\BLBeacon")
        value, _ = winreg.QueryValueEx(key, "version")
        return value
    except Exception as e:
        print(f"Error: {e}")
        return "unknown"
if __name__ == "__main__":
    print("Edge Browser Version:", get_browser_version())










def get_driver_version(driver_path: str) -> str:
    """Return Edge WebDriver version (e.g., 140.0.x.x)."""
    if not os.path.exists(driver_path):
        log.error(f"[DRIVER] Driver binary not found at {driver_path}")
        return "unknown"
    try:
        output = subprocess.check_output([driver_path, "--version"], text=True)
        return re.search(r"(\d+\.\d+\.\d+\.\d+)", output).group(1)
    except Exception as e:
        log.error(f"[DRIVER] Failed to get driver version from {driver_path} → {e}")
        return "unknown"


def get_or_create_driver():
    """Return singleton Edge WebDriver, creating it if needed."""
    global _driver
    if _driver:
        return _driver

    driver_path = r"C:\temp\Python\msedgedriver.exe"
    browser_ver = get_browser_version()
    driver_ver = get_driver_version(driver_path)

    # Always log detected versions
    log.info(f"[DRIVER] Detected Browser={browser_ver}, Driver={driver_ver}")

    # Compare before launching browser
    if browser_ver.split(".")[0] != driver_ver.split(".")[0]:
        log.error(f"[DRIVER] Version mismatch → Browser {browser_ver}, Driver {driver_ver}")
        raise RuntimeError("Edge/Driver version mismatch")

    try:
        log.info(f"[DRIVER] Launching Edge → Browser {browser_ver}, Driver {driver_ver}")
        options = webdriver.EdgeOptions()
        options.add_argument("--inprivate")
        options.add_argument("--start-maximized")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 2 }) 
        service = Service(r"C:\temp\Python\msedgedriver.exe")
        _driver = webdriver.Edge(service=service, options=options)
         #_driver = webdriver.Edge(driver_path, options=options)
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
