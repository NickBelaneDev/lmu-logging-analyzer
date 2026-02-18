import re
from pydantic import BaseModel, field_validator


class RegexPattern(BaseModel):
    name: str
    pattern: str

    @classmethod
    @field_validator("pattern", mode="before")
    def validate_pattern(cls, value: str):
        try:
            pattern = re.compile(value)
            return pattern
        except re.error:
            raise ValueError


class RegexRegistry:
    def __init__(self):
        self.registry = []

    def add_pattern(self, name: str, pattern: str):
        self.registry.append = RegexPattern(name=name, pattern=pattern)

    def get_registry(self) -> list[RegexPattern]:
        return self.registry
