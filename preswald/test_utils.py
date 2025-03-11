import os
import pytest
import toml
from unittest.mock import mock_open, patch
import logging
from preswald.utils import (
    read_template,
    read_port_from_config,
    configure_logging,
    validate_slug,
    get_project_slug,
    generate_slug,
)


def test_read_template():
    mock_content = "test template content"
    with patch("pkg_resources.resource_filename") as mock_resource:
        mock_resource.return_value = "test_path"
        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = read_template("test")
            assert result == mock_content


def test_read_port_from_config_exists(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"port": 8000}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    result = read_port_from_config(str(config_file), 3000)
    assert result == 8000


def test_read_port_from_config_missing(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    result = read_port_from_config(str(config_file), 3000)
    assert result == 3000


def test_read_port_from_config_no_file():
    result = read_port_from_config("nonexistent.toml", 3000)
    assert result == 3000


def test_configure_logging_default():
    with patch("builtins.open", mock_open()):
        level = configure_logging()
        assert level == "INFO"


def test_configure_logging_from_config(tmp_path):
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
    valid_slugs = ["test-slug", "my-project-123", "abc", "123", "a-b-c"]
    for slug in valid_slugs:
        assert validate_slug(slug) is True


def test_validate_slug_invalid():
    invalid_slugs = [
        "",
        "ab",  # too short
        "-test",  # starts with hyphen
        "test-",  # ends with hyphen
        "Test",  # uppercase
        "test_slug",  # underscore
        "test.slug",  # period
        "a" * 64,  # too long
        "test slug",  # space
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
    with pytest.raises(Exception) as exc_info:
        get_project_slug("nonexistent.toml")
    assert "Config file not found" in str(exc_info.value)


def test_get_project_slug_invalid_format(tmp_path):
    config_file = tmp_path / "preswald.toml"
    config = {"project": {"slug": "Invalid Slug!"}}
    with open(config_file, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc_info:
        get_project_slug(str(config_file))
    assert "Invalid slug format" in str(exc_info.value)


def test_generate_slug():
    with patch("random.randint") as mock_random:
        mock_random.return_value = 123456

        result = generate_slug("Test Project!")
        assert result == "test-project-123456"

        result = generate_slug("!!!!")  # Invalid base name
        assert result == "preswald-123456"


def test_generate_slug_random():
    # Test that random numbers are actually random
    slug1 = generate_slug("test")
    slug2 = generate_slug("test")
    assert slug1 != slug2
