import json
import sys
import pytest
from unittest.mock import mock_open, patch


# Fixture to ensure config_loader is reloaded for each test
@pytest.fixture(autouse=True)
def reload_config_loader():
    if "config.config_loader" in sys.modules:
        del sys.modules["config.config_loader"]
    if "config" in sys.modules and hasattr(sys.modules["config"], "config_loader"):
        delattr(sys.modules["config"], "config_loader")
    yield
    if "config.config_loader" in sys.modules:
        del sys.modules["config.config_loader"]
    if "config" in sys.modules and hasattr(sys.modules["config"], "config_loader"):
        delattr(sys.modules["config"], "config_loader")
def test_get_config_existing_key():
    mock_config_data = {"username": "testuser", "password": "testpassword"}
    with patch("json.load", return_value=mock_config_data), patch("builtins.open", mock_open()):
        from config.config_loader import get_config
        assert get_config("username") == "testuser"
        assert get_config("password") == "testpassword"


def test_get_config_non_existent_key_no_default():
    mock_config_data = {"username": "testuser"}
    with patch("json.load", return_value=mock_config_data), patch("builtins.open", mock_open()):
        from config.config_loader import get_config
        with pytest.raises(KeyError, match="Missing key: 'non_existent_key'"):
            get_config("non_existent_key")


def test_get_config_non_existent_key_with_default():
    mock_config_data = {"username": "testuser"}
    with patch("json.load", return_value=mock_config_data), patch("builtins.open", mock_open()):
        from config.config_loader import get_config
        assert get_config("non_existent_key", "default_value") == "default_value"


def test_config_loader_missing_file():
    with pytest.raises(RuntimeError, match="Missing file"):
        with patch("builtins.open", side_effect=FileNotFoundError):
            from config import config_loader  # noqa: F401


def test_config_loader_invalid_json():
    with pytest.raises(RuntimeError, match="Invalid JSON format"):
        with patch("builtins.open", mock_open()), patch(
            "json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0)
        ):
            from config import config_loader  # noqa: F401


def test_default_timeout_loaded():
    mock_config_data = {"delay_seconds": 10}
    with patch("json.load", return_value=mock_config_data), patch("builtins.open", mock_open()):
        from config.config_loader import DEFAULT_TIMEOUT
        assert DEFAULT_TIMEOUT == 10


def test_default_timeout_uses_default_if_missing():
    mock_config_data = {}
    with patch("json.load", return_value=mock_config_data), patch("builtins.open", mock_open()):
        from config.config_loader import DEFAULT_TIMEOUT
        assert DEFAULT_TIMEOUT == 8