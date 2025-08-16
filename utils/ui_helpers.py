# utils/ui_helpers.py
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def select_location(driver, value="GA4-A", close_timeout=15):
    # Open popover
    office_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bp6-button.fleet-operations-pwa__button__y3et95"))
    )
    office_btn.click()
    print("[FILTER] Office button clicked")

    # Target the popover input and type
    filter_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".bp6-popover-content input.bp6-input[placeholder='Filter...']"))
    )
    filter_input.click()
    time.sleep(0.1)
    filter_input.send_keys("\ue009" + "a")  # Ctrl+A
    time.sleep(0.05)
    filter_input.send_keys("\ue003")  # Delete
    for ch in value:
        filter_input.send_keys(ch)
        time.sleep(0.5)
    time.sleep(2)  # Allow time for filtering

    # Click the exact menu item
    xp = ("//div[contains(@class,'bp6-popover-content')]"
          "//ul[contains(@class,'bp6-menu')]"
          f"//a[contains(@class,'bp6-menu-item') and .//div[normalize-space(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))='{value}']]")
    item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", item)
    item.click()
    print(f"[FILTER] clicked {value}")
    time.sleep(4)  # Allow time for selection to apply

    # Confirm popover closed
    WebDriverWait(driver, close_timeout).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".bp6-popover-content"))
    )
    print("[FILTER] popover closed")

    # Verify the office button now shows correct text
    btn_label = WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "button.bp6-button.fleet-operations-pwa__button__y3et95 h1.bp6-heading"),
            value
        )
    )
    if btn_label:
        print(f"[FILTER] Verified selection '{value}' displayed on button")
    else:
        print(f"[FILTER] Warning: '{value}' not found in button label")
    return True

def _click_tab(driver, data_tab_id: str, timeout: int = 10) -> bool:
    # Guard: any modal overlay gone
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".bp6-dialog[aria-modal='true']"))
    )

    # Find the tab by stable attribute
    tab = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"div.bp6-tab[data-tab-id='{data_tab_id}']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab)
    time.sleep(0.2)
    tab.click()

    # Verify it took (aria-selected flips to true)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"div.bp6-tab[data-tab-id='{data_tab_id}'][aria-selected='true']"))
    )
    return True

def click_work_items(driver, timeout: int = 10) -> bool:
    return _click_tab(driver, "workItems", timeout)

def click_complaints(driver, timeout: int = 10) -> bool:
    print(f"[TAB] Attempting to click Complaints tab (timeout={timeout}s)")
    result = _click_tab(driver, "complaints", timeout)
    if result:
        print("[TAB] Complaints tab clicked and verified as active")
    else:
        print("[TAB] Complaints tab click may have failed")
    return result

