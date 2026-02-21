import sys

from dotenv import load_dotenv, find_dotenv
from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings
from pathlib import Path
from _helper.create_env import create_env

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    trace_path: Path
    direct_input: Path

    @field_validator("trace_path", mode="before")
    @classmethod
    def _validate_trace_path(cls, value: str) -> Path:
        if not value.endswith(".txt"):
            raise ValueError(f"File: {value} is not a .txt file.")

        _trace_path: Path = Path(value)
        if _trace_path.is_file():
            return _trace_path

        raise ValueError(f"Path: {_trace_path} does not exist.")

    @field_validator("direct_input", mode="before")
    @classmethod
    def _validate_direct_input(cls, value: str) -> Path:
        if not value.endswith(".json"):
            raise ValueError(f"File: {value} is not a .json file.")

        _direct_input: Path = Path(value)
        if _direct_input.is_file():
            return _direct_input

        raise ValueError(f"Path: {_direct_input} does not exist.")


def get_settings() -> Settings:
    """
    Loads settings with a fallback to interactive creation.
    """
    try:
        return Settings()  # type: ignore
    except (ValidationError, ValueError):
        print("\nConfiguration missing or invalid. Starting setup...")
        create_env()

        # Reload environment variables from the newly created .env
        load_dotenv(find_dotenv(), override=True)

        try:
            return Settings()  # type: ignore
        except (ValidationError, ValueError) as e:
            print(f"\nCritical Error: Failed to load settings.\n{e}")
            sys.exit(1)


settings = get_settings()


if __name__ == "__main__":
    print(settings.trace_path)
    print(settings.direct_input)
