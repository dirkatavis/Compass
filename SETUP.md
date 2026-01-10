# Compass Automation Setup Guide

Simple PowerShell-based setup for the Compass Automation development environment.

## Prerequisites

- **Python 3.8+** installed and added to your PATH
- **Git** for version control
- **Microsoft Edge** browser (for msedgedriver.exe compatibility)
- **Windows PowerShell 5.1+** or **PowerShell Core 7+**

## Quick Setup

Simply run the PowerShell setup script:

```powershell
.\setup.ps1
```

**Options:**
- `-SkipDevDependencies` - Skip development tools installation (flake8, black, isort)
- `-Verbose` - Show detailed output

**What it does:**
- ✅ Validates Python installation
- ✅ Creates virtual environment (`venv/`)
- ✅ Installs dependencies (selenium, pytest)
- ✅ Creates sample config files
- ✅ Validates project structure
- ✅ Tests basic functionality

## What the Setup Does

The PowerShell setup script automatically:

1. **Environment Check** - Validates Python 3.8+ installation
2. **Virtual Environment** - Creates `venv/` directory with isolated Python environment
3. **Dependencies** - Installs selenium, pytest, pytest-html (and optional dev tools)
4. **Configuration** - Creates `config/config.json` with sample credentials
5. **Data Files** - Creates `data/mva.csv` with sample MVA data
6. **Validation** - Tests imports and project structure
7. **Driver Check** - Verifies msedgedriver.exe presence

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

## Common Usage

**Activate environment:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Run tests:**
```powershell
pytest -v tests/
pytest -v -m smoke tests/  # Smoke tests only
```

**Run automation:**
```powershell
python run_compass.py
```

**Validate setup:**
```powershell
python validate_setup.py
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
├── venv/                    # Virtual environment  
├── config/
│   ├── config.json         # Your credentials (KEEP PRIVATE)
│   └── test_data.json      # Test scenarios
├── data/
│   └── mva.csv            # MVA numbers for testing
├── setup.ps1              # PowerShell setup script
├── validate_setup.py      # Environment validation
├── requirements.txt       # Generated dependencies
├── msedgedriver.exe       # Download separately
└── run_compass.py         # Main automation script
```

## Quick Start Commands

```powershell
# Initial setup
.\setup.ps1

# Activate environment
.\venv\Scripts\Activate.ps1

# Validate everything works
python validate_setup.py

# Run your first test
pytest -v -m smoke

# Run automation
python run_compass.py
```