def get_complaints(driver, timeout: int = 10):
    """Return list of {'state': 'Open'|'Closed', 'type': 'PM'|...} from the visible Complaints tab."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.bp6-tab-panel[id*='complaints'][aria-hidden='false']"))
    )
    panel = driver.find_element(By.CSS_SELECTOR, "div.bp6-tab-panel[id*='complaints'][aria-hidden='false']")
    tiles = panel.find_elements(By.CSS_SELECTOR, "div[class*='fleet-operations-pwa__complaint-record__']")

    items = []
    for t in tiles:
        state = ""
        ctype = ""
        try:
            state = t.find_element(By.CSS_SELECTOR, "div.fleet-operations-pwa__complaint-status__1yyobh2 div").text.strip()
        except Exception:
            pass
        try:
            ctype = t.find_element(By.CSS_SELECTOR, "div.fleet-operations-pwa__scan-record-header-title__1yyobh2").text.strip()
        except Exception:
            pass
        items.append({"state": state, "type": ctype})
    print(f"[COMPLAINTS] collected {len(items)} item(s)")
    return items

def has_open_of_type(items, ctype: str) -> bool:
    return any(it.get("state") == "Open" and it.get("type") == ctype for it in items)

def get_work_items(driver, timeout: int = 10):
	"""
	Return list of {'state': 'Open'|'Closed'|'Complete'|..., 'type': '<text>'}
	from the visible Work Items tab.
	Counts only real scan-record cards and reads headers for type/state.
	"""
	# Ensure the Work Items panel is visible
	panel = WebDriverWait(driver, timeout).until(
		EC.presence_of_element_located(
			(By.CSS_SELECTOR, "div.bp6-tab-panel[id*='workItems'][aria-hidden='false']")
		)
	)

	# STRICT tile selection: only real scan-record cards
	tiles = panel.find_elements(By.CSS_SELECTOR, "div[class*='scan-record__'][class*='bp6-card']")
	print(f"[WORKITEMS] collected {len(tiles)} tile(s) [strict scan-record cards]")

	items = []
	for i, t in enumerate(tiles, 1):
		state, wtype = "", ""

		# TYPE: left header (e.g., 'PM')
		try:
			wtype = t.find_element(
				By.CSS_SELECTOR, "div[class*='scan-record-header-title__']"
			).text.strip()
		except Exception:
			pass

		# STATE: right header (e.g., 'Open', 'Complete')
		try:
			state = t.find_element(
				By.CSS_SELECTOR, "div[class*='scan-record-header-title-right__']"
			).text.strip()
		except Exception:
			pass

		if state or wtype:
			items.append({"state": state, "type": wtype})
			print(f"[WORKITEMS][DBG] {i}: type='{wtype}' state='{state}'")

	# Summary & debug after the loop
	print(f"[WORKITEMS] collected {len(items)} item(s)")
	if not items:
		try:
			html = panel.get_attribute("innerHTML")
			print("[WORKITEMS][DEBUG] panel HTML length:", len(html))
		except Exception:
			pass

	return items




def has_open_workitems_of_type(items, itype: str) -> bool:
    time.sleep(5)  # Allow any async updates to settle
    return any(it.get("state") == "Open" and it.get("type") == itype for it in items)

def debug_list_work_items(driver, timeout: int = 10):
    # Ensure Work Items panel is visible
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.bp6-tab-panel[id*='workItems'][aria-hidden='false']"))
    )
    panel = driver.find_element(By.CSS_SELECTOR, "div.bp6-tab-panel[id*='workItems'][aria-hidden='false']")

    # One tile = scan-record card
    tiles = panel.find_elements(By.CSS_SELECTOR, "div[class*='scan-record__'][class*='bp6-card']")
    print(f"[WORKITEMS][DBG] tiles={len(tiles)}")

    for i, t in enumerate(tiles, 1):
        try:
            wtype = t.find_element(By.CSS_SELECTOR, "div[class*='scan-record-header-title__']").text.strip()
        except Exception:
            wtype = ""
        try:
            state = t.find_element(By.CSS_SELECTOR, "div[class*='scan-record-header-title-right__']").text.strip()
        except Exception:
            state = ""
        print(f"  - #{i} type='{wtype}' state='{state}'")

def click_button_by_text(driver, text: str, timeout: int = 10) -> bool:
    """Clicks a <button> (or button-like element) by its visible text."""
    try:
        loc = (By.XPATH, f"//button[normalize-space()='{text}'] | //*[self::button or self::span or self::div][normalize-space()='{text}']")
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(loc))
        el.click()
        return True
    except TimeoutException:
        return False
    
def click_button(driver, *, text: str = None, css_class: str = None, timeout: int = 8) -> bool:
        """Click a button by visible text OR CSS class."""
        if not text and not css_class:
            raise ValueError("Either 'text' or 'css_class' is required.")
        loc = (By.XPATH, f"//button[normalize-space()='{text}']") if text else (By.CSS_SELECTOR, f"button.{css_class}")
        try:
            btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(loc))
            btn.click()
            return True
        except TimeoutException:
            return False

def find_pm_tiles(driver, timeout: int = 8):
    """
    Find PM tiles in either the overlay dialog or the page.
    Matches: 'PM' and 'PM Hard Hold'. Returns a list of tile elements.
    """
    end = time.time() + timeout
    while time.time() < end:
        # Prefer visible overlay; fallback to page container
        scopes = []
        for css in ["div[class*='bp6-dialog']", "div[class*='complaintContainer']"]:
            for el in driver.find_elements(By.CSS_SELECTOR, css):
                try:
                    if el.is_displayed():
                        scopes.append(el)
                except Exception:
                    continue

        tiles = []
        for root in scopes:
            # any complaint-like tile under the scope
            cands = root.find_elements(
                By.XPATH,
                ".//*[contains(@class,'complaintItem') or contains(@class,'complaint')]"
            )
            for t in cands:
                try:
                    label = t.find_element(By.XPATH, ".//*[contains(@class,'tileContent') or self::div or self::span]")
                    txt = (label.text or "").strip()
                    if txt == "PM" or "PM Hard Hold" in txt:
                        tiles.append(t)
                except Exception:
                    continue
        if tiles:
            return tiles
        time.sleep(0.2)
    return []



def _is_selected_tile(tile) -> bool:
    try:
        cls = tile.get_attribute("class") or ""
        return "fleet-operations-pwa__selected__153vo4c" in cls
    except Exception:
        return False


def select_all_pm_tiles(driver, tiles, sleep_between_clicks: float = 0.3) -> int:
    """Click all unselected PM tiles; returns count clicked."""
    clicked = 0
    for t in tiles:
        if not _is_selected_tile(t):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", t)
                t.click()
                clicked += 1
                time.sleep(sleep_between_clicks)
            except Exception:
                continue
    return clicked


def select_all_pm_tiles(driver, timeout: int = 8, sleep_between_clicks: float = 0.2) -> int:
    """
    Select every PM/PM Hard Hold tile (multi-select). Re-queries after each click
    so DOM updates don't leave stale elements.
    """
    from selenium.common.exceptions import (ElementClickInterceptedException,
                                            StaleElementReferenceException,
                                            TimeoutException)

    clicked = 0
    # Wait for the container once
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fleet-operations-pwa__complaintContainer__153vo4c"))
        )
    except TimeoutException:
        return 0

    while True:
        # Find any unselected PM tiles (PM or PM Hard Hold)
        candidates = container.find_elements(
            By.XPATH,
            ".//div[contains(@class,'complaintItem')][.//div[contains(@class,'tileContent')][normalize-space()='PM' or contains(., 'PM Hard Hold')]]"
            "[not(contains(@class,'selected'))]"
        )
        if not candidates:
            break

        el = candidates[0]
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            clicked += 1
            time.sleep(sleep_between_clicks)
        except (ElementClickInterceptedException, StaleElementReferenceException):
            # Re-loop to re-query after transient overlay/rerender
            time.sleep(0.2)
            continue
        except Exception:
            # Last-resort JS click
            try:
                driver.execute_script("arguments[0].click();", el)
                clicked += 1
            except Exception:
                break

    return clicked

def select_opcode_pm_gas(driver, timeout: int = 8) -> bool:
    """
    Select the 'PM Gas' opcode tile.
    Tile: .fleet-operations-pwa__opCodeItem__153vo4c
    Text: .fleet-operations-pwa__opCodeText__153vo4c == 'PM Gas'
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeItem__153vo4c"))
        )
    except TimeoutException:
        return False
    tiles = driver.find_elements(By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeItem__153vo4c")
    for t in tiles:
        try:
            txt = t.find_element(By.CSS_SELECTOR, ".fleet-operations-pwa__opCodeText__153vo4c").text.strip()
            if txt == "PM Gas":
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", t)
                t.click()
                time.sleep(0.3)
                return True
        except Exception:
            continue
    return False


def create_work_item(driver, timeout: int = 8) -> bool:
    """Click 'Create Work Item'."""
    return click_button(driver, text="Create Work Item", timeout=timeout)


def click_done(driver, timeout: int = 8) -> bool:
    """Click 'Done' (post-create)."""
    # Try text → role+text → span ancestor button
    for loc in [
        (By.XPATH, "//button[normalize-space()='Done']"),
        (By.XPATH, "//*[@role='button' and normalize-space()='Done']"),
        (By.XPATH, "//span[normalize-space()='Done']/ancestor::button[1]")
    ]:
        try:
            btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(loc))
            btn.click()
            time.sleep(0.3)
            return True
        except TimeoutException:
            continue
    return False

