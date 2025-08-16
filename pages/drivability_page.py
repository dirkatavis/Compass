# FILE: pages/drivability_page.py
# PASTE THIS FULL FILE

from __future__ import annotations
from typing import Tuple
from .base_page import BasePage

try:
	from selenium.webdriver.common.by import By
except Exception:
	class _By:
		CSS_SELECTOR = "css selector"
		XPATH = "xpath"
		ID = "id"
		NAME = "name"
	By = _By()  # type: ignore


class DrivabilityPage(BasePage):
	"""Represents the Drivability question page (Is the vehicle drivable?)."""

	class S:
		DIALOG: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"div.bp6-dialog[data-testid='drivability-page'], div.fleet-operations-pwa__drivabilityPage",
		)
		YES_BTN: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"button[data-testid='drivable-yes'], button.fleet-operations-pwa__drivableYes",
		)
		NO_BTN: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"button[data-testid='drivable-no'], button.fleet-operations-pwa__drivableNo",
		)
		NEXT_BTN: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"button[data-testid='drivability-next'], button.bp6-button.bp6-intent-primary",
		)

	def ensure_open(self) -> None:
		"""Later: wait until page/dialog is visible."""
		pass

	def select_drivable(self, drivable: bool) -> None:
		"""Stub: click YES or NO depending on drivable."""
		pass

	def click_next(self) -> None:
		"""Stub: continue to the next page (Complaint Type)."""
		pass
