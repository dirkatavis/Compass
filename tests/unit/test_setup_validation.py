from __future__ import annotations

from pathlib import Path


def test_setup_scripts_exist():
    repo_root = Path(__file__).resolve().parents[2]

    for script in ("setup.ps1", "bootstrap.ps1", "install-compass.ps1"):
        assert (repo_root / script).exists(), f"Missing {script} at repo root"


def test_requirements_include_webdriver_manager():
    repo_root = Path(__file__).resolve().parents[2]
    req = repo_root / "requirements.txt"
    assert req.exists(), "requirements.txt is expected to exist"

    content = req.read_text(encoding="utf-8", errors="ignore")

    # Pin presence checks (versions may change, but dependency must exist)
    assert "webdriver-manager==" in content
    assert "selenium==" in content
    assert "pytest==" in content


def test_setup_ps1_installs_from_requirements():
    repo_root = Path(__file__).resolve().parents[2]
    content = (repo_root / "setup.ps1").read_text(encoding="utf-8", errors="ignore")

    # Ensure our setup script uses requirements.txt when present.
    assert "requirements.txt" in content
    assert "pip install -r" in content or "-m pip install -r" in content


def test_install_compass_runs_setup():
    repo_root = Path(__file__).resolve().parents[2]
    content = (repo_root / "install-compass.ps1").read_text(encoding="utf-8", errors="ignore")

    assert "setup.ps1" in content


def test_validate_setup_main_passes():
    # tests/conftest.py puts repo root on sys.path, so this should import.
    import validate_setup

    assert validate_setup.main() == 0
