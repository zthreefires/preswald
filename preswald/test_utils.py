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
    mock_content = "Template content"
    with patch("pkg_resources.resource_filename") as mock_resource:
        mock_resource.return_value = "mock_path"
        with patch("builtins.open", mock_open(read_data=mock_content)):
            content = read_template("test_template")
            assert content == mock_content


def test_read_port_from_config(tmp_path):
    config_path = tmp_path / "preswald.toml"
    config = {"project": {"port": 8000}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    assert read_port_from_config(str(config_path), 3000) == 8000


def test_read_port_from_config_missing_file():
    assert read_port_from_config("nonexistent.toml", 3000) == 3000


def test_read_port_from_config_invalid():
    with patch("toml.load") as mock_load:
        mock_load.side_effect = Exception("Invalid TOML")
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
    with patch("toml.load") as mock_load:
        mock_load.side_effect = Exception("Invalid TOML")
        level = configure_logging("invalid.toml")
        assert level == "INFO"


def test_validate_slug_valid():
    valid_slugs = ["test-slug", "my-project-123", "abc", "123", "a-b-c"]
    for slug in valid_slugs:
        assert validate_slug(slug) is True


def test_validate_slug_invalid():
    invalid_slugs = [
        "",
        "ab",  # too short
        "-test-slug",  # starts with hyphen
        "test-slug-",  # ends with hyphen
        "Test_Slug",  # uppercase and underscore
        "a" * 64,  # too long
        "hello!world",  # invalid character
        "slug space",  # contains space
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
    config = {"project": {"slug": "Invalid Slug!"}}
    with open(config_path, "w") as f:
        toml.dump(config, f)

    with pytest.raises(Exception) as exc:
        get_project_slug(str(config_path))
    assert "Invalid slug format" in str(exc.value)


def test_generate_slug():
    slug = generate_slug("Test Project Name")
    assert validate_slug(slug)
    assert slug.startswith("test-project-name-")
    assert len(slug) <= 63


def test_generate_slug_invalid_base():
    slug = generate_slug("!!!???")
    assert validate_slug(slug)
    assert slug.startswith("preswald-")
    assert len(slug) <= 63


def test_generate_slug_long_base():
    long_name = "This is a very long project name that would result in an invalid slug"
    slug = generate_slug(long_name)
    assert validate_slug(slug)
    assert len(slug) <= 63
