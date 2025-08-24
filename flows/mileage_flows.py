from pages.mileage_dialog import MileageDialog


def complete_mileage_dialog(driver, mva: str) -> dict:
    """Complete the mileage dialog by clicking Next."""
    print(f"[MILEAGE] {mva} — skipping mileage entry → proceeding with Next")
    dlg = MileageDialog(driver)
    if dlg.click_next():
        print(f"[COMPLAINT] {mva} — Mileage Next clicked")
        return {"status": "ok"}
    else:
        print(f"[WORKITEM][WARN] {mva} — Mileage Next not found")
        return {"status": "failed", "reason": "mileage_next"}


def has_next_button(self) -> bool:
    """Return True if the Next button is visible on the mileage dialog."""
    return bool(self.driver.find_elements(*self.S.NEXT_BTN))
