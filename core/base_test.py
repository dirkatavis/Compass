import pytest

from core.driver_manager import get_driver


@pytest.fixture
def driver():
    """Fixture to initialize and quit the WebDriver."""
    driver = get_driver()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

