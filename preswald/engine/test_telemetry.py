import os
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, mock_open
import requests
from preswald.engine.telemetry import TelemetryService

@pytest.fixture
def telemetry_service(tmp_path):
    script_path = tmp_path / "test_script.py"
    script_path.touch()
    service = TelemetryService(str(script_path))
    return service

@pytest.fixture
def mock_config():
    return {
        "project": {
            "slug": "test-project",
            "title": "Test Project"
        },
        "data": {
            "source1": {"type": "mysql"},
            "source2": {"type": "postgres"}
        },
        "telemetry": {
            "enabled": True
        }
    }

def test_update_script_path(tmp_path):
    service = TelemetryService()
    script_path = tmp_path / "test.py"
    script_path.touch()

    service.update_script_path(str(script_path))

    assert service.script_path == str(script_path)
    assert service.script_dir == script_path.parent
    assert service.config_path == script_path.parent / "preswald.toml"

def test_update_script_path_none():
    service = TelemetryService()
    service.update_script_path(None)

    assert service.script_path is None
    assert service.script_dir == Path.cwd()
    assert service.config_path == Path.cwd() / "preswald.toml"

@patch('requests.post')
def test_send_telemetry_success(mock_post, telemetry_service, mock_config):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    with patch("builtins.open", mock_open(read_data=str(mock_config))):
        result = telemetry_service.send_telemetry("test_event", {"test": "data"})

    assert result is True
    mock_post.assert_called_once()

@patch('requests.post')
def test_send_telemetry_failure(mock_post, telemetry_service):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    result = telemetry_service.send_telemetry("test_event")

    assert result is False
    mock_post.assert_called_once()

@patch('requests.post')
def test_send_telemetry_exception(mock_post, telemetry_service):
    mock_post.side_effect = requests.exceptions.RequestException()

    result = telemetry_service.send_telemetry("test_event")

    assert result is False
    mock_post.assert_called_once()

@patch('requests.post')
def test_track_command_success(mock_post, telemetry_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = telemetry_service.track_command("test_command", {"arg": "value"})

    assert result is True
    mock_post.assert_called_once()

@patch('requests.post')
def test_track_command_with_script(mock_post, tmp_path):
    service = TelemetryService()
    script_path = tmp_path / "test.py"
    script_path.touch()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = service.track_command("test_command", {"script": str(script_path)})

    assert result is True
    assert service.script_path == str(script_path)
    mock_post.assert_called_once()

@patch('requests.post')
def test_track_command_telemetry_disabled(mock_post, telemetry_service):
    telemetry_service._telemetry_enabled = False

    result = telemetry_service.track_command("test_command")

    assert result is False
    mock_post.assert_not_called()