def next_step(driver, timeout: int = 10) -> bool:
    """Click the Next button when it is actually enabled."""
    # Prefer visible text; fallback to known class
    if click_button(driver, text="Next", timeout=timeout):
        time.sleep(0.3)
        return True
    return click_button(driver, css_class="fleet-operations-pwa__nextButton__153vo4c", timeout=timeout)

def click_next_in_dialog(driver, timeout: int = 10) -> bool:
    """
    Clicks the 'Next' button inside the bp6 dialog (PM tile step).
    Waits until it's enabled (not disabled / aria-disabled).
    """
    loc = (By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[normalize-space()='Next']")
    try:
        btn = WebDriverWait(driver, timeout).until(
            lambda d: (el := d.find_element(*loc)) and el.is_displayed() and el.is_enabled()
                      and (el.get_attribute("aria-disabled") not in ("true", "1"))
                      and ("disabled" not in (el.get_attribute("class") or ""))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def has_complete_of_type(items, ctype: str) -> bool:
    print("[WORKITEM] A total of", len(items), "work items found")
    print(f"[WORKITEM] Checking for completed PM work items of type '{ctype}'") 
    result = any(it.get("state") == "Complete" and it.get("type") == ctype for it in items)
    print(f"[WORKITEM] has_complete_of_type('{ctype}') → {result}") 
    return result

def complete_work_item_dialog(driver, note: str = "Done", timeout: int = 10, observe: int = 0) -> dict:
    """
    Click 'Complete Work Item' in the dialog, type a note, and click 'Complete'.
    Returns: {'status': 'ok'|'error', 'reason': str}
    """
    try:
        # Wait for the dialog to appear
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".bp6-dialog[aria-modal='true']"))
        )
        print("[DIALOG] Complete Work Item dialog opened")
    except TimeoutException:
        return {'status': 'error', 'reason': 'DIALOG_NOT_FOUND'}

    # Type the note
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea.fleet-operations-pwa__note-textarea__153vo4c")
        textarea.clear()
        textarea.send_keys(note)
        if observe > 0:
            time.sleep(observe)
        print(f"[DIALOG] Typed note: {note}")
    except Exception as e:
        print(f"[DIALOG][ERROR] Note textarea not found or not interactable: {e}")
        return {'status': 'error', 'reason': 'NOTE_TEXTAREA_NOT_FOUND'}

    # Click Complete Work Item
    if click_button(driver, text="Complete Work Item", timeout=timeout):
        print("[DIALOG] Clicked Complete Work Item")
        return {'status': 'ok', 'reason': 'COMPLETED'}
    
    print("[DIALOG][ERROR] Complete Work Item button not found or not clickable")
    return {'status': 'error', 'reason': 'COMPLETE_BUTTON_NOT_FOUND'}


