# Compass Automation

## Project Overview

This project is a Python-based automation tool for the Compass Mobile PWA. It uses Selenium to automate workflows, likely related to vehicle maintenance or management. The project is structured with clear separation of concerns, including configuration, core driver management, page objects, and business logic flows.

**Key Technologies:**

*   **Language:** Python 3.13
*   **Browser Automation:** Selenium
*   **Testing:** pytest
*   **Configuration:** JSON

**Architecture:**

*   **`run_compass.py`:** The main entry point for running the automation standalone.
*   **`config/`:** Contains configuration files, primarily `config.json` for storing credentials and application settings.
*   **`core/`:** Manages the Selenium WebDriver instance.
*   **`data/`:** Holds CSV files with input data, such as `mva.csv`.
*   **`flows/`:** Encapsulates the business logic for different application workflows.
*   **`pages/`:** Implements the Page Object Model (POM) pattern to represent and interact with different pages of the Compass application.
*   **`tests/`:** Contains pytest tests for verifying the automation scripts.
*   **`utils/`:** Provides helper functions for tasks like data loading and logging.

## Building and Running

**1. Prerequisites:**

*   Python 3.13+
*   Microsoft Edge WebDriver:
    *   Recommended: install `webdriver-manager` (auto-downloads EdgeDriver)
    *   Fallback: `msedgedriver.exe` in the project root

**2. Installation:**

Install dependencies from `requirements.txt` (recommended). A virtual environment is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**3. Running the Application:**

The application can be run in two ways:

*   **Standalone:**

    ```bash
    python run_compass.py
    ```

*   **Via pytest:**

    ```bash
    pytest -q -s tests/test_mva_complaints_tab_fixed.py
    ```

## Development Conventions

*   **Page Object Model (POM):** The project follows the POM pattern, with each page of the application represented by a class in the `pages/` directory.
*   **Configuration:** Application settings and credentials are externalized to `config/config.json`.
*   **Testing:** pytest is used for testing. Tests are located in the `tests/` directory.
*   **Logging:** The project uses a custom logger for logging messages.
*   **Data-Driven:** The automation is data-driven, with input data loaded from CSV files in the `data/` directory.


## Logging Conventions

INFO	Standard application activity. Used to track the general flow of the application for major business-level events or successful operations. Useful for auditing and general statistics.	A user successfully logs in; a background job started/completed; application startup/shutdown.

DEBUG	Detailed, technical information useful only to developers for debugging specific problems during development or testing. This level is generally disabled in production due to high volume.	Variable values at a certain point in a function; a successful database query result; entering or exiting a function.

TRACE	The most granular level. Extremely fine-grained informational events that are typically only needed to diagnose the most obscure issues and show the execution path of the code. Never enabled in production.	Logging every step within an internal loop; every parameter passed into a low-level utility function.