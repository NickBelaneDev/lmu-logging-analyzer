import os
import tempfile
from pathlib import Path

# Importing the `settings` package runs `settings = get_settings()` at import
# time. Without a valid configuration that falls back to interactive setup
# (`input()` via create_env), which aborts pytest collection on CI where no
# .env and no game install exist. Seed valid temporary paths up front so the
# import-time singleton initializes cleanly everywhere. `setdefault` keeps any
# real environment/.env configuration a developer already has.
_tmp_dir = Path(tempfile.mkdtemp(prefix="lmu-test-env-"))

_trace_path = _tmp_dir / "trace.txt"
_trace_path.write_text("ci-placeholder")

_direct_input_path = _tmp_dir / "direct_input.json"
_direct_input_path.write_text("{}")

os.environ.setdefault("TRACE_PATH", str(_trace_path))
os.environ.setdefault("DIRECT_INPUT", str(_direct_input_path))