def process_pm_workitem_flow(driver, sleeps=(0.5, 0.5, 0.5), pre_clicked: bool = False) -> dict:
    """
    End-to-end (design phase): Add Work Item → select PM tiles → Next → Next (Mileage) → select 'PM Gas' → Create → Done.
    Returns: {'status': 'done'|'skipped_no_pm'|'failed', 'selected': int, 'reason': str}
    """
    # 1) Click "Add Work Item" unless the caller already did it
    if not pre_clicked:
        if not click_button(driver, text="Add Work Item", timeout=8):
            if not click_button(driver, css_class="fleet-operations-pwa__create-item-button__1gmnvu9", timeout=8):
                return {'status': 'failed', 'selected': 0, 'reason': 'ADD_WORK_ITEM_NOT_FOUND'}
        wait = max(float(sleeps[0]), 0.8)
        print("[SLEEP]", wait)
        time.sleep(wait)

    # 2) Check for PM tiles first
    tiles = find_pm_tiles(driver, timeout=5)
    if not tiles:
        return {'status': 'skipped_no_pm', 'selected': 0, 'reason': 'NO_PM_TILES'}

    # >>> PASTE THIS INSTEAD — utils/ui_helpers.py → process_pm_workitem_flow
    # 3) Select all PM tiles
    selected = select_all_pm_tiles(driver, tiles)
    # pause so Next enables after selection (consolidated sleep)
    time.sleep(max(sleeps[1], 0.3))

    # 4) Next (within PM selection dialog) → proceed to Record Mileage
    if not click_next_in_dialog(driver, timeout=10):
        return {'status': 'failed', 'selected': selected, 'reason': 'NEXT_PM_SELECTION_FAILED'}
    # <<< END PASTE

    time.sleep(0.3)
    if not click_next_in_dialog(driver, timeout=10):
        return {'status': 'failed', 'selected': selected, 'reason': 'NEXT_PM_SELECTION_FAILED'}


    # 5) Record Mileage → Next (ignore fields)
    if not next_step(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'NEXT_MILEAGE_FAILED'}
    time.sleep(0.5)

    # 6) Opcode: select 'PM Gas'
    if not select_opcode_pm_gas(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'OPCODE_PM_GAS_NOT_FOUND'}
    time.sleep(0.3)

    # 7) Create Work Item
    if not create_work_item(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'CREATE_WORK_ITEM_FAILED'}
    time.sleep(0.5)

    # 8) Open → Mark Complete → Complete Work Item
    if not complete_pm_workitem(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'COMPLETE_PM_WORKITEM_FAILED'}
    time.sleep(0.5)

    # 9) Done
    if not click_done(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'DONE_BUTTON_NOT_FOUND'}
    return {'status': 'done', 'selected': selected, 'reason': 'SUCCESS'}


