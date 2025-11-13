# utils/ui_helpers.py
import os
import time
from config.config_loader import DEFAULT_TIMEOUT
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.logger import log


def is_element_present(driver, locator: tuple, timeout: int = 5) -> bool:
    """
    Checks if an element is present on the page within the given timeout.
    Returns True if present, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return True
    except TimeoutException:
        return False


def safe_wait(driver, timeout, condition, desc="condition"):
    """Wait safely for a condition; return element/value or None on timeout."""
    try:
        return WebDriverWait(driver, timeout).until(condition)
    except TimeoutException:
        msg = f"[SAFE_WAIT] Timeout while waiting for {desc}"
        # For now: all waits are required, so fail
        raise AssertionError(msg)



def _click_tab(driver, data_tab_id: str, timeout: int = 10) -> bool:
    # Guard: any modal overlay gone
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".bp6-dialog[aria-modal='true']")
        )
    )

    # Find the tab by stable attribute
    tab = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"div.bp6-tab[data-tab-id='{data_tab_id}']")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab)
    time.sleep(0.2)
    log.debug(f"[TAB] Clicking tab with data-tab-id: {data_tab_id}")
    tab.click()

    # Verify it took (aria-selected flips to true)
    log.debug(f"[TAB] Verifying tab {data_tab_id} is active.")
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                f"div.bp6-tab[data-tab-id='{data_tab_id}'][aria-selected='true']",
            )
        )
    )
    return True


def click_work_items(driver, timeout: int = 10) -> bool:
    log.debug(f"[TAB] Attempting to click Work Items tab (timeout={timeout}s)")
    return _click_tab(driver, "workItems", timeout)


def click_complaints(driver, timeout: int = 10) -> bool:
    log.debug(f"[TAB] Attempting to click Complaints tab (timeout={timeout}s)")
    result = _click_tab(driver, "complaints", timeout)
    if result:
        log.debug("[TAB] Complaints tab clicked and verified as active")
    else:
        log.debug("[TAB] Complaints tab click may have failed")
    return result


def send_text(
    driver,
    locator: tuple,
    text: str,
    timeout: int = 10,
    clear: bool = True,
    label: str = "",
) -> bool:
    """
    Safely send text to a textbox with wait, optional clear, and validation.

    Args:
        driver: Selenium WebDriver instance
        locator: (By, value) tuple
        text: text to type
        timeout: max seconds to wait for element
        clear: whether to clear existing text first
        label: optional name for logging

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Wait until element is interactable
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    except TimeoutException:
        log.warning(f"[SENDTEXT] {label or locator} not found within {timeout}s")
        return False

    try:
        if clear:
            element.clear()
        element.send_keys(text)

        # Verify typed value
        typed_value = element.get_attribute("value")
        if typed_value != text:
            log.warning(
                f"[SENDTEXT] {label or locator} mismatch → expected '{text}', got '{typed_value}'"
            )
            return False

        log.debug(f"[SENDTEXT] Sent text to {label or locator}")
        return True

    except Exception as e:
        log.error(f"[SENDTEXT] Exception sending text to {label or locator}: {e}")
        return False


def get_complaints(driver, timeout: int = 10):
    """Return list of {'state': 'Open'|'Closed', 'type': 'PM'|...} from the visible Complaints tab."""
    log.debug(f"[COMPLAINTS] Getting complaints with timeout: {timeout}s")
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "div.bp6-tab-panel[id*='complaints'][aria-hidden='false']",
            )
        )
    )
    panel = driver.find_element(
        By.CSS_SELECTOR, "div.bp6-tab-panel[id*='complaints'][aria-hidden='false']"
    )
    tiles = panel.find_elements(
        By.CSS_SELECTOR, "div[class*='fleet-operations-pwa__complaint-record__']"
    )

    items = []
    for t in tiles:
        state = ""
        ctype = ""
        try:
            state = t.find_element(
                By.CSS_SELECTOR,
                "div.fleet-operations-pwa__complaint-status__1yyobh2 div",
            ).text.strip()
        except Exception:
            pass
        try:
            ctype = t.find_element(
                By.CSS_SELECTOR,
                "div.fleet-operations-pwa__scan-record-header-title__1yyobh2",
            ).text.strip()
        except Exception:
            pass
        items.append({"state": state, "type": ctype})
    log.debug(f"[COMPLAINTS] collected {len(items)} item(s)")
    return items


