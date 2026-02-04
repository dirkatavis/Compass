from selenium.webdriver.common.by import By

from utils.logger import log
from utils.ui_helpers import find_element


class VehiclePropertiesPage:
    def __init__(self, driver):
        self.driver = driver

    def find_mva_echo(self, last8: str, timeout: int = 8):
        """Return the element where the vehicle properties panel echoes the given last8 MVA."""
        try:
            xp_by_label = (
                "//div[contains(@class,'vehicle-properties-container')]"
                "//div[contains(@class,'vehicle-property__')]"
                "[div[contains(@class,'vehicle-property-name')][normalize-space()='MVA']]"
                f"/div[contains(@class,'vehicle-property-value')][contains(normalize-space(), '{last8}')]"
            )
            return find_element(self.driver, (By.XPATH, xp_by_label), timeout=timeout)
        except Exception:
            try:
                xp_any_value_contains = (
                    "//div[contains(@class,'vehicle-properties-container')]"
                    f"//div[contains(@class,'vehicle-property-value')][contains(normalize-space(), '{last8}')]"
                )
                return find_element(
                    self.driver, (By.XPATH, xp_any_value_contains), timeout=3
                )
            except Exception:
                log.error(
                    "[MVA][ERROR] echoed value not found (looked for last8='{last8}')"
                )
                return None

    def get_property_value(self, label: str, timeout: int = 5) -> str | None:
        """Helper to find a property value by its label."""
        try:
            # Debug: find all property names to see what's available
            names = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='vehicle-property-name']")
            available = [n.text.strip() for n in names if n.text.strip()]
            log.info(f"[VEHICLE_PROP] Available labels: {available}")
            
            xpath = (
                "//div[contains(@class, 'vehicle-property__') "
                f"and ./div[contains(@class, 'vehicle-property-name') and normalize-space()='{label}']]"
                "//div[contains(@class, 'vehicle-property-value')]"
            )
            element = find_element(self.driver, (By.XPATH, xpath), timeout=timeout)
            if element:
                value = element.text.strip()
                log.debug(f"[VEHICLE_PROP] Found {label}: {value}")
                return value
            return None
        except Exception as e:
            log.debug(f"[VEHICLE_PROP] Could not find {label}: {e}")
            return None

    def get_lighthouse_status(self) -> str | None:
        """Scrape the Lighthouse status."""
        return self.get_property_value("Lighthouse")

    def get_odometer(self) -> int | None:
        """Scrape the Wizard Odometer and return as an integer."""
        val = self.get_property_value("Wizard Odometer")
        if val:
            try:
                # Remove commas, spaces, or non-numeric chars if any
                clean_val = "".join(filter(str.isdigit, val))
                return int(clean_val)
            except ValueError:
                log.error(f"[VEHICLE_PROP] Odometer value '{val}' is not numeric")
        return None

    def get_next_pm_mileage(self) -> int | None:
        """Scrape the Next PM Mileage and return as an integer."""
        val = self.get_property_value("Next PM Mileage")
        if val:
            try:
                clean_val = "".join(filter(str.isdigit, val))
                return int(clean_val)
            except ValueError:
                log.error(f"[VEHICLE_PROP] Next PM Mileage value '{val}' is not numeric")
        return None

    def get_pm_interval(self) -> int | None:
        """Scrape the PM Interval and return as an integer."""
        val = self.get_property_value("PM Interval")
        if val:
            try:
                clean_val = "".join(filter(str.isdigit, val))
                return int(clean_val)
            except ValueError:
                log.error(f"[VEHICLE_PROP] PM Interval value '{val}' is not numeric")
        return None
