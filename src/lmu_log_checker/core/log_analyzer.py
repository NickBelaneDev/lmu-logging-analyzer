import re
from typing import Any, Dict, List

from pydantic import BaseModel

from lmu_log_checker.core.log_line_model import AnalysisEvent, AnalysisRule, LogLine


class LogAnalyzer(BaseModel):
    """
    Analyzer for log files based on defined rules.
    """

    LOG_PATTERN: re.Pattern = re.compile(
        r"^\s*(?P<timestamp>\d+\.\d+)s"
        r"\s+(?P<file>[\w\.]+)"
        r"\s+(?P<line_number>\d+):"
        r"\s+(?P<message>.+)$"
    )

    rules: List[AnalysisRule] = []
    events: List[AnalysisEvent] = []

    def load_rules(self, rules_data: Dict[str, Any]) -> None:
        """
        Loads analysis rules from a dictionary.

        Args:
            rules_data: A dictionary containing a 'rules' key with a list of rule definitions.
        """
        rules_list = rules_data.get("rules", [])
        if not isinstance(rules_list, list):
            raise ValueError("The 'rules' key in rules_data must be a list.")

        for rule_data in rules_list:
            if not isinstance(rule_data, dict):
                continue
            rule = AnalysisRule(**rule_data)
            rule.compile()
            self.rules.append(rule)

    def process_log_file(self, file_content: str) -> None:
        """
        Processes the content of a log file and matches it against loaded rules.

        Args:
            file_content: The string content of the log file.
        """
        for line in file_content.splitlines():
            match = self.LOG_PATTERN.match(line)
            if not match:
                continue

            log_entry = LogLine(**match.groupdict())

            for rule in self.rules:
                if rule.trigger_file and rule.trigger_file != log_entry.file:
                    continue

                extracted_data = rule.match(log_entry.message)

                if extracted_data is not None:
                    event = AnalysisEvent(
                        rule_id=rule.id,
                        message=log_entry.message,
                        timestamp=log_entry.timestamp,
                        found_in_file=log_entry.file,
                        captured_data=extracted_data,
                    )
                    self.events.append(event)
                    break

    def generate_report_json(self) -> List[Dict[str, Any]]:
        """
        Generates a JSON-compatible report of the analysis events.

        Returns:
            A list of dictionaries representing the analysis events.
        """
        return [event.model_dump() for event in self.events]
