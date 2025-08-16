# core/driver_manager.py
from typing import Optional
from selenium.common.exceptions import WebDriverException


import os
import logging

_logger = logging.getLogger("mc.driver")
if not _logger.handlers:
    level_name = os.getenv("MC_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    _logger.setLevel(level)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    _logger.addHandler(h)

def _dbg(msg: str):
    _logger.debug(msg)

def _info(msg: str):
    _logger.info(msg)






# ---- Verbose console logging controls ---------------------------------------
_VERBOSE = False  # set False to silence; or call set_verbose(False) at runtime

def set_verbose(enabled: bool):
    """Turn console tracing on/off at runtime."""
    global _VERBOSE
    _VERBOSE = bool(enabled)

def _log(msg: str):
    if _VERBOSE:
        print(f"[DRIVER_MANAGER] {msg}")

# ---- Singleton holder --------------------------------------------------------
_driver_singleton: Optional[object] = None


def is_alive(driver: Optional[object]) -> bool:
    """
    Check if the given driver/session is usable.
    We ping a lightweight property access to trigger a WebDriver round trip.
    """
    if driver is None:
        _log("is_alive: driver=None → False")
        return False
    try:
        _log("is_alive: probing driver.title …")
        _ = driver.title
        _log("is_alive: OK → True")
        return True
    except WebDriverException as e:
        _log(f"is_alive: WebDriverException → False ({e})")
        return False
    except Exception as e:
        _log(f"is_alive: Exception → False ({e})")
        return False


# core/driver_manager.py
# tabs, not spaces
def _create_new_driver():
    import os
    import subprocess

    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService

    _log("_create_new_driver: begin")

    options = webdriver.EdgeOptions()
    options.add_argument("--disable-geolocation")
    options.add_argument("--start-maximized")
    


    # Mobile emulation (optional)
    mobile_emulation = {
        "deviceMetrics": {"width": 720, "height": 1600, "pixelRatio": 3.0},
        "userAgent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
    }
    #options.add_experimental_option("mobileEmulation", mobile_emulation)





    # ↓ Reduce Chromium console noise
    options.add_argument("--log-level=3")  # 0=ALL, 3=ERROR
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # hides "DevTools listening..."

    # Prepare a quiet service that discards driver logs
    def _quiet_service(path: str | None = None):
        if path:
            return EdgeService(path, log_output=subprocess.DEVNULL)
        return EdgeService(log_output=subprocess.DEVNULL)

    local_driver = r"C:\temp\edgedriver_win64\msedgedriver.exe"
    if os.path.isfile(local_driver):
        _log(f"_create_new_driver: using LOCAL edgedriver → {local_driver}")
        driver = webdriver.Edge(service=_quiet_service(local_driver), options=options)
        driver = webdriver.Edge(service=_quiet_service(local_driver), options=options)
        #driver.set_window_size(720, 1700)  # keep in sync with deviceMetrics
    else:
        _log("_create_new_driver: local driver NOT found → using Selenium Manager")
        driver = webdriver.Edge(service=_quiet_service(), options=options)
        driver = webdriver.Edge(service=_quiet_service(local_driver), options=options)
        #driver.set_window_size(720, 1700)  # keep in sync with deviceMetrics

    # Snapshot a few details (safe-guarded)
    try:
        _log(f"_create_new_driver: session_id={getattr(driver, 'session_id', '<n/a>')}")
        _log(f"_create_new_driver: capabilities.browserName={driver.capabilities.get('browserName')}")
        _log(f"_create_new_driver: capabilities.browserVersion={driver.capabilities.get('browserVersion')}")
    except Exception as e:
        _log(f"_create_new_driver: (capabilities log skipped) {e}")

    _log("_create_new_driver: end")
    return driver



def get_or_create_driver():
    """
    Return the live singleton driver if available; otherwise create a new one.
    Prints a detailed decision trail to the console.
    """
    global _driver_singleton

    _log("get_or_create_driver: called")
    if is_alive(_driver_singleton):
        _log("get_or_create_driver: reusing existing driver")
        try:
            _log(f"→ session_id={_driver_singleton.session_id}")
            # Optional quick status:
            _try_log_status(_driver_singleton, label="reuse")
        except Exception:
            pass
        return _driver_singleton

    if _driver_singleton is not None:
        _log("get_or_create_driver: existing driver found but dead → quitting")
        try:
            _driver_singleton.quit()
            _log("get_or_create_driver: old driver quit OK")
        except Exception as e:
            _log(f"get_or_create_driver: quit raised (ignored): {e}")

    _log("get_or_create_driver: creating new driver")
    _driver_singleton = _create_new_driver()
    try:
        _log(f"→ NEW session_id={_driver_singleton.session_id}")
        _try_log_status(_driver_singleton, label="new")
    except Exception:
        pass
    return _driver_singleton


def get_driver():
    """Back-compat alias for get_or_create_driver()."""
    _log("get_driver: alias → get_or_create_driver()")
    return get_or_create_driver()


def quit_driver():
    """Quit and clear the singleton driver with console prints."""
    global _driver_singleton
    _log("quit_driver: called")
    try:
        if _driver_singleton is not None:
            sid = getattr(_driver_singleton, "session_id", "<n/a>")
            _log(f"quit_driver: quitting session_id={sid}")
            _driver_singleton.quit()
            _log("quit_driver: quit OK")
    finally:
        _driver_singleton = None
        _log("quit_driver: singleton cleared")


# ---- Optional: quick status dump (console only) ------------------------------
def _try_log_status(driver, label: str = ""):
    """
    Best-effort status snapshot to the console:
    - session_id
    - current_url (if available)
    - number of window handles
    - page title (truncated)
    Never raises; purely diagnostic.
    """
    try:
        sid = getattr(driver, "session_id", "<n/a>")
        url = "<n/a>"
        title = "<n/a>"
        handles = 0

        try:
            url = driver.current_url
        except Exception:
            pass
        try:
            title = driver.title
        except Exception:
            pass
        try:
            handles = len(driver.window_handles or [])
        except Exception:
            pass

        if len(title) > 120:
            title = title[:117] + "..."

        prefix = f"status[{label}]" if label else "status"
        _log(f"{prefix}: session_id={sid} windows={handles} url={url}")
        _log(f"{prefix}: title={title}")
    except Exception as e:
        _log(f"status: skipped due to exception: {e}")

