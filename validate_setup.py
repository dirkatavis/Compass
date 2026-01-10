#!/usr/bin/env python3
"""
Compass Automation Environment Validator

This script validates that the Compass automation environment is properly set up.
Run this after setup.py to ensure everything is working correctly.

Usage:
    python validate_setup.py
"""

import sys
import os
import subprocess
from pathlib import Path


def validate_python_environment():
    """Test Python environment and dependencies"""
    print("🔍 Validating Python Environment...")
    
    # Test basic imports
    try:
        import selenium
        print("  [OK] Selenium imported successfully")
        print(f"     Version: {selenium.__version__}")
    except ImportError as e:
        print(f"  [ERROR] Selenium import failed: {e}")
        return False
    
    try:
        import pytest
        print("  [OK] Pytest imported successfully")
        print(f"     Version: {pytest.__version__}")
    except ImportError as e:
        print(f"  [ERROR] Pytest import failed: {e}")
        return False
    
    # Test project imports
    try:
        from config.config_loader import get_config
        print("  [OK] Config loader imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Config loader import failed: {e}")
        return False
    
    try:
        from utils.logger import log
        print("  [OK] Logger imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Logger import failed: {e}")
        return False
    
    return True


def validate_configuration():
    """Test configuration files"""
    print("🔍 Validating Configuration Files...")
    
    project_root = Path(__file__).parent
    config_file = project_root / "config" / "config.json"
    
    if not config_file.exists():
        print(f"  [ERROR] Config file missing: {config_file}")
        return False
    
    try:
        import json
        with open(config_file) as f:
            config = json.load(f)
        
        required_keys = ["username", "password", "login_id"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"  [ERROR] Missing config keys: {missing_keys}")
            return False
        
        # Check if still using default values
        default_values = ["your.email@company.com", "YourPassword123!", "YOUR_ID"]
        using_defaults = any(config.get(key) in default_values for key in required_keys)
        
        if using_defaults:
            print("  [WARN] Still using default config values - UPDATE config.json with your credentials")
        else:
            print("  [OK] Config file contains custom values")
        
        print(f"  [OK] Config file loaded successfully: {config_file}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Config file validation failed: {e}")
        return False


def validate_data_files():
    """Test data files"""
    print("🔍 Validating Data Files...")
    
    project_root = Path(__file__).parent
    mva_file = project_root / "data" / "mva.csv"
    
    if not mva_file.exists():
        print(f"  [ERROR] MVA data file missing: {mva_file}")
        return False
    
    try:
        with open(mva_file) as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("  [WARN] MVA file only contains header - ADD your MVA numbers")
        else:
            print(f"  [OK] MVA file contains {len(lines)-1} MVA entries")
        
        print(f"  [OK] MVA data file loaded successfully: {mva_file}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] MVA file validation failed: {e}")
        return False


def validate_driver():
    """Test WebDriver availability"""
    print("🔍 Validating WebDriver...")
    
    project_root = Path(__file__).parent
    driver_path = project_root / "msedgedriver.exe"
    
    if not driver_path.exists():
        print(f"  [ERROR] msedgedriver.exe not found: {driver_path}")
        print("     Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        return False
    
    print(f"  [OK] msedgedriver.exe found: {driver_path}")
    
    # Try to get driver version
    try:
        result = subprocess.run([str(driver_path), "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"     Version: {version}")
        else:
            print("     Could not determine driver version")
    except Exception:
        print("     Could not determine driver version")
    
    return True


def validate_project_structure():
    """Test project structure"""
    print("🔍 Validating Project Structure...")
    
    project_root = Path(__file__).parent
    required_dirs = ["config", "core", "data", "flows", "pages", "tests", "utils"]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  [OK] {dir_name}/ directory exists")
        else:
            print(f"  [ERROR] {dir_name}/ directory missing")
            missing_dirs.append(dir_name)
    
    return len(missing_dirs) == 0


def run_basic_test():
    """Run a basic test to ensure everything works together"""
    print("🔍 Running Basic Integration Test...")
    
    try:
        # Test driver creation
        from core import driver_manager
        print("  [OK] Driver manager imported successfully")
        
        # Test config loading  
        from config.config_loader import get_config
        username = get_config("username")
        print(f"  [OK] Config loaded successfully (username: {username[:5]}...)")
        
        # Test data loading
        from utils.data_loader import load_mvas
        project_root = Path(__file__).parent
        csv_path = project_root / "data" / "mva.csv"
        mvas = load_mvas(str(csv_path))
        print(f"  [OK] Data loading successful ({len(mvas)} MVAs loaded)")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Integration test failed: {e}")
        return False


def main():
    """Main validation function"""
    print("=" * 60)
    print(">> Compass Automation Environment Validation")
    print("=" * 60)
    print()
    
    # Run all validations
    validations = [
        ("Python Environment", validate_python_environment),
        ("Configuration", validate_configuration),
        ("Data Files", validate_data_files),
        ("WebDriver", validate_driver),
        ("Project Structure", validate_project_structure),
        ("Integration Test", run_basic_test),
    ]
    
    results = []
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"  [ERROR] {name} validation crashed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status:10} {name}")
    
    print(f"\n📈 Overall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Your Compass automation environment is fully configured!")
        print("\nNext steps:")
        print("  1. Update config/config.json with your actual credentials")
        print("  2. Update data/mva.csv with your MVA numbers") 
        print("  3. Run: pytest -v tests/")
        print("  4. Run: python run_compass.py")
    else:
        print(f"\n[WARNING] {total - passed} validation(s) failed!")
        print("Please fix the issues above before proceeding.")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)