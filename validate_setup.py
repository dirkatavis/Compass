#!/usr/bin/env python3
"""Compass Automation Environment Validator.

This validator is intentionally lightweight and focuses on *local* setup health.
It does NOT require repo-root msedgedriver.exe because the project can use
webdriver-manager to auto-download/cached EdgeDriver.
"""

from __future__ import annotations

from pathlib import Path


def _ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def _warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def _err(msg: str) -> None:
    print(f"  [ERROR] {msg}")


def validate_imports() -> bool:
    print(">> Validating Imports...")
    try:
        import selenium  # noqa: F401

        _ok("selenium import")
    except Exception as e:
        _err(f"selenium import failed: {e}")
        return False

    try:
        import pytest  # noqa: F401

        _ok("pytest import")
    except Exception as e:
        _err(f"pytest import failed: {e}")
        return False

    try:
        from core import driver_manager  # noqa: F401

        _ok("core.driver_manager import")
    except Exception as e:
        _err(f"core.driver_manager import failed: {e}")
        return False

    # webdriver-manager is optional but strongly recommended
    try:
        import webdriver_manager  # noqa: F401

        _ok("webdriver_manager import")
    except Exception as e:
        _warn(f"webdriver_manager not available (local msedgedriver.exe fallback required): {e}")

    return True


def validate_files() -> bool:
    print(">> Validating Files...")
    root = Path(__file__).resolve().parent

    req = root / "requirements.txt"
    if req.exists():
        _ok("requirements.txt present")
    else:
        _warn("requirements.txt missing (setup.ps1 will install minimal deps)")

    cfg = root / "config" / "config.json"
    if cfg.exists():
        _ok("config/config.json present")
    else:
        _warn("config/config.json missing (create it before running real flows)")

    mva = root / "data" / "mva.csv"
    if mva.exists():
        _ok("data/mva.csv present")
    else:
        _warn("data/mva.csv missing")

    local_driver = root / "msedgedriver.exe"
    if local_driver.exists():
        _ok("msedgedriver.exe present (fallback mode)")
    else:
        _warn("msedgedriver.exe not present (OK if webdriver-manager works)")

    return True


def main() -> int:
    print("=" * 60)
    print(">> Compass Automation Environment Validation")
    print("=" * 60)

    ok = True
    ok &= validate_imports()
    print()
    ok &= validate_files()

    print("\n" + "=" * 60)
    if ok:
        print(">> Validation Summary: PASS")
        return 0
    print(">> Validation Summary: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
