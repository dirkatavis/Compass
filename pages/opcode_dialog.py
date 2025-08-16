# FILE: pages/opcode_dialog.py
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


class OpcodeDialog(BasePage):
	"""Represents the Opcode selection dialog (≈20 options, incl. PM Gas)."""

	# ---- Selector constants -------------------------------------------------
	class S:
		DIALOG: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"div.bp6-dialog[data-testid='opcode-dialog'], div.fleet-operations-pwa__opcodeDialog",
		)
		OPCODE_ITEM: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"div[data-testid='opcode-item'], div.fleet-operations-pwa__opcodeItem",
		)
		OPCODE_LABEL: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"span.opcode-label, div.fleet-operations-pwa__opcodeLabel",
		)
		CREATE_BTN: Tuple[str, str] = (
			By.CSS_SELECTOR,
			"button[data-testid='opcode-create'], button.bp6-button.bp6-intent-primary",
		)

	# ---- Public API (stubs) ------------------------------------------------
	def ensure_open(self) -> None:
		"""Later: wait until dialog S.DIALOG is visible."""
		pass

	def select_opcode(self, name: str) -> None:
		"""
		Stub: locate and click an opcode by visible text.
		Example: select_opcode("PM Gas")
		"""
		pass

	def click_create(self) -> None:
		"""Stub: click the 'Create Work Item' button."""
		pass
