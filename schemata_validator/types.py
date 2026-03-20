"""Shared types."""

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class ValidationError:
    instance_path: str = ""
    keyword: str = ""
    message: str = ""
    schema_path: str = ""


@dataclass
class ValidationResult:
    valid: bool = False
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)


class Subject(Enum):
    RELAY = "relay"
    CLIENT = "client"
