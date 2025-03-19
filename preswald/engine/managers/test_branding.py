import os
import pytest
import toml
from unittest.mock import mock_open, patch
import time

from preswald.engine.managers.branding import BrandingManager

@pytest.fixture
def branding_manager(tmp_path):
    static_dir = tmp_path / "static"
    assets_dir = tmp_path / "assets"
    static_dir.mkdir()
    assets_dir.mkdir()
    return BrandingManager(str(static_dir), str(assets_dir))

def test_get_branding_config_defaults(branding_manager):
    config = branding_manager.get_branding_config()
    assert config["name"] == "Preswald"
    assert config["logo"] == "/assets/logo.png"
    assert "/assets/favicon.ico?timestamp=" in config["favicon"]
    assert config["primaryColor"] == "#000000"

def test_get_branding_config_with_valid_config(branding_manager, tmp_path):
    config_content = """
    [branding]
    name = "Test App"
    logo = "https://example.com/logo.png"
    favicon = "https://example.com/favicon.ico"
    primaryColor = "#FF0000"
    """

    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    config_file = script_dir / "preswald.toml"
    config_file.write_text(config_content)

    config = branding_manager.get_branding_config(str(script_dir / "script.py"))

    assert config["name"] == "Test App"
    assert config["logo"] == "https://example.com/logo.png"
    assert config["favicon"] == "https://example.com/favicon.ico"
    assert config["primaryColor"] == "#FF0000"

def test_get_branding_config_with_invalid_config(branding_manager, tmp_path):
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    config_file = script_dir / "preswald.toml"
    config_file.write_text("invalid toml content")

    config = branding_manager.get_branding_config(str(script_dir / "script.py"))

    assert config["name"] == "Preswald"
    assert config["logo"] == "/assets/logo.png"
    assert "/assets/favicon.ico?timestamp=" in config["favicon"]
    assert config["primaryColor"] == "#000000"

def test_get_branding_config_with_missing_config(branding_manager, tmp_path):
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()

    config = branding_manager.get_branding_config(str(script_dir / "script.py"))

    assert config["name"] == "Preswald"
    assert config["logo"] == "/assets/logo.png"
    assert "/assets/favicon.ico?timestamp=" in config["favicon"]
    assert config["primaryColor"] == "#000000"

def test_get_branding_config_with_partial_config(branding_manager, tmp_path):
    config_content = """
    [branding]
    name = "Test App"
    """

    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    config_file = script_dir / "preswald.toml"
    config_file.write_text(config_content)

    config = branding_manager.get_branding_config(str(script_dir / "script.py"))

    assert config["name"] == "Test App"
    assert config["logo"] == "/assets/logo.png"
    assert "/assets/favicon.ico?timestamp=" in config["favicon"]
    assert config["primaryColor"] == "#000000"

def test_get_branding_config_with_none_script_path(branding_manager):
    config = branding_manager.get_branding_config(None)

    assert config["name"] == "Preswald"
    assert config["logo"] == "/assets/logo.png"
    assert "/assets/favicon.ico?timestamp=" in config["favicon"]
    assert config["primaryColor"] == "#000000"
