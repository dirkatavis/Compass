# Compass Automation

Automating Preventive Maintenance (PM) workflows in the Compass Mobile PWA using Python 3.13, Selenium, and pytest.

## Quick Start
1. Install Python 3.13+ and dependencies (a virtual environment is recommended):
   - `pip install -r requirements.txt`
2. WebDriver options:
   - Recommended: `webdriver-manager` (auto-downloads EdgeDriver; included in `requirements.txt`)
   - Fallback: place `msedgedriver.exe` in the project root
3. Run test suite:
   ```bash
   pytest -q -s tests/test_mva_complaints_tab_fixed.py
   ```
4. Or run standalone:
   ```bash
   py run_compass.py
   ```
