import os
import pytest
import toml
from unittest.mock import mock_open, patch
from preswald.utils import (
    read_template,
    read_port_from_config,
    configure_logging,
    validate_slug,
    get_project_slug,
    generate_slug,
)


def test_read_template():
    mock_content = "template content"
    with patch("pkg_resources.resource_filename") as mock_filename:
        mock_filename.return_value = "test_template.template"
        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = read_template("test")
            assert result == mock_content


def test_read_port_from_config(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"project": {"port": 8080}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    assert read_port_from_config(str(config_path), 3000) == 8080


def test_read_port_from_config_missing_file():
    assert read_port_from_config("nonexistent.toml", 3000) == 3000


def test_read_port_from_config_invalid():
    with patch("toml.load", side_effect=Exception("Invalid TOML")):
        assert read_port_from_config("config.toml", 3000) == 3000


def test_configure_logging(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"logging": {"level": "DEBUG", "format": "%(message)s"}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    level = configure_logging(str(config_path))
    assert level == "DEBUG"


def test_configure_logging_override_level():
    level = configure_logging(level="ERROR")
    assert level == "ERROR"


def test_configure_logging_invalid_config():
    with patch("toml.load", side_effect=Exception("Invalid TOML")):
        level = configure_logging("invalid.toml")
        assert level == "INFO"  # Falls back to default


def test_validate_slug_valid():
    valid_slugs = ["test-slug", "my-project-123", "abc", "123", "a-b-c"]
    for slug in valid_slugs:
        assert validate_slug(slug) is True


def test_validate_slug_invalid():
    invalid_slugs = [
        "",  # Empty
        "ab",  # Too short
        "-test-",  # Starts/ends with hyphen
        "Test_Slug",  # Invalid characters
        "a" * 64,  # Too long
        "hello world",  # Contains space
        "UPPERCASE",  # Contains uppercase
    ]
    for slug in invalid_slugs:
        assert validate_slug(slug) is False


def test_get_project_slug(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"project": {"slug": "test-project"}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    assert get_project_slug(str(config_path)) == "test-project"


def test_get_project_slug_missing_file():
    with pytest.raises(Exception) as exc:
        get_project_slug("nonexistent.toml")
    assert "Config file not found" in str(exc.value)


def test_get_project_slug_missing_section(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_path))
    assert "Missing [project] section" in str(exc.value)


def test_get_project_slug_missing_field(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"project": {}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_path))
    assert "Missing required field 'slug'" in str(exc.value)


def test_get_project_slug_invalid(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"project": {"slug": "INVALID!"}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_path))
    assert "Invalid slug format" in str(exc.value)


@patch("random.randint", return_value=123456)
def test_generate_slug(mock_random):
    assert generate_slug("Test Project") == "test-project-123456"
    assert generate_slug("!!!") == "preswald-123456"
    assert generate_slug("a" * 100) == "preswald-123456"  # Too long input
    assert generate_slug("hello_world") == "hello-world-123456"
