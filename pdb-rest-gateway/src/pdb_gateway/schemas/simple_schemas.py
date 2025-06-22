"""Simple schemas without Pydantic dependencies."""

from enum import Enum


class StepType(str, Enum):
    """Types of stepping operations."""
    NEXT = "next"
    STEP = "step" 
    CONTINUE = "continue"
    UNTIL = "until"
    RETURN = "return"


class SessionStatus(str, Enum):
    """Debugging session status."""
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"