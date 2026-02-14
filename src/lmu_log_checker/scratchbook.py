from pathlib import Path

example_trace_path = Path(__file__).parent.parent.parent / "example_user_data" / "example_trace.txt"
with open(example_trace_path, "r", encoding="utf-8") as f:
    for line in f.readlines():
        if "game.cpp" in line:
            print(line)