def open_pm_workitem_card(driver, timeout: int = 8) -> bool:
    """Open the newly created PM work item (status: Open)."""
    loc = (By.XPATH, "//div[contains(@class,'scan-record')][.//div[normalize-space()='PM'] and .//div[normalize-space()='Open']]")
    try:
        card = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(loc))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        card.click()
        time.sleep(0.3)
        return True
    except TimeoutException:
        return False


def mark_complete_pm_workitem(driver, note: str = "Done", timeout: int = 8) -> bool:
    """Click 'Mark Complete', then use dialog-scoped helper to type note and complete."""
    # 1) Mark Complete (class → text fallback)
    if not click_button(driver, css_class="fleet-operations-pwa__mark-complete-button__spuz8c", timeout=timeout):
        if not click_button(driver, text="Mark Complete", timeout=timeout):
            return False
    time.sleep(0.2)
    # 2) Fill correction textarea and click 'Complete Work Item'
    res = complete_work_item_dialog(driver, note=note, timeout=max(10, timeout), observe=1)
    print(f"[MARKCOMPLETE] complete_work_item_dialog → {res}")
    return res.get("status") == "ok"


def complete_pm_workitem(driver, timeout: int = 8) -> bool:
    """Open the PM work item, mark complete with note='Done'."""
    if not open_pm_workitem_card(driver, timeout=timeout):
        return False
    return mark_complete_pm_workitem(driver, note="Done", timeout=timeout)


# exact-text matches for the two PM variants
_PM_TILE_OVERLAY = ("//div[contains(@class,'bp6-dialog')]"
    "//div[contains(@class,'tileContent')][normalize-space(.)='PM - PM' or normalize-space(.)='PM Hard Hold - PM']"
    "/ancestor::div[contains(@class,'complaintItem')][1]")

_PM_TILE_PAGE = ("//div[contains(@class,'tileContent')][normalize-space(.)='PM - PM' or normalize-space(.)='PM Hard Hold - PM']"
    "/ancestor::div[contains(@class,'complaintItem')][1]")

def find_pm_tiles(driver, timeout: int = 6):
    end = time.time() + timeout
    while time.time() < end:
        # overlay first
        tiles = driver.find_elements(By.XPATH, _PM_TILE_OVERLAY)
        if not tiles:
            tiles = driver.find_elements(By.XPATH, _PM_TILE_PAGE)
        tiles = [t for t in tiles if t.is_displayed()]
        if tiles:
            return tiles
        time.sleep(0.2)
    return []


def select_all_pm_tiles(driver, tiles, sleep_between_clicks: float = 0.2) -> int:
    """Click all unselected PM tiles; re-query each time to handle re-render."""
    clicked = 0
    while True:
        unselected = driver.find_elements(By.XPATH, _PM_TILE_OVERLAY + "[not(contains(@class,'selected'))]") \
            or driver.find_elements(By.XPATH, _PM_TILE_PAGE + "[not(contains(@class,'selected'))]")
        if not unselected:
            break
        tile = unselected[0]
        # Prefer clicking the label inside the tile (more reliable)
        try:
            target = tile.find_element(By.XPATH, ".//*[contains(@class,'tileContent')]")
        except Exception:
            target = tile
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
        try:
            target.click()
        except Exception:
            driver.execute_script("arguments[0].click();", target)
        # wait for selected class to apply
        try:
            WebDriverWait(driver, 3).until(lambda d: "selected" in (tile.get_attribute("class") or ""))
        except Exception:
            pass
        clicked += 1
        time.sleep(sleep_between_clicks)
    return clicked


