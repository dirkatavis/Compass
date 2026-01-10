# Compass Automation Setup Guide

Complete step-by-step guide for setting up the Compass Automation development environment.

## Option 0: Ultimate One-Click Setup

**The absolute easiest way** - just copy and paste this into PowerShell:

```powershell
iwr -useb https://raw.githubusercontent.com/dirkatavis/Compass/main/install-compass.ps1 | iex
```

This single command:
- ✅ Downloads the installer
- ✅ Prompts for installation location  
- ✅ Runs complete automated setup
- ✅ Installs everything including Python and Git if needed
- ✅ No prerequisites required!

## Option 1: Fully Automated Bootstrap (Recommended)

**For the easiest setup, use the bootstrap script that handles EVERYTHING:**

```powershell
# Download and run the bootstrap script (requires internet connection)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dirkatavis/Compass/main/bootstrap.ps1" -OutFile "bootstrap.ps1"
.\bootstrap.ps1
```

**What the bootstrap script does:**
- ✅ Checks for and installs Python 3.13 if needed
- ✅ Checks for and installs Git if needed  
- ✅ Creates recommended folder structure (`C:\Dev\Compass`)
- ✅ Clones the repository automatically
- ✅ Downloads correct Edge WebDriver automatically
- ✅ Runs the main setup script
- ✅ Validates everything works

**Bootstrap Options:**
```powershell
# Custom installation path
.\bootstrap.ps1 -InstallPath "C:\MyProjects\Compass"

# Use Windows Package Manager (faster if available)
.\bootstrap.ps1 -UseWinget

# Skip automatic software installation (if you don't have admin rights)
.\bootstrap.ps1 -SkipSoftwareInstall
```

**⚠️ No Administrator Rights?**
The bootstrap script can install Python and Git for your user account only (no admin required). When prompted, choose option 1 to continue with user-level installation.

## Option 2: Manual Setup

If you prefer to control each step manually:

## Initial Environment Requirements

### Before You Start
You need these installed on your Windows machine:

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: During installation, check "Add Python to PATH"
   - Verify: Open PowerShell and run `python --version`

2. **Git for Windows** 
   - Download from: https://git-scm.com/download/win
   - Needed for cloning the repository
   - Verify: Open PowerShell and run `git --version`

3. **PowerShell 5.1+** (Usually pre-installed on Windows)
   - Verify: Run `$PSVersionTable.PSVersion`

4. **Microsoft Edge Browser** (for msedgedriver compatibility)
   - Usually pre-installed on Windows 10/11

## Complete Setup Workflow

### Step 1: Get the Code
Choose your preferred location and clone the repository:

```powershell
> **Example:** The following demonstrates how to choose a directory and clone the repository. Adjust the path as needed for your environment.
cd C:\Temp\Code\Scripts\py

# Clone the repository
git clone https://github.com/dirkatavis/Compass.git
cd Compass
```

### Step 2: Run Setup
The setup script handles everything automatically:

```powershell
.\setup.ps1
```

**What happens during setup:**
- ✅ Validates Python installation
- ✅ Creates isolated virtual environment (`venv/`)
- ✅ Installs all required dependencies (selenium, pytest, etc.)
- ✅ Creates sample configuration files
- ✅ Sets up project structure
- ✅ Tests basic functionality

### Step 3: Download WebDriver
Download the Edge WebDriver that matches your Edge browser version:
1. Go to: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
2. Download `msedgedriver.exe` 
3. Place it in the project root directory (same folder as setup.ps1)

### Step 4: Configure
Update the configuration with your actual credentials:

```powershell
# Edit these files with your information
notepad config\config.json  # Add your username, password, login_id
notepad data\mva.csv        # Add your actual MVA numbers
```

## Setup Options

The setup script supports these options:
- `-SkipDevDependencies` - Skip development tools (flake8, black, isort) for faster setup
- `-Verbose` - Show detailed output (not implemented in current version)

Example:
```powershell
.\setup.ps1 -SkipDevDependencies
```

## Verification Steps

### Step 5: Validate Setup
Run the validation script to ensure everything is working:

```powershell
python validate_setup.py
```

This checks:
- ✅ All dependencies are installed correctly
- ✅ Configuration files are present
- ✅ Project structure is complete
- ✅ WebDriver is available
- ✅ Basic imports work
- ✅ Integration test passes

### Step 6: Activate Environment
Every time you work on the project, activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

You'll see `(venv)` in your prompt when activated.

### Step 7: Test Everything
Run a basic test to ensure the automation works:

```powershell
# Run unit tests
pytest tests/unit/ -v

# Run smoke tests (requires valid config)
pytest -m smoke -v

# Or run the main automation (requires valid config/data)
python run_compass.py
```

## Alternative Setup Methods

If you prefer a different approach:

### Method 1: Fork and Clone (Recommended for Development)
If you plan to make changes and contribute:

```powershell
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Compass.git
cd Compass
git remote add upstream https://github.com/dirkatavis/Compass.git
.\setup.ps1
```

### Method 2: Download ZIP
If you don't want to use Git:

1. Go to: https://github.com/dirkatavis/Compass
2. Click "Code" → "Download ZIP"
3. Extract to your preferred location
4. Open PowerShell in the extracted folder
5. Run `.\setup.ps1`

## Troubleshooting Common Issues

### Python Not Found
```
ERROR: Python not found. Install Python 3.8+ and add to PATH.
```
**Solution:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart PowerShell
4. Verify with `python --version`

### No Administrator Rights
```
[WARN] Administrator rights recommended for software installation
Options for software installation:
1. Continue with user-level installation (recommended)
2. Skip software installation and install manually
3. Exit and run as Administrator
Choose option [1/2/3]
```
**Solution:** Choose option **1** - the script can install Python and Git for your user account only (no admin rights needed).

### PowerShell Execution Policy Error
```
ERROR: Execution of scripts is disabled on this system
```
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Git Not Found
```
ERROR: 'git' is not recognized as an internal or external command
```
**Solution:**
1. Install Git from https://git-scm.com/download/win
2. Restart PowerShell
3. Verify with `git --version`

### Permission Denied Creating Virtual Environment
```
ERROR: Access denied
```
**Solution:**
- Run PowerShell as Administrator, or
- Choose a different directory where you have write permissions

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