def has_open_of_type(items, ctype: str) -> bool:
    log.debug(f"[COMPLAINTS] Checking for open complaints of type '{ctype}'.")
    return any(it.get("state") == "Open" and it.get("type") == ctype for it in items)


def find_dialog(driver):
    """Return the current Compass dialog element, if present."""
    log.debug("[DIALOG] Attempting to find dialog.")
    return driver.find_element(By.CSS_SELECTOR, "div.bp6-dialog, div[class*='dialog']")


def find_elements(driver, locator, timeout=10):
    """Wait for one or more elements to appear and return them."""
    log.debug(f"[FIND] Waiting for elements with locator {locator} and timeout {timeout}s.")
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(locator)
    )


def get_text(driver, xpath: str, timeout: int = 6) -> str:
    log.debug(f"[GETTEXT] Getting text from element with XPath: {xpath} and timeout {timeout}s.")
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    return el.text.strip()


def get_create_date_workitem(driver, complaint: str = "PM", timeout: int = 6) -> str:
    log.debug(f"[GETDATE] Getting create date for work item with complaint '{complaint}' and timeout {timeout}s.")
    xp = (
        "(//div[contains(@class,'scan-record-row-2')]"
        f"[.//div[strong[normalize-space()='Complaints']][contains(normalize-space(),'{complaint}')]]"
        "//div[strong[normalize-space()='Created At']])[1]"
    )
    txt = get_text(driver, xp, timeout)
    return txt.replace("Created At", "").lstrip(": ").strip()


def get_create_date_complaint(driver, complaint: str = "PM", timeout: int = 6) -> str:
    log.debug(f"[GETDATE] Getting create date for complaint '{complaint}' with timeout {timeout}s.")
    xp = (
        "(//div[contains(@class,'complaintItem') or contains(@class,'complaint')]"
        f"[.//*[contains(normalize-space(),'{complaint}')]]"
        "//div[strong[normalize-space()='Created At']])[1]"
    )
    txt = get_text(driver, xp, timeout)
    return txt.replace("Created At", "").lstrip(": ").strip()


def has_open_workitems_of_type(items, itype: str) -> bool:
    log.debug(f"[WORKITEM] Checking for open work items of type '{itype}'.")
    time.sleep(5)  # Allow any async updates to settle
    return any(it.get("state") == "Open" and it.get("type") == itype for it in items)