def click_next_in_dialog(driver, timeout: int = 10) -> bool:
    locators = [
        (By.CSS_SELECTOR, "div[class*='bp6-dialog'] button[class*='nextButton']"),
        (By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[.//p[normalize-space()='Next']]"),
    ]
    for by, sel in locators:
        try:
            btn = WebDriverWait(driver, timeout).until(
                lambda d: (el := d.find_element(by, sel)) and el.is_displayed() and el.is_enabled()
                          and (el.get_attribute('aria-disabled') not in ('true','1'))
                          and ('disabled' not in (el.get_attribute('class') or ''))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try: btn.click()
            except Exception: driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.3)
            return True
        except Exception:
            continue
    return False

# ==========================
# PATCH APPENDED (2025-08-12)
# Overrides for: click_next_in_dialog, click_done, process_pm_workitem_flow
# ==========================

def click_next_in_dialog(driver, timeout: int = 10) -> bool:
    """
    Find and click the PM wizard 'Next' button.
    Matches your HTML exactly and no longer requires the bp6-dialog ancestor.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    import time

    def _cands():
        # 1) Exact class from your snippet
        cs = driver.find_elements(By.CSS_SELECTOR, "button.fleet-operations-pwa__nextButton__153vo4c")
        # 2) Button with a <p> 'Next' inside (your DOM shape)
        x1 = driver.find_elements(By.XPATH, "//button[.//p[normalize-space()='Next']]")
        # 3) Any role=button with that inner <p> text (fallback)
        x2 = driver.find_elements(By.XPATH, "//*[@role='button' and .//p[normalize-space()='Next']]")
        # 4) Last resort: visible text 'Next' on/inside a button-ish thing
        x3 = driver.find_elements(By.XPATH, "//*[self::button or @role='button'][.//span or .//p][.//p[normalize-space()='Next'] or normalize-space()='Next']")
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
    print("[NEXT][SCAN] searching for Next button…")
    while time.time() < end:
        cands = _cands()
        if cands:
            for i, c in enumerate(cands, 1):
                try:
                    txt = (c.text or c.get_attribute("textContent") or "").strip()
                    clz = c.get_attribute("class") or ""
                    aria = c.get_attribute("aria-disabled")
                    print(f"[NEXT][CAND] #{i} text='{txt}' enabled={c.is_enabled()} aria-disabled={aria} class='{clz}'")
                except Exception:
                    pass

            btn = next((c for c in cands if _enabled(c)), None)
            if btn:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
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
    print(f"[NEXT][ERROR] No enabled Next button found. candidates={len(cands)}")
    return False




def click_done(driver, timeout: int = 8) -> bool:
    """
    Click 'Done' if the wizard is open; if no dialog visible, consider it already done.
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    dialogs = [el for el in driver.find_elements(By.CSS_SELECTOR, "div[class*='bp6-dialog']") if el.is_displayed()]
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
            btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xp)))
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
        close_btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class,'bp6-dialog')]//button[contains(@class,'close') or @aria-label='Close']"
        )))
        close_btn.click()
        time.sleep(0.2)
        return True
    except Exception:
        return False


