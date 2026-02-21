import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LogLine(BaseModel):
    """
    Represents a single parsed line from a log file.

    Attributes:
        timestamp (float): The time in seconds since the start of the log.
        file (str): The source file name from which the log entry originated.
        line_number (int): The line number within the source file.
        message (str): The actual log message content.
    """

    timestamp: float
    file: str
    line_number: int
    message: str


class AnalysisRule(BaseModel):
    """
    Defines a rule for identifying specific events within log messages using regex.

    Attributes:
        id (str): Unique identifier for the rule.
        category (str): The category of the rule (e.g., 'hardware', 'error').
        description (str): A human-readable description of what the rule detects.
        pattern (str): The regular expression pattern used for matching.
        trigger_file (Optional[str]): If provided, the rule only applies to logs from this file.
        solution (Optional[str]): A suggested fix or action if the rule matches.
    """

    id: str
    category: str
    description: str
    pattern: str
    trigger_file: Optional[str] = None
    solution: Optional[str] = None

    _compiled: Optional[re.Pattern] = None

    def compile(self) -> None:
        """
        Compiles the regex pattern for faster matching.
        """
        self._compiled = re.compile(self.pattern, re.IGNORECASE)

    def match(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Matches the rule's pattern against the provided text.

        Args:
            text (str): The log message to check.

        Returns:
            Optional[Dict[str, Any]]: A dictionary of captured named groups if a match is found,
                                      otherwise None.
        """
        if not self._compiled:
            self.compile()
        if self._compiled:
            match = self._compiled.search(text)
            return match.groupdict() if match else None
        return None


class AnalysisEvent(BaseModel):
    """
    Represents an event detected by an AnalysisRule.

    Attributes:
        rule_id (str): The ID of the rule that triggered this event.
        timestamp (float): The timestamp from the log line.
        found_in_file (str): The source file where the event was found.
        message (str): The original log message.
        captured_data (Dict[str, Any]): Data extracted from the message via regex groups.
    """

    rule_id: str
    timestamp: float
    found_in_file: str
    message: str
    captured_data: Dict[str, Any] = Field(default_factory=dict)
