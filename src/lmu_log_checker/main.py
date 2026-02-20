from pathlib import Path
from typing import Any

import yaml
from lmu_log_checker.core.log_analyzer import LogAnalyzer
from settings.settings import settings


def load_patterns(file_path: Path) -> Any:
    """
    Loads the YAML patterns from the specified file path.

    Args:
        file_path (Path): The path to the patterns.yaml file.

    Returns:
        Any: The parsed YAML data.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


from collections import Counter, defaultdict


def print_summary(events):
    print("\n" + "=" * 40)
    print("       LMU LOG ANALYSIS REPORT       ")
    print("=" * 40 + "\n")

    # Speicher für Daten
    stats = Counter()
    unique_data = defaultdict(set)
    hardware_info = {}
    critical_events = []

    for e in events:
        rule_id = e["rule_id"]
        data = e.get("captured_data", {})

        # 1. Zählen
        stats[rule_id] += 1

        # 2. Einzigartige Daten sammeln (z.B. Dateinamen, Texturen)
        # Wir nehmen alle Werte aus captured_data und fügen sie als String hinzu
        if data:
            # Erstellt einen String aus den relevanten Daten, z.B. "file_name: layout.mas"
            info_str = ", ".join([str(v) for k, v in data.items() if v])
            if info_str:
                unique_data[rule_id].add(info_str)

        # 3. Hardware Infos separat speichern
        if rule_id == "HW_CPU_INFO":
            hardware_info["CPU"] = (
                f"{data.get('cpu_model')} ({data.get('cores')} cores)"
            )
        if rule_id == "HW_INPUT_DEVICE":
            unique_data["DEVICES"].add(data.get("device_name").strip())

        # 4. Kritische Events merken
        if rule_id == "PHYS_FFB_THROTTLING":
            critical_events.append(e)

    # --- OUTPUT ---

    # SYSTEM SECTION
    print("--- SYSTEM INFO ---")
    if "CPU" in hardware_info:
        print(f"CPU: {hardware_info['CPU']}")

    if "DEVICES" in unique_data:
        print(f"Input Devices ({len(unique_data['DEVICES'])} found):")
        for dev in sorted(unique_data["DEVICES"]):
            print(f"  - {dev}")
    print("")

    # CRITICAL SECTION
    if stats["PHYS_FFB_THROTTLING"] > 0:
        print(f"!!! CRITICAL PERFORMANCE ISSUES ({stats['PHYS_FFB_THROTTLING']}x) !!!")
        for crit in critical_events:
            d = crit["captured_data"]
            print(
                f"  - At {crit['timestamp']}s: Physics dropped to {d.get('physics_hz')}Hz (FFB reduced by {d.get('reduction_pct')}%)"
            )
        print("")

    # ERRORS & WARNINGS SECTION
    print("--- DETECTED ISSUES ---")

    # Regeln definieren, die wir als Liste anzeigen wollen (nicht Hardware/State)
    ignore_rules = [
        "HW_CPU_INFO",
        "HW_INPUT_DEVICE",
        "STATE_ENTER_GAME",
        "STATE_EXIT_GAME",
        "HW_STEER_RANGE_SET",
        "PHYS_FFB_THROTTLING",
    ]

    for rule_id, count in stats.most_common():
        if rule_id in ignore_rules:
            continue

        print(f"[{rule_id}]: {count} occurrences")

        # Details anzeigen (aber limitiert auf z.B. die ersten 3, damit es nicht spammt)
        details = list(unique_data[rule_id])
        if details:
            for i, detail in enumerate(details[:5]):  # Zeige max 5 Beispiele
                print(f"    -> {detail}")
            if len(details) > 5:
                print(f"    -> ... and {len(details) - 5} more unique items.")
        print("")


# Am Ende deiner main.py aufrufen:
# print_summary(result_list)


def main() -> None:
    """
    Main entry point for the log analyzer.
    """
    # Resolve the path to patterns.yaml relative to this script
    base_path = Path(__file__).parent
    patterns_path = base_path / "core" / "patterns.yaml"

    log_analyzer = LogAnalyzer()

    try:
        rules_data = load_patterns(patterns_path)
        log_analyzer.load_rules(rules_data)
        print(f"Successfully loaded {len(rules_data.get('rules', []))} rules.")
    except FileNotFoundError:
        print(f"Error: Could not find patterns file at {patterns_path}")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")

    with open(settings.trace_path, "r", encoding="utf-8") as trace_file:
        log_analyzer.process_log_file(trace_file.read())

    report = log_analyzer.generate_report_json()
    print_summary(report)


"""
 {'captured_data': {'parameter_name': 'FWLiftHeightPlus'},
  'found_in_file': 'ContentLoadi',
  'rule_id': 'PHYS_PARAM_LOAD_FAIL',
  'timestamp': 89.4},
"""
if __name__ == "__main__":
    main()