def debug_list_work_items(driver, timeout: int = 10):
    log.debug(f"[WORKITEM] Debugging list of work items with timeout {timeout}s.")
    # Ensure Work Items panel is visible
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.bp6-tab-panel[id*='workItems'][aria-hidden='false']")
        )
    )
    panel = driver.find_elements(
        By.CSS_SELECTOR, "div.bp6-tab-panel[id*='workItems'][aria-hidden='false']"
    )

    # One tile = scan-record card
    tiles = panel.find_elements(
        By.CSS_SELECTOR, "div[class*='scan-record__'][class*='bp6-card']"
    )
    log.info(f"[WORKITEMS][DBG] tiles={len(tiles)}")

    for i, t in enumerate(tiles, 1):
        try:
            wtype = t.find_element(
                By.CSS_SELECTOR, "div[class*='scan-record-header-title__']"
            ).text.strip()
        except Exception:
            wtype = ""
        try:
            state = t.find_element(
                By.CSS_SELECTOR, "div[class*='scan-record-header-title-right__']"
            ).text.strip()
        except Exception:
            state = ""
        log.info(f"  - #{i} type='{wtype}' state='{state}'")


 
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _dump_artifacts(driver, label: str):
    log.debug(f"[ARTIFACT] Dumping artifacts for label: {label}")
    ts = time.strftime("%Y%m%d-%H%M%S")
    artifacts_dir = os.path.join(PROJECT_ROOT, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    png = os.path.join(artifacts_dir, f"{ts}_{label}.png")
    html = os.path.join(artifacts_dir, f"{ts}_{label}.html")
    try:
        driver.save_screenshot(png)
    except Exception as _:
        pass
    try:
        with open(html, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception as _:
        pass
    log.debug(f"[ARTIFACT] saved {png} and {html}")

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def is_mva_known(driver, mva: str, timeout: int = 12) -> bool:
    """Return True when the vehicle properties container renders."""
    log.info(f"[MVA] {mva} — verifying vehicle properties render...")
    container_selector = (By.CSS_SELECTOR, "div[class*='vehicle-properties-container']")
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(container_selector)
        )
        log.debug(
            f"[MVA] {mva} — vehicle properties container detected (class={container.get_attribute('class')!r})"
        )
        return True
    except TimeoutException:
        _dump_artifacts(driver, f"mva_{mva}_missing_vehicle_props")
        log.warning(f"[MVA][WARN] {mva} — vehicle properties container not found (likely unknown MVA)")
        return False



from selenium.common.exceptions import StaleElementReferenceException

def is_stale(element) -> bool:
    try:
        # Calling .is_enabled() or .tag_name forces a round-trip to the DOM
        element.is_enabled()
        return False
    except StaleElementReferenceException:
        return True



from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def is_stale(element) -> bool:
    """Return True if element reference is stale (detached from DOM)."""
    log.debug("[ELEMENT] Checking if element is stale.")
    try:
        _ = element.is_enabled()  # any property that forces a DOM call
        return False
    except StaleElementReferenceException:
        return True


def click_element(driver, locator: tuple, desc: str = "element", timeout: int = 8) -> bool:
    """Find and click an element with a single retry if stale."""
    log.debug(f"[CLICK] attempting to click {locator} ({desc}) and a timeout of {timeout}s")
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        try:
            el.click()
            log.debug(f"[CLICK] clicked {locator} ({desc}) successfully ")
            return True
        except StaleElementReferenceException:
            log.warning(f"[CLICK][WARN] stale element → retrying {locator} ({desc})")
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            input(f"Pausing before clicking {locator} ({desc}). Press Enter to continue...")
            el.click()
            log.debug(f"[CLICK] clicked after retry {locator} ({desc})")
            return True
    except TimeoutException:
        log.warning(f"[CLICK][WARN] timeout waiting for {locator} ({desc})")
        
        return False
    except Exception as e:
        log.exception(f"[CLICK][ERR] could not click {locator} ({desc})")
        return False





def _is_selected_tile(tile) -> bool:
    log.debug("[TILE] Checking if tile is selected.")
    try:
        cls = tile.get_attribute("class") or ""
        return "fleet-operations-pwa__selected__153vo4c" in cls
    except Exception:
        return False


def select_opcode_pm_gas(driver, timeout: int = 8) -> bool:
    """
    Select the 'PM Gas' opcode tile.
    Tile: .fleet-operations-pwa__opCodeItem__153vo4c
    Text: .fleet-operations-pwa__opCodeText__153vo4c == 'PM Gas'
    """
    log.debug(f"[OPCODE] Selecting 'PM Gas' opcode tile with timeout {timeout}s.")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeItem__153vo4c")
            )
        )
    except TimeoutException:
        return False
    tiles = driver.find_elements(
        By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeItem__153vo4c"
    )
    for t in tiles:
        try:
            txt = t.find_element(
                By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeText__153vo4c"
            ).text.strip()
            if txt == "PM Gas":
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", t
                )
                t.click()
                time.sleep(0.3)
                return True
        except Exception:
            continue
    return False


def create_work_item(driver) -> bool:
    """Click 'Create Work Item'."""
    log.debug("[WORKITEM] Attempting to click 'Create Work Item'.")
    locator = (By.XPATH, "//button[normalize-space()='Create Work Item']")
    return click_element(driver, locator)


def next_step(driver, timeout: int = 10) -> bool:
    """Click the Next button when it is actually enabled."""
    log.debug(f"[NAV] Attempting to click Next button with timeout {timeout}s.")
    # Prefer visible text; fallback to known class
    if click_element(driver, (By.XPATH, "//button[normalize-space()='Next']")):
        time.sleep(0.3)
        return True
    return click_element(driver, (By.CSS_SELECTOR, "button.fleet-operations-pwa__nextButton__153vo4c"))



def has_complete_of_type(items, ctype: str) -> bool:
    log.debug(f"[WORKITEM] Checking for completed work items of type '{ctype}'.")
    log.info(f"[WORKITEM] Checking for completed PM work items of type '{ctype}'")
    result = any(
        it.get("state") == "Complete" and it.get("type") == ctype for it in items
    )
    log.info(f"[WORKITEM] has_complete_of_type('{ctype}') -> {result}")
    return result


