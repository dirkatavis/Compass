from __future__ import annotations
import time
from typing import Tuple
from .base_page import BasePage

try:
	from selenium.webdriver.common.by import By
except Exception:
	class _By:
		CSS_SELECTOR = "css selector"; XPATH = "xpath"; ID = "id"; NAME = "name"
	By = _By()  # type: ignore

class DrivabilityPage(BasePage):
	class S:
		DIALOG: Tuple[str,str] = (By.CSS_SELECTOR, "div.bp6-dialog[data-testid='drivability-page'], div.fleet-operations-pwa__drivabilityPage")
		YES_BTN: Tuple[str,str] = (By.CSS_SELECTOR, "button[data-testid='drivable-yes'], button.fleet-operations-pwa__drivableYes")
		NO_BTN:  Tuple[str,str] = (By.CSS_SELECTOR, "button[data-testid='drivable-no'],  button.fleet-operations-pwa__drivableNo")
		NEXT_BTN:Tuple[str,str] = (By.CSS_SELECTOR, "button[data-testid='drivability-next'], button.bp6-button.bp6-intent-primary")

	def ensure_open(self) -> None:
		self.find(*self.S.DIALOG)

	def select_drivable(self, drivable: bool) -> None:
		btn = self.S.YES_BTN if drivable else self.S.NO_BTN
		self.find(*btn).click()
		time.sleep(0.3)

	def click_next(self) -> None:
		self.find(*self.S.NEXT_BTN).click()
		time.sleep(0.5)
