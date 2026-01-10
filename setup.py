#!/usr/bin/env python3
"""
Compass Automation Setup Script

This script automatically configures the development environment for the Compass automation project.
It creates a virtual environment, installs dependencies, and validates the setup.

Usage:
    python setup.py

Features:
    - Creates Python virtual environment
    - Installs all required dependencies
    - Validates msedgedriver.exe presence
    - Creates sample config files if missing
    - Validates project structure
    - Runs basic environment tests
"""

import os
import sys
import subprocess
import json
import shutil
import platform
from pathlib import Path


class CompassSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / "venv"
        self.python_exe = None
        self.pip_exe = None
        
        # Core dependencies based on project analysis
        self.dependencies = [
            "selenium>=4.0.0",
            "pytest>=7.0.0",
            "pytest-html",  # For better test reporting
        ]
        
        # Development dependencies
        self.dev_dependencies = [
            "flake8",  # Already in .flake8 config
            "black",   # Code formatting
            "isort",   # Import sorting
        ]
    
    def log(self, message, level="INFO"):
        """Simple logging function"""
        print(f"[{level}] {message}")
    
    def check_python_version(self):
        """Ensure Python 3.8+ is available"""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {version.major}.{version.minor}")
        
        self.log(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        self.log("Setting up virtual environment...")
        
        if self.venv_path.exists():
            self.log("✓ Virtual environment already exists")
        else:
            self.log("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            self.log("✓ Virtual environment created")
        
        # Set executable paths
        if platform.system() == "Windows":
            self.python_exe = self.venv_path / "Scripts" / "python.exe"
            self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:
            self.python_exe = self.venv_path / "bin" / "python"
            self.pip_exe = self.venv_path / "bin" / "pip"
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        self.log("Upgrading pip...")
        try:
            subprocess.run([str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
            self.log("✓ pip upgraded")
        except subprocess.CalledProcessError:
            self.log("⚠ pip upgrade failed, continuing with existing version", "WARN")
    
    def install_dependencies(self):
        """Install project dependencies"""
        self.log("Installing dependencies...")
        
        # Install core dependencies
        for dep in self.dependencies:
            self.log(f"Installing {dep}...")
            subprocess.run([str(self.python_exe), "-m", "pip", "install", dep], check=True)
        
        self.log("✓ Core dependencies installed")
        
        # Ask user if they want dev dependencies
        install_dev = input("Install development dependencies (flake8, black, isort)? [y/N]: ").lower()
        if install_dev in ['y', 'yes']:
            for dep in self.dev_dependencies:
                self.log(f"Installing {dep}...")
                subprocess.run([str(self.python_exe), "-m", "pip", "install", dep], check=True)
            self.log("✓ Development dependencies installed")
    
    def check_msedgedriver(self):
        """Check for msedgedriver.exe in project root"""
        self.log("Checking for msedgedriver.exe...")
        
        driver_path = self.project_root / "msedgedriver.exe"
        if driver_path.exists():
            self.log("✓ msedgedriver.exe found")
            return True
        
        self.log("⚠ msedgedriver.exe not found in project root", "WARN")
        self.log("Please download the correct version from:", "WARN")
        self.log("https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/", "WARN")
        self.log("Place it in: " + str(self.project_root), "WARN")
        return False
    
    def create_sample_config(self):
        """Create sample config files if they don't exist"""
        self.log("Checking configuration files...")
        
        config_dir = self.project_root / "config"
        config_file = config_dir / "config.json"
        
        if config_file.exists():
            self.log("✓ config.json already exists")
            return
        
        # Create config directory if needed
        config_dir.mkdir(exist_ok=True)
        
        # Sample configuration
        sample_config = {
            "username": "your.email@company.com",
            "password": "YourPassword123!",
            "login_id": "YOUR_ID",
            "delay_seconds": 2,
            "mva_entry_delay_seconds": 5,
            "credentials": {
                "sso_email": "your.email@company.com"
            },
            "logging": {
                "level": "INFO",
                "format": "[%(levelname)s] [compass.automation] [%(asctime)s] %(message)s"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        self.log("✓ Sample config.json created - PLEASE UPDATE WITH YOUR CREDENTIALS", "WARN")
        self.log(f"Config location: {config_file}", "WARN")
    
    def create_sample_data(self):
        """Create sample data files"""
        self.log("Checking data files...")
        
        data_dir = self.project_root / "data"
        mva_file = data_dir / "mva.csv"
        
        if mva_file.exists():
            self.log("✓ mva.csv already exists")
            return
        
        # Create data directory if needed
        data_dir.mkdir(exist_ok=True)
        
        # Sample MVA data
        sample_data = """MVA
12345
67890
"""
        
        with open(mva_file, 'w') as f:
            f.write(sample_data)
        
        self.log("✓ Sample mva.csv created - ADD YOUR MVA NUMBERS", "WARN")
    
    def validate_project_structure(self):
        """Validate that all required directories exist"""
        self.log("Validating project structure...")
        
        required_dirs = [
            "config", "core", "data", "flows", "pages", "tests", "utils"
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.log(f"⚠ Missing directories: {', '.join(missing_dirs)}", "WARN")
            return False
        
        self.log("✓ Project structure validated")
        return True
    
    def run_basic_tests(self):
        """Run basic import tests to verify setup"""
        self.log("Running basic environment tests...")
        
        test_script = '''
import sys
print("Testing basic imports...")

try:
    import selenium
    print("OK Selenium import successful")
except ImportError as e:
    print(f"ERROR Selenium import failed: {e}")
    sys.exit(1)

try:
    import pytest
    print("OK Pytest import successful")
except ImportError as e:
    print(f"ERROR Pytest import failed: {e}")
    sys.exit(1)

try:
    from config.config_loader import get_config
    print("OK Config loader import successful")
except ImportError as e:
    print(f"ERROR Config loader import failed: {e}")
    sys.exit(1)

print("OK All basic tests passed!")
'''
        
        try:
            result = subprocess.run(
                [str(self.python_exe), "-c", test_script],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            self.log("✓ Basic environment tests passed")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"✗ Basic tests failed: {e.stdout} {e.stderr}", "ERROR")
            return False
    
    def generate_requirements_txt(self):
        """Generate requirements.txt file"""
        self.log("Generating requirements.txt...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        try:
            # Get installed packages
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True
            )
            
            with open(requirements_file, 'w') as f:
                f.write(result.stdout)
            
            self.log(f"✓ requirements.txt generated")
        except subprocess.CalledProcessError as e:
            self.log(f"⚠ Could not generate requirements.txt: {e}", "WARN")
    
    def print_next_steps(self):
        """Print next steps for the user"""
        self.log("\n" + "="*60)
        self.log("SETUP COMPLETE! Next Steps:")
        self.log("="*60)
        
        if platform.system() == "Windows":
            activate_cmd = ".\\venv\\Scripts\\Activate.ps1"
        else:
            activate_cmd = "source venv/bin/activate"
        
        self.log(f"1. Activate virtual environment:")
        self.log(f"   {activate_cmd}")
        self.log("")
        self.log("2. Update configuration files:")
        self.log("   - config/config.json (add your credentials)")
        self.log("   - data/mva.csv (add your MVA numbers)")
        self.log("")
        self.log("3. Ensure msedgedriver.exe is in project root")
        self.log("")
        self.log("4. Run tests:")
        self.log("   pytest -v tests/")
        self.log("")
        self.log("5. Run standalone:")
        self.log("   python run_compass.py")
        self.log("")
        self.log("For more info, see: Markdown_Files/README.md")
        self.log("="*60)
    
    def run(self):
        """Run the complete setup process"""
        try:
            self.log("Starting Compass Automation Setup...")
            self.log(f"Project root: {self.project_root}")
            
            # Core setup steps
            self.check_python_version()
            self.create_virtual_environment()
            self.upgrade_pip()
            self.install_dependencies()
            
            # Project configuration
            self.create_sample_config()
            self.create_sample_data()
            self.validate_project_structure()
            
            # Validation
            self.run_basic_tests()
            self.generate_requirements_txt()
            
            # Driver check (non-blocking)
            self.check_msedgedriver()
            
            self.print_next_steps()
            
            self.log("✓ Setup completed successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"✗ Setup failed: {e}", "ERROR")
            return False


def main():
    """Main entry point"""
    setup = CompassSetup()
    success = setup.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()