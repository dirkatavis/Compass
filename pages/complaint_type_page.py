# FILE: pages/complaint_type_page.py
# PASTE THIS FULL FILE

from __future__ import annotations
from typing import Tuple
from .base_page import BasePage
from utils.mva_helpers import select_pm_complaint

try:
    from selenium.webdriver.common.by import By
except Exception:
    class _By:
        CSS_SELECTOR = "css selector"
        XPATH = "xpath"
        ID = "id"
        NAME = "name"
    By = _By()  # type: ignore


class ComplaintTypePage(BasePage):
    """Select a specific complaint type (e.g., PM) after Drivability."""

    # ---- Selector constants -------------------------------------------------
    class S:
        DIALOG: Tuple[str, str] = (
            By.CSS_SELECTOR,
            "div.bp6-dialog[data-testid='complaint-type-page'], div.fleet-operations-pwa__complaintTypePage",
        )
        TYPE_ITEM: Tuple[str, str] = (
            By.CSS_SELECTOR,
            "div[data-testid='complaint-type-item'], div.fleet-operations-pwa__complaintTypeItem",
        )
        TYPE_LABEL: Tuple[str, str] = (
            By.CSS_SELECTOR,
            "span.complaint-type-label, div.fleet-operations-pwa__complaintTypeLabel",
        )
        NEXT_BTN: Tuple[str, str] = (
            By.CSS_SELECTOR,
            "button[data-testid='complaint-type-next'], button.bp6-button.bp6-intent-primary",
        )

    # ---- Public API (stubs) ------------------------------------------------
    def select_pm_tile(self) -> bool:
        """
        Minimal: try selecting a 'PM' complaint tile.
        Returns True if a tile was clicked (auto-forwards), else False.
        """
        try:
            ok = select_pm_complaint(self.driver, timeout=12)
            if ok:
                print("[COMPLAINT] PM complaint tile selected (auto-forward)")
            else:
                print("[COMPLAINT] No PM complaint tile present; continuing")
            return ok
        except Exception as e:
            print(f"[COMPLAINT][WARN] Failed to select PM complaint: {e}")
            return False
        


    def ensure_open(self) -> None:
        """Later: wait until page/dialog is visible (S.DIALOG)."""
        pass

    def select_type(self, name: str) -> None:
        """
        Stub: locate and click a complaint type by visible text.
        Example: select_type('PM')
        """
        pass

    def click_next(self) -> None:
        """Stub: advance to the Additional Information page."""
        pass


    def select_pm_tile(self, mva=None) -> bool:
        """Select a 'PM' complaint tile (auto-forwards). Returns True if clicked."""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(@class,'damage-options') or contains(., 'Mechanical Issue') or contains(., 'Tire Damage') or contains(., 'Glass Damage') or contains(., 'Keys') or .//h1[normalize-space()='PM']]"
            )))
            from utils.mva_helpers import click_button
            clicked = (click_button(self.driver, text="PM", timeout=4)
                       or click_button(self.driver, text="Preventive Maintenance", timeout=3))
            if not clicked:
                pm_btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class,'damage-option') or contains(@class,'damage-options')]"
                    "[.//h1[normalize-space()='PM'] or .//span[normalize-space()='PM'] or normalize-space()='PM']"
                )))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pm_btn)
                pm_btn.click()
                clicked = True
            print(f"[COMPLAINT] {mva or ''} — Complaint type 'PM' selected")
            return True
        except Exception as e:
            print(f"[COMPLAINT][WARN] {mva or ''} — 'PM' complaint button not available ({e}); continuing")
            return False
