import pytest
from pathlib import Path
from settings.settings import Settings


def test_settings_valid_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests if Settings correctly initializes when a valid path is provided.
    """
    # Create a temporary file to act as a valid trace path
    fake_trace = tmp_path / "trace.txt"
    fake_trace.write_text("test content")

    # Mock the environment variable
    monkeypatch.setenv("TRACE_PATH", str(fake_trace))

    settings = Settings()
    assert settings.trace_path == fake_trace
    assert settings.trace_path.exists()


def test_settings_invalid_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests if Settings raises a ValidationError when the path does not exist.
    """
    # Mock an environment variable with a non-existent path
    monkeypatch.setenv("TRACE_PATH", "non_existent_file.txt")

    with pytest.raises(ValueError):
        Settings()


def test_settings_invalid_file_type(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Tests if Settings raises a ValidationError when the file is not a .txt file.
    """
    monkeypatch.setenv("TRACE_PATH", "invalid_file.type")

    with pytest.raises(ValueError):
        Settings()
