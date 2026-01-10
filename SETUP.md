# Environment Setup Guide

This guide provides multiple ways to set up the Compass Automation development environment. Choose the method that works best for you.

## Prerequisites

- **Python 3.8+** installed and added to your PATH
- **Git** for version control
- **Microsoft Edge** browser (for msedgedriver.exe compatibility)
- **Windows PowerShell 5.1+** or **PowerShell Core 7+** (recommended)

## Quick Setup Options

### Option 1: One-Click Setup (Recommended)
For the fastest setup, simply run:

```cmd
setup.bat
```

This will:
- Check Python installation
- Run the full setup script
- Show next steps

### Option 2: PowerShell Setup (Advanced Users)
If you prefer PowerShell with more control:

```powershell
.\setup.ps1
```

Options:
- `-SkipDevDependencies` - Skip development tools installation
- `-Verbose` - Show detailed output

### Option 3: Python Setup Script (Cross-Platform)
For maximum compatibility:

```bash
python setup.py
```

### Option 4: Make Commands (Developers)
If you have Make installed:

```bash
make setup          # Full setup
make help           # Show all commands
```

## What the Setup Does

The setup scripts automatically:

1. **Environment Check**
   - Validates Python 3.8+ installation
   - Checks project structure

2. **Virtual Environment**
   - Creates `venv/` directory
   - Installs Python virtual environment

3. **Dependencies Installation**
   - Core: `selenium`, `pytest`, `pytest-html`
   - Optional: `flake8`, `black`, `isort` (development tools)

4. **Configuration Files**
   - Creates `config/config.json` with sample credentials
   - Creates `data/mva.csv` with sample data
   - Generates `requirements.txt`

5. **Validation**
   - Tests basic imports
   - Validates project structure
   - Checks for msedgedriver.exe

## Post-Setup Steps

### 1. Activate Virtual Environment

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Update Configuration

Edit `config/config.json` with your credentials:
```json
{
  "username": "your.email@company.com",
  "password": "YourActualPassword",
  "login_id": "YOUR_ACTUAL_ID",
  "delay_seconds": 2,
  "mva_entry_delay_seconds": 5
}
```

### 3. Add Test Data

Edit `data/mva.csv` with your MVA numbers:
```csv
MVA
12345
67890
ACTUAL_MVA_1
ACTUAL_MVA_2
```

### 4. Download msedgedriver.exe

1. Visit: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
2. Download version matching your Edge browser
3. Place `msedgedriver.exe` in project root directory

### 5. Verify Setup

Run basic tests:
```bash
pytest tests/unit/
```

Run full smoke tests:
```bash
pytest -m smoke tests/
```

## Common Usage Patterns

### Run Tests
```bash
# All tests
pytest -v tests/

# Smoke tests only
pytest -v -m smoke tests/

# Specific test file
pytest -v tests/test_mva_complaints_tab_fixed.py
```

### Run Automation
```bash
# Standalone run with default data
python run_compass.py

# With specific config
python run_compass.py --config config/production.json
```

### Development Tools
```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Check imports
python -c "from config.config_loader import get_config; print('✓ Imports OK')"
```

## Troubleshooting

### Python Not Found
```
ERROR: Python is not installed or not in PATH
```
**Solution:** Install Python from https://www.python.org/downloads/ and ensure "Add to PATH" is checked.

### Permission Errors
```
ERROR: Access denied creating virtual environment
```
**Solution:** Run PowerShell as Administrator or use different directory.

### Import Errors
```
ModuleNotFoundError: No module named 'selenium'
```
**Solution:** Ensure virtual environment is activated and dependencies are installed.

### Driver Issues
```
WebDriverException: Message: 'msedgedriver.exe' executable needs to be in PATH
```
**Solution:** Download correct msedgedriver.exe version and place in project root.

### Configuration Errors
```
FileNotFoundError: config/config.json not found
```
**Solution:** Run setup script to create sample configuration files.

## Manual Setup (If Scripts Fail)

If the automated scripts fail, you can set up manually:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate.bat  # Windows
# or
source venv/bin/activate   # Linux/Mac

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install selenium>=4.0.0 pytest>=7.0.0 pytest-html

# 5. Create config directory
mkdir config
mkdir data

# 6. Create sample config.json (edit with your values)
echo '{"username":"your.email@company.com","password":"password","login_id":"ID"}' > config/config.json

# 7. Create sample mva.csv
echo "MVA\n12345" > data/mva.csv

# 8. Test basic imports
python -c "import selenium, pytest; print('Setup OK')"
```

## Directory Structure After Setup

```
Compass/
├── venv/                 # Virtual environment
├── config/
│   ├── config.json      # Your credentials (KEEP PRIVATE)
│   └── test_data.json   # Test scenarios
├── data/
│   └── mva.csv         # MVA numbers for testing
├── setup.py            # Main setup script
├── setup.ps1           # PowerShell setup script
├── setup.bat           # Batch file setup
├── Makefile            # Make commands
├── requirements.txt    # Generated dependencies
├── msedgedriver.exe    # Download separately
└── run_compass.py      # Main automation script
```

## Next Steps

Once setup is complete:

1. **Read the documentation:** `Markdown_Files/README.md`
2. **Review the architecture:** `.github/copilot-instructions.md`
3. **Run your first test:** `pytest -v -m smoke`
4. **Customize for your environment:** Update configs and test data

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review setup logs for error messages
3. Ensure all prerequisites are installed
4. Try the manual setup steps
5. Refer to project documentation in `Markdown_Files/`