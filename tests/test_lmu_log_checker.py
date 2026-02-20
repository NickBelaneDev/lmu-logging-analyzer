import json

from lmu_log_checker.core.log_analyzer import LogAnalyzer


def _build_rules_data() -> dict:
    return {
        "rules": [
            {
                "id": "ERR_MISSING",
                "category": "error",
                "description": "Missing asset",
                "pattern": r"Missing (?P<asset>\S+)",
                "trigger_file": "ContentLoadi",
            },
            {
                "id": "WARN_LATENCY",
                "category": "warning",
                "description": "Latency warning",
                "pattern": r"Warning: (?P<message>.+)",
            },
        ]
    }


def _make_analyzer() -> LogAnalyzer:
    analyzer = LogAnalyzer()
    # Defensive reset in case class-level lists persist across instances
    analyzer.rules = []
    analyzer.events = []
    return analyzer


def test_load_rules_invalid_rules_key_raises() -> None:
    analyzer = _make_analyzer()

    try:
        analyzer.load_rules({"rules": "not-a-list"})
    except ValueError as exc:
        assert "must be a list" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid rules type")


def test_process_log_file_creates_events() -> None:
    analyzer = _make_analyzer()
    analyzer.load_rules(_build_rules_data())

    log_content = "\n".join(
        [
            "12.34s ContentLoadi 123: Missing texture.dds",
            "15.00s OtherFile 200: Missing mesh.msh",
            "20.00s Render 10: Warning: high latency",
            "not a log line",
        ]
    )

    analyzer.process_log_file(log_content)

    assert len(analyzer.events) == 2
    assert analyzer.events[0].rule_id == "ERR_MISSING"
    assert analyzer.events[0].captured_data == {"asset": "texture.dds"}
    assert analyzer.events[1].rule_id == "WARN_LATENCY"
    assert analyzer.events[1].captured_data == {"message": "high latency"}

    report = analyzer.generate_report_json()
    assert isinstance(report, list)
    assert report[0]["rule_id"] == "ERR_MISSING"

    # Sanity check JSON serializability
    json.dumps(report)
