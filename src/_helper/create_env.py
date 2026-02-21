from pathlib import Path
from typing import Optional
from .resolve_game_path import resolve_direct_input_path, resolve_trace_path


def create_env() -> None:
    """
    Creates a .env file. Tries auto-detection first, then falls back to user input.
    """
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"

    print("--- Environment Setup ---")

    # 1. Trace Path
    trace_path: Optional[Path] = None
    try:
        trace_path = resolve_trace_path()
        print(f"Auto-detected trace path: {trace_path}")
    except FileNotFoundError:
        print("Could not automatically find trace.txt.")
        trace_path = _prompt_user_for_file(
            "Please enter the full path to your 'trace.txt'"
        )

    # 2. Direct Input Path
    direct_input_path: Optional[Path] = None
    try:
        direct_input_path = resolve_direct_input_path()
        print(f"Auto-detected direct input path: {direct_input_path}")
    except FileNotFoundError:
        print("Could not automatically find direct input.json.")
        direct_input_path = _prompt_user_for_file(
            "Please enter the full path to your 'direct input.json'"
        )

    # 3. Write .env
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"TRACE_PATH={trace_path}\n")
        f.write(f"DIRECT_INPUT={direct_input_path}\n")

    print(f"Successfully created .env file at: {env_path}")


def _prompt_user_for_file(prompt_text: str) -> Path:
    while True:
        user_input = input(f"{prompt_text}: ").strip()
        # Remove quotes if user copied path as "C:\..."
        user_input = user_input.strip('"').strip("'")

        path = Path(user_input)
        if path.is_file():
            return path
        print(f"Error: File not found at '{path}'. Please try again.")
