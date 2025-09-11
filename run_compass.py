from core import driver_manager
from pages.login_page import LoginPage
from config.config_loader import get_config  # correct import

def main():
    print("Starting Compass automation...")

    driver = driver_manager.get_or_create_driver()
    print(f"Driver: {driver}")

    login_page = LoginPage(driver)
    login_page.ensure_ready(
        get_config("username"),
        get_config("password"),
        get_config("login_id"),
    )

    print("Automation run complete.")

if __name__ == "__main__":
    main()
