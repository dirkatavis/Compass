# Copilot Instructions for Compass Automation

## Project Overview
- Automates Preventive Maintenance (PM) workflows in the Compass Mobile PWA using Python 3.13, Selenium, and pytest.
- Core flow: Login → MVA validation → Work Item detection/creation → Complaint association → Dialog navigation → Finalization.

## Architecture & Structure
- **flows/**: Business logic for work item, complaint, and dialog flows. Entry: `work_item_flow.py`.
- **pages/**: Page Object Model for UI screens (e.g., `login_page.py`, `work_items_tab.py`).
- **core/**: Driver management (`driver_manager.py`), navigation, and base test logic.
- **utils/**: Logging (`logger.py`), UI helpers, data loading.
- **config/**: Loads credentials and test data from JSON.
- **tests/**: Pytest-based test orchestration.
- **data/**: CSVs for test input (e.g., MVA numbers).

## Key Workflows
- **Run all tests:** `pytest -q -s tests/test_mva_complaints_tab_fixed.py`
- **Standalone run:** `py run_compass.py` (uses `data/mva.csv` as input)
- **Driver:** Prefer `webdriver-manager` (auto-downloads EdgeDriver). Fallback: `msedgedriver.exe` in repo root (see `core/driver_manager.py`).
- **Install deps:** `pip install -r requirements.txt`
- **Logging:** Use `[TAG] {mva} - action` format. Tags: `[LOGIN]`, `[MVA]`, `[WORKITEM]`, `[COMPLAINT]`, `[WARN]`, `[ERROR]`.

## Patterns & Conventions
- **Page Objects:** All UI interactions go through `pages/` classes. Avoid direct Selenium calls in flows.
- **Flows:** Orchestrate business logic, call page objects and helpers.
- **Helpers:** Use `utils/` for reusable logic (e.g., `click_element`, `safe_wait`).
- **Config:** Use `config_loader.get_config(key)` for credentials and settings.
- **Test Data:** Use CSVs in `data/` for MVA/test input. Prefer reading via helpers.
- **Error Handling:** Log and skip on recoverable errors (invalid MVA, missing elements).
- **[TODO] Markers:** Use `[TODO]` inline for future work; backlog tracked in `Markdown_Files/History.md`.

## Project Practices
- **Small, focused changes** (≤20 LOC preferred).
- **One commit at a time**; suggest new branch for large changes.
- **Append-only session logs**; curate milestones in `History.md`.
- **Reuse helpers** before adding new files.
- **Freeze driver/browser versions during debugging.**

## Examples
- See `flows/work_item_flow.py` for main orchestration pattern.
- See `pages/login_page.py` for page object conventions.
- See `utils/logger.py` for logging setup and usage.

---
For unclear patterns or missing context, ask for clarification or reference the relevant file.
