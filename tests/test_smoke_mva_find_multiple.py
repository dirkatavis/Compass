import json
import time
from pathlib import Path

import pytest

from core import driver_manager
from pages.login_page import LoginPage
from tests.test_smoke_mva_find_single import _enter_mva_and_wait_for_hit
from utils.data_loader import load_mvas
from utils.ui_helpers import select_location

# load real creds (replace hardcoded placeholders)
config_path = Path(r"C:\temp\Python\config\config.json")  # keep your existing pathing convention
with open(config_path, "r") as f:
    config = json.load(f)

USERNAME = config.get("username")
PASSWORD = config.get("password")
LOGIN_ID = config.get("login_id")

@pytest.mark.smoke
def test_smoke_mva_find_multiple():
    driver = driver_manager.get_or_create_driver()
    lp = LoginPage(driver)
    lp.ensure_ready(USERNAME, PASSWORD, LOGIN_ID)

    lp.enter_wwid(LOGIN_ID)
    # Load MVAs from CSV
    mvas = load_mvas(r"data/mva.csv")

    for mva in mvas:
        if not mva or not mva.isdigit() or len(mva) != 8:
            print(f"[MVA] Skipping invalid value: {mva!r}")
            continue

        elem = _enter_mva_and_wait_for_hit(driver, mva, timeout=12)
        if elem:
            print(f"[MVA] {mva} ✓ found")
        else:
            print(f"[MVA] {mva} ✗ not found")
        time.sleep(0.3)  # settle before next iteration

    # Optional: close driver after loop
    driver_manager.quit_driver()

