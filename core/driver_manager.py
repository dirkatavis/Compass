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
    # Candidate driver locations to try (primary working path + repo vendored path)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidate_paths = [
        r"C:\temp\Python\msedgedriver.exe",
        os.path.join(repo_root, "msedgedriver.exe"),
        os.path.join(repo_root, "v141.0.3537.57", "edgedriver_win64", "msedgedriver.exe"),
    ]

    selected_driver = None
    driver_ver = "unknown"
    for p in candidate_paths:
        if os.path.exists(p):
            selected_driver = p
            driver_ver = get_driver_version(p)
            log.debug(f"[DRIVER] Found candidate driver at {p} → {driver_ver}")
            break

    if not selected_driver:
        log.error(
            "[DRIVER] No Edge WebDriver binary found. Tried: %s",
            ", ".join(candidate_paths),
        )
        raise RuntimeError(
            "Edge WebDriver not found. Place msedgedriver.exe at one of the candidate paths or update driver_manager.")

    browser_ver = get_browser_version()
    # Always log detected versions
    log.info(f"[DRIVER] Detected Browser={browser_ver}, Driver={driver_ver}")

    # If both versions are known, enforce major-version match. If either is unknown, warn and continue.
    if browser_ver != "unknown" and driver_ver != "unknown":
        try:
            if browser_ver.split(".")[0] != driver_ver.split(".")[0]:
                log.error(f"[DRIVER] Version mismatch → Browser {browser_ver}, Driver {driver_ver}")
                raise RuntimeError("Edge/Driver version mismatch")
        except Exception:
            # Defensive: if split/parse fails, log and continue to allow debugging on machines where registry isn't standard
            log.warning("[DRIVER] Could not compare browser/driver versions precisely; proceeding with caution.")
    else:
        log.warning("[DRIVER] Browser or driver version unknown; skipping strict version check.")

    # Launch Edge using the selected driver
    try:
        log.info(f"[DRIVER] Launching Edge → Browser {browser_ver}, Driver {driver_ver}")
        options = webdriver.EdgeOptions()
        options.add_argument("--inprivate")
        options.add_argument("--start-maximized")
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 2})
        service = Service(selected_driver)
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
