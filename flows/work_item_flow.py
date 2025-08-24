import time

from selenium.webdriver.common.by import By
from flows.complaints_flows import handle_complaint
from flows.mileage_flows import complete_mileage_dialog
from flows.opcode_flows import select_opcode
from flows.finalize_flow import finalize_workitem
from flows.complaints_flows import handle_complaint
from flows.mileage_flows import complete_mileage_dialog
from flows.opcode_flows import select_opcode
from flows.finalize_flow import finalize_workitem
from utils.ui_helpers import click_element_by_text

def click_work_items(driver) -> bool:
    """Click the 'Work Items' tab in Compass."""
    if click_element_by_text(driver, tag="div", text="Work Items", timeout=8):
        print("[WORKITEMS] tab clicked")
        return True
    else:
        print("[WORKITEMS][WARN] tab not found")
        return False

def get_work_items(driver):
    """Return a list of work item tiles from the Work Items panel."""
    tiles = driver.find_elements(By.CSS_SELECTOR, "div.fleet-operations-pwa__scan-record-row-2__18ey3wz")
    items = []
    for tile in tiles:
        type_el = tile.find_element(By.XPATH, ".//div[strong[contains(text(),'Type')]]")
        state_el = tile.find_element(By.XPATH, ".//div[strong[contains(text(),'State')]]")
        items.append({
            "type": type_el.text.replace("Type:", "").strip(),
            "state": state_el.text.replace("State:", "").strip(),
        })
    print(f"[WORKITEMS] collected {len(items)} item(s)")
    return items

def debug_list_work_items(driver):
    """Print debug info for all current work items."""
    items = get_work_items(driver)
    for i, item in enumerate(items, 1):
        print(f"[WORKITEMS][DBG] {i}: type='{item['type']}' state='{item['state']}'")
    return items


# flows/work_item_flow.py

def process_workitem(driver, mva: str):
	print(f"[WORKITEM] {mva} — starting process")

	# 1) Add Work Item
	print(f"[WORKITEM] {mva} — attempting to add new Work Item")
	if not click_element_by_text(driver, tag="button", text="Add Work Item", timeout=8):
		print(f"[WORKITEM][WARN] {mva} — Add Work Item not found")
		return {"status": "failed", "reason": "add_btn"}
	print(f"[WORKITEM] {mva} — Add Work Item clicked")

	time.sleep(2)  # let complaints dialog settle

	# 2) Complaint decision point
	print(f"[WORKITEM] {mva} — checking for existing complaints")
	complaints = driver.find_elements(By.CLASS_NAME, "fleet-operations-pwa__complaintItem__153vo4c")
	if complaints:
		print(f"[WORKITEM] {mva} — found {len(complaints)} existing complaints")
		selected = False
		for c in complaints:
			tile_text = c.text.strip()
			print(f"[WORKITEM] {mva} — inspecting complaint: '{tile_text}'")
			if "PM" in tile_text:
				c.click()
				print(f"[WORKITEM] {mva} — selected existing complaint '{tile_text}'")
				selected = True
		if not selected:
			print(f"[WORKITEM] {mva} — no PM complaint found → creating new")
			if not click_element_by_text(driver, tag="button", text="Add New Complaint", timeout=6):
				print(f"[WORKITEM][WARN] {mva} — Add New Complaint not clickable")
				return {"status": "failed", "reason": "add_complaint"}
	else:
		print(f"[WORKITEM] {mva} — no complaints listed → creating new")
		if not (click_element_by_text(driver, tag="button", text="Add New Complaint", timeout=6) or
				click_element_by_text(driver, tag="button", text="Create New Complaint", timeout=6)):
			print(f"[WORKITEM][WARN] {mva} — Complaint entry step missing")
			return {"status": "failed", "reason": "entry_step"}

	# 3) Continue workflow (placeholder for mileage, opcode, etc.)
	print(f"[WORKITEM] {mva} — proceeding to next step")
	return {"status": "ok"}