def process_pm_workitem_flow(driver, sleeps=(0.5, 0.5, 0.5)) -> dict:
    """
    End-to-end (design phase): Add Work Item → select PM tiles → Next → Next (Mileage)
    → select 'PM Gas' → Create Work Item → Open item → Mark Complete → Complete Work Item → Done.
    Returns: {'status': 'done'|'skipped_no_pm'|'failed', 'selected': int, 'reason': 'SUCCESS'|'reason'}
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    # 1) Click "Add Work Item" (text preferred; class fallback)
    if not click_button(driver, text="Add Work Item", timeout=8):
        if not click_button(driver, css_class="fleet-operations-pwa__create-item-button__1gmnvu9", timeout=8):
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((
                    By.XPATH, "//button[normalize-space()='Add Work Item' or .//span[normalize-space()='Add Work Item'] or .//p[normalize-space()='Add Work Item']]"
                )))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                try:
                    btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", btn)
            except TimeoutException:
                return {'status': 'failed', 'selected': 0, 'reason': 'ADD_WORK_ITEM_NOT_FOUND'}

    time.sleep(max(sleeps[0], 0.8))

    # 2) Check for PM tiles first
    tiles = find_pm_tiles(driver, timeout=5)
    if not tiles:
        return {'status': 'skipped_no_pm', 'selected': 0, 'reason': 'NO_PM_TILES'}

    # 3) Select all PM tiles
    selected = select_all_pm_tiles(driver, tiles)
    time.sleep(max(sleeps[1], 0.3))

    # 4) Next (within PM selection dialog) → proceed to Record Mileage
    print("[FLOW][DEBUG] Attempting to click Next in PM selection dialog...")
    if not click_next_in_dialog(driver, timeout=10):
        print("[FLOW][ERROR] Next button click in PM selection dialog failed.")
        return {'status': 'failed', 'selected': selected, 'reason': 'NEXT_PM_SELECTION_FAILED'}

    # 5) Record Mileage → Next (ignore fields)
    if not next_step(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'NEXT_MILEAGE_FAILED'}

    # 6) Opcode: select 'PM Gas'
    if not select_opcode_pm_gas(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'OPCODE_PM_GAS_NOT_FOUND'}
    time.sleep(0.2)

    # 7) Create Work Item
    if not create_work_item(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'CREATE_WORK_ITEM_FAILED'}
    time.sleep(0.3)

    # 8) Open → Mark Complete → Complete Work Item
    if not complete_pm_workitem(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'COMPLETE_PM_WORKITEM_FAILED'}
    time.sleep(0.3)

    # 9) Done
    if not click_done(driver, timeout=8):
        return {'status': 'failed', 'selected': selected, 'reason': 'DONE_BUTTON_NOT_FOUND'}

    return {'status': 'done', 'selected': selected, 'reason': 'SUCCESS'}


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def complete_work_item_dialog(driver, note="Done", timeout=10, observe=0):
    """
    Type `note` in the correction dialog and click 'Complete Work Item'.
    Returns dict with status/reason for easy debug.
    """
    try:
        # 1) Visible dialog root
        dialog = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'bp6-dialog') and @aria-modal='true' and not(@aria-hidden='true')]")
            )
        )
        print("[DIALOG] Correction dialog visible")

        # 2) Textarea inside dialog
        textarea = WebDriverWait(dialog, timeout).until(
            EC.visibility_of_element_located(
                (By.XPATH, ".//textarea[contains(@class,'bp6-text-area') or contains(@class,'textArea')]")
            )
        )
        textarea.click()
        try:
            textarea.clear()
        except Exception:
            pass  # some textareas don't support clear(); sending ctrl+a below covers it
        textarea.send_keys(note)
        # confirm value latched
        try:
            WebDriverWait(driver, 3).until(lambda d: textarea.get_attribute("value") and note in textarea.get_attribute("value"))
        except Exception:
            val = textarea.get_attribute("value") or ""
            print(f"[DIALOG][WARN] textarea value after send_keys: '{val}'")

        # 3) Click 'Complete Work Item'
        btn = WebDriverWait(dialog, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, ".//button[.//span[normalize-space()='Complete Work Item']]")
            )
        )
        if observe:
            import time; time.sleep(observe)  # optional: watch before clicking
        btn.click()
        time.sleep(10)  # allow click to register
        print("[DIALOG] Clicked 'Complete Work Item'")

        # 4) Wait for dialog to close
        WebDriverWait(driver, timeout).until(EC.invisibility_of_element(dialog))
        print("[DIALOG] Correction dialog closed")
        return {"status": "ok"}
    except Exception as e:
        print(f"[DIALOG][ERROR] complete_work_item_dialog: {e}")
        return {"status": "failed", "reason": "COMPLETE_WORK_ITEM_DIALOG_ERROR", "error": str(e)}

