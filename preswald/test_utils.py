import os
import pytest
import toml
import logging
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
    with patch("pkg_resources.resource_filename") as mock_resource:
        mock_resource.return_value = "mock_path"
        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = read_template("test_template")
            assert result == mock_content


def test_read_port_from_config_exists(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"port": 8000}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    result = read_port_from_config(str(config_file), 3000)
    assert result == 8000


def test_read_port_from_config_missing_file():
    result = read_port_from_config("nonexistent.toml", 3000)
    assert result == 3000


def test_read_port_from_config_invalid():
    with patch("toml.load") as mock_load:
        mock_load.side_effect = Exception("Invalid TOML")
        result = read_port_from_config("config.toml", 3000)
        assert result == 3000


def test_configure_logging_default():
    with patch("logging.basicConfig") as mock_basic_config:
        level = configure_logging()
        assert level == "INFO"
        mock_basic_config.assert_called_once()


def test_configure_logging_from_file(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"logging": {"level": "DEBUG"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    level = configure_logging(str(config_file))
    assert level == "DEBUG"


def test_configure_logging_override_level():
    level = configure_logging(level="ERROR")
    assert level == "ERROR"


def test_validate_slug_valid():
    valid_slugs = ["test-slug", "my-project-123", "abc-123", "valid-slug-test"]
    for slug in valid_slugs:
        assert validate_slug(slug) is True


def test_validate_slug_invalid():
    invalid_slugs = [
        "Test-Slug",  # uppercase
        "-test-slug",  # starts with hyphen
        "test-slug-",  # ends with hyphen
        "te",  # too short
        "a" * 64,  # too long
        "test_slug",  # underscore
        "test slug",  # space
        "!invalid!",  # special chars
    ]
    for slug in invalid_slugs:
        assert validate_slug(slug) is False


def test_get_project_slug_valid(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"slug": "test-project"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    result = get_project_slug(str(config_file))
    assert result == "test-project"


def test_get_project_slug_missing_file():
    with pytest.raises(Exception) as exc:
        get_project_slug("nonexistent.toml")
    assert "Config file not found" in str(exc.value)


def test_get_project_slug_missing_section(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"other": {"key": "value"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_file))
    assert "Missing [project] section" in str(exc.value)


def test_get_project_slug_missing_field(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"other": "value"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_file))
    assert "Missing required field 'slug'" in str(exc.value)


def test_get_project_slug_invalid(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"slug": "INVALID"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_file))
    assert "Invalid slug format" in str(exc.value)


def test_generate_slug_valid():
    with patch("random.randint") as mock_random:
        mock_random.return_value = 123456
        result = generate_slug("Test Project")
        assert result == "test-project-123456"
        assert validate_slug(result) is True


def test_generate_slug_fallback():
    with patch("random.randint") as mock_random:
        mock_random.return_value = 123456
        result = generate_slug("!!!!")  # Invalid characters only
        assert result == "preswald-123456"
        assert validate_slug(result) is True


def test_generate_slug_random():
    # Test that different random numbers generate different slugs
    result1 = generate_slug("test")
    result2 = generate_slug("test")
    assert result1 != result2
