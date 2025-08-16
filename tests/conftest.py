# tests/conftest.py
# tabs, not spaces
import os
import sys

import pytest

# Ensure project root is on sys.path before importing project modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import driver_manager  # now this will resolve


@pytest.fixture(scope="session", autouse=True)
def _quit_browser_after_session():
    yield
    print("[FIXTURE] All tests complete — quitting singleton driver...")
    driver_manager.quit_driver()

