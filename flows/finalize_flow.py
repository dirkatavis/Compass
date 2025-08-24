import time

from utils.ui_helpers import click_element_by_text


def finalize_workitem(driver, mva: str) -> dict:
    """Finalize a Work Item by clicking 'Create Work Item' then 'Done'."""
    print(f"[OPCODE] {mva} — searching for opcode 'PM Gas'")
    if not click_element_by_text(driver, tag="button", text="Create Work Item", timeout=8):
        print(f"[WORKITEM][WARN] {mva} — create_btn not found")
        return {"status": "failed", "reason": "create_btn"}

    print(f"[WORKITEM] {mva} — PM Work Item created")
    time.sleep(2)

    if click_element_by_text(driver, tag="button", text="Done", timeout=8):
        print(f"[WORKITEM] {mva} — Done clicked, returning to MVA input")
        return {"status": "ok"}
    else:
        print(f"[WORKITEM][WARN] {mva} — Done button not found")
        return {"status": "failed", "reason": "done_button"}