# def mark_complete_pm_workitem(driver, note: str = "Done", timeout: int = 8) -> bool:
#     """Click 'Mark Complete', then use dialog-scoped helper to type note and complete."""
#     # 1) Mark Complete (class -> text fallback)
#     if not click_element(driver, (By.CSS_SELECTOR, "button.fleet-operations-pwa__mark-complete-button__spuz8c")):
#         if not click_element(driver, (By.XPATH, "//button[normalize-space()='Mark Complete']")):
#             return False
#     time.sleep(0.2)

#     # 2) Fill correction textarea and click 'Complete Work Item'
#     res = complete_work_item_dialog(
#         driver, note=note, timeout=max(10, timeout), observe=1
#     )
#     log.info(f"[MARKCOMPLETE] complete_work_item_dialog -> {res}")
#     return res.get("status") == "ok"



# _PM_TILE_OVERLAY = (
#     "//div[contains(@class,'bp6-dialog')]"
#     "//div[contains(@class,'tileContent')][normalize-space(.)='PM - PM' or normalize-space(.)='PM Hard Hold - PM']"
#     "/ancestor::div[contains(@class,'complaintItem')][1]"
# )

# _PM_TILE_PAGE = (
#     "//div[contains(@class,'tileContent')][normalize-space(.)='PM - PM' or normalize-space(.)='PM Hard Hold - PM']"
#     "/ancestor::div[contains(@class,'complaintItem')][1]"
# )


def find_element(driver, locator, timeout=10):
    """Wait for a single element to appear and return it."""
    log.debug(f"[FIND] Waiting for element with locator {locator} and timeout {timeout}s.")
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )

# ==========================
# PATCH APPENDED (2025-08-12)
# Overrides for: click_next_in_dialog, click_done, process_pm_workitem_flow
# ==========================


def click_next_in_dialog(driver, timeout: int = 10) -> bool:
    """
    Find and click the PM wizard 'Next' button.
    Matches your HTML exactly and no longer requires the bp6-dialog ancestor.
    """
    log.debug(f"[NAV] Attempting to click Next button in dialog with timeout {timeout}s.")

    def _cands():
        # 1) Exact class from your snippet
        cs = driver.find_elements(
            By.CSS_SELECTOR, "button.fleet-operations-pwa__nextButton__153vo4c"
        )
        # 2) Button with a <p> 'Next' inside (your DOM shape)
        x1 = driver.find_elements(By.XPATH, "//button[.//p[normalize-space()='Next']]")
        # 3) Any role=button with that inner <p> text (fallback)
        x2 = driver.find_elements(
            By.XPATH, "//*[@role='button' and .//p[normalize-space()='Next']]"
        )
        # 4) Last resort: visible text 'Next' on/inside a button-ish thing
        x3 = driver.find_elements(
            By.XPATH,
            "//*[self::button or @role='button'][.//span or .//p][.//p[normalize-space()='Next'] or normalize-space()='Next']",
        )
        seen = set()
        out = []
        for el in cs + x1 + x2 + x3:
            try:
                if not el.is_displayed():
                    continue
                # de-dupe by id()
                oid = el.id if hasattr(el, "id") else el
                if oid in seen:
                    continue
                seen.add(oid)
                out.append(el)
            except Exception:
                continue
        time.sleep(10)
        return out

    def _enabled(el):
        try:
            if not el.is_enabled():
                return False
            aria = el.get_attribute("aria-disabled")
            if str(aria).lower() in ("true", "1"):
                return False
            clz = (el.get_attribute("class") or "").lower()
            if "disabled" in clz:
                return False
            return True
        except Exception:
            return False

    # Wait until at least one candidate is present and enabled
    end = time.time() + timeout
    print("[NEXT][SCAN] searching for Next buttonâ€¦")
    while time.time() < end:
        cands = _cands()
        if cands:
            for i, c in enumerate(cands, 1):
                try:
                    txt = (c.text or c.get_attribute("textContent") or "").strip()
                    clz = c.get_attribute("class") or ""
                    aria = c.get_attribute("aria-disabled")
                    log.info(
                        "[NEXT][CAND] #{i} text='{txt}' enabled={c.is_enabled()} aria-disabled={aria} class='{clz}'"
                    )
                except Exception:
                    pass

            btn = next((c for c in cands if _enabled(c)), None)
            if btn:
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", btn
                    )
                except Exception:
                    pass
                try:
                    btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", btn)
                print("[NEXT] Clicked Next.")
                time.sleep(0.3)
                return True
        time.sleep(0.2)

    # One last dump before failing
    cands = _cands()
    log.error(f"[NEXT][ERROR] No enabled Next button found. candidates={len(cands)}")
    return False


