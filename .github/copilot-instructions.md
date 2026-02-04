# Copilot Instructions for Compass Automation

## Project Overview
- Automates Preventive Maintenance (PM) workflows in the Compass Mobile PWA using Python 3.13, Selenium, and pytest.
- Primary goal: "Fleet PM Data Integrity Auditor" logic—detecting, creating, and reconciling PM work items.
- Core flow: Login → MVA validation → Work Item detection/creation → Complaint association → Dialog navigation → Finalization.

## Architecture & Structure
- **[flows/](flows/)**: Business orchestration logic. [work_item_flow.py](flows/work_item_flow.py) is the central entry point.
- **[pages/](pages/)**: Page Object Model (POM). Classes often inherit from [base_page.py](pages/base_page.py). Avoid direct Selenium calls in flows.
- **[core/](core/)**: System core. [driver_manager.py](core/driver_manager.py) manages a singleton Edge driver.
- **[utils/](utils/)**: Reusable helpers. [ui_helpers.py](utils/ui_helpers.py) (clicks, waits), [logger.py](utils/logger.py), [data_loader.py](utils/data_loader.py).
- **[config/](config/)**: Configuration management via [config_loader.py](config/config_loader.py) reading `config.json`.
- **[data/](data/)**: Test input data (e.g., [mva.csv](data/mva.csv)).

## Key Workflows
- **Test Execution:** `pytest -q -s tests/test_mva_complaints_tab_fixed.py`
- **Unit Tests (TDD):** `pytest tests/unit/` for verifying logic isolation.
- **Standalone Execution:** `py run_compass.py` (processes [mva.csv](data/mva.csv))
- **Indentation:** Use 4 spaces (standardized by [fix-indentation.ps1](fix-indentation.ps1)).
- **Driver:** Requires `msedgedriver.exe` in the project root, matching the installed Edge version.

## Patterns & Conventions (The "Three Pillars" Standard)
- **Singleton Driver:** Access the browser via `driver_manager.get_or_create_driver()`. Never instantiate `webdriver.Edge()` directly.
- **State-Matched Interaction:** Every `.click()` must be followed by a `WebDriverWait` for a unique UI state transition. Prefer [ui_helpers.py](utils/ui_helpers.py) (e.g., `click_element`, `safe_wait`).
- **No Locator Fall-Backs**: DO NOT use `A or B` XPath patterns. Use `find_elements` and explicit `if/else` logic to determine current state. For text buttons, prefer `//button[descendant-or-self::*[normalize-space()='Text']]` to handle nested elements.
- **Tagged Logging:** Use format `[TAG] {mva} - message`. Tags: `[LOGIN]`, `[MVA]`, `[WORKITEM]`, `[COMPLAINT]`, `[AUDITOR]`, `[WARN]`, `[ERROR]`.
- **Error Handling:** Log and skip on recoverable errors. Capture debug info in [artifacts/](artifacts/) (HTML/screenshots).
- **TODOs:** Mark future work with `[TODO]` and track backlog in [Markdown_Files/History.md](Markdown_Files/History.md).

## Project Practices
- **TDD (Test-Driven Development):** Prioritize unit tests in [tests/unit/](tests/unit/) for new utility functions or logic before implementation.
- **Small, Focused Changes:** Prefer changes ≤ 20 lines of code.
- **Reuse Before Create:** Use [utils/ui_helpers.py](utils/ui_helpers.py) before adding new low-level Selenium logic.
- **Milestones:** Update [Markdown_Files/History.md](Markdown_Files/History.md) with key transitions.
- **Stale Elements:** Always re-locate elements inside retry loops or wait for transitions to minimize `StaleElementReferenceException`.

## Example References
- **Flow Logic:** [flows/work_item_flow.py](flows/work_item_flow.py)
- **POM Pattern:** [pages/login_page.py](pages/login_page.py)
- **UI Interactions:** `click_element`, `safe_wait` in [utils/ui_helpers.py](utils/ui_helpers.py)
- **Execution Entry:** [run_compass.py](run_compass.py)


---
For unclear patterns or missing context, ask for clarification or reference the relevant file.
