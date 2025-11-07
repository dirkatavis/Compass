from logging import log

from selenium.webdriver.support.ui import WebDriverWait


class HomePage:
    """A Page Object for a generic home page."""

    def __init__(self, driver):
        """Initializes the Page Object with a WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def go_to_page(self, url):
        """Navigates to the specified URL."""
        self.driver.get(url)
        self.driver.maximize_window()

    def print_page_title(self):
        """Prints the title of the current page."""
        log.info(f"Current Page Title: {self.driver.title}")
