"""Tests for settings persistence."""

import json
import os
import tempfile
from unittest.mock import patch


def test_settings_creates_defaults_if_file_missing():
    """Settings file is created with defaults when it doesn't exist."""
    from whisper_local.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        settings = Settings(path)

        assert settings.model_size == "turbo"
        assert settings.output_mode == "type"
        assert settings.run_on_startup is False
        assert os.path.exists(path)


def test_settings_persists_across_loads():
    """Changed settings persist when reloaded from disk."""
    from whisper_local.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")

        # Create and modify settings
        settings = Settings(path)
        settings.model_size = "small"
        settings.output_mode = "clipboard"
        settings.run_on_startup = True
        settings.save()

        # Reload from disk
        settings2 = Settings(path)
        assert settings2.model_size == "small"
        assert settings2.output_mode == "clipboard"
        assert settings2.run_on_startup is True


def test_settings_save_writes_valid_json():
    """Settings file contains valid JSON with expected keys."""
    from whisper_local.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        settings = Settings(path)
        settings.save()

        with open(path) as f:
            data = json.load(f)

        assert "model_size" in data
        assert "output_mode" in data
        assert "run_on_startup" in data


def test_settings_ignores_invalid_model_size():
    """Setting an invalid model size is rejected."""
    from whisper_local.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        settings = Settings(path)
        settings.model_size = "invalid_model"
        assert settings.model_size == "turbo"  # unchanged


def test_settings_ignores_invalid_output_mode():
    """Setting an invalid output mode is rejected."""
    from whisper_local.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "settings.json")
        settings = Settings(path)
        settings.output_mode = "invalid_mode"
        assert settings.output_mode == "type"  # unchanged
