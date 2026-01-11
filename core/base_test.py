import pytest

from core import driver_manager


@pytest.fixture
def driver():
    """Fixture to initialize and quit the WebDriver."""
    driver = driver_manager.get_or_create_driver()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver_manager.quit_driver()