def click_done(driver, timeout: int = 8) -> bool:
    """
    Click 'Done' if the wizard is open; if no dialog visible, consider it already done.
    """
    log.debug(f"[DIALOG] Attempting to click Done button with timeout {timeout}s.")

    dialogs = [
        el
        for el in driver.find_elements(By.CSS_SELECTOR, "div[class*='bp6-dialog']")
        if el.is_displayed()
    ]
    if not dialogs:
        return True

    xpaths = [
        "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Done']",
        "//div[contains(@class,'bp6-dialog')]//span[normalize-space()='Done']/ancestor::button[1]",
        "//div[contains(@class,'bp6-dialog')]//*[@role='button' and normalize-space()='Done']",
        "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Finish']",
        "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Close']",
    ]
    for xp in xpaths:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.3)
            return True
        except TimeoutException:
            continue

    # Last resort: dialog close icon
    try:
        close_btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'bp6-dialog')]//button[contains(@class,'close') or @aria-label='Close']",
                )
            )
        )
        close_btn.click()
        time.sleep(0.2)
        return True
    except Exception:
        return False


# def process_workitem(driver, mva: str):
# 	"""Process a Work Item: complete Open PM WI if found, else skip."""
# 	log.info(f"[WORKITEM] {mva} - starting process")

# 	tiles = get_work_items(driver, mva)
# 	total = len(tiles)
# 	log.info(f"[WORKITEM] {mva} - {total} total work items found")

# 	if total == 0:
# 		log.info(f"[WORKITEM][SKIP] {mva} - no PM work items found")
# 		return {"status": "skipped", "reason": "no_pm_workitems", "mva": mva}

# 	# Handle existing Open PM Work Items only
# 	res = complete_pm_workitem(driver, mva, timeout=8)
# 	if res and res.get("status") == "ok":
# 		return res

# 	log.warning(f"[WORKITEM][WARN] {mva} - failed to complete Open PM Work Item")
# 	return {"status": "failed", "reason": "complete_failed", "mva": mva}





def navigate_back_to_home(driver, max_clicks: int = 3) -> bool:
    """Click the back arrow until the home screen (camera button visible) is reached."""
    log.debug(f"[NAV] Navigating back to home screen (max_clicks={max_clicks}).")
    for i in range(max_clicks):
        # 1) Check if camera button exists (home screen)
        if driver.find_elements(By.XPATH, "//button[contains(@class,'fleet-operations-pwa__camera-button')]"):
            log.info("[NAV] back at MVA input screen (camera button visible)")
            return True

        # 2) Try clicking back arrow
        arrows = driver.find_elements(By.XPATH, "//button[contains(@class,'fleet-operations-pwa__back-button')]")
        if arrows:
            try:
                time.sleep(3)  # brief pause before clicking
                arrows[0].click()
                log.info(f"[NAV] back arrow clicked ({i+1}/{max_clicks})")
                time.sleep(1.5)  # settle
            except Exception as e:
                log.warning(f"[NAV][WARN] could not click back arrow -> {e}")
                return False
        else:
            log.info("[NAV] no back arrow visible")
            break

    log.warning("[NAV][FAIL] did not return to home screen (camera button not found)")
    return False



PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def take_screenshot(driver, prefix="screenshot"):
    """Save a screenshot under {project_root}/screenshots/ with timestamp."""
    log.debug(f"[SCREENSHOT] Taking screenshot with prefix: {prefix}")
    ts = time.strftime("%Y%m%d-%H%M%S")
    fname = f"{prefix}_{ts}.png"
    path = os.path.join(PROJECT_ROOT, "screenshots", fname)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    log.info(f"[DEBUG] Screenshot saved -> {path}")
    return path