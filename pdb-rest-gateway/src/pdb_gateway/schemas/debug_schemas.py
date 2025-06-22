"""Pydantic schemas for debugging operations."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
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


class StartSessionRequest(BaseModel):
    """Request to start a new debugging session."""
    target_file: str = Field(..., description="Python file to debug")
    args: Optional[List[str]] = Field(default=None, description="Arguments for the script")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")


class StartSessionResponse(BaseModel):
    """Response when starting a debugging session."""
    session_id: str = Field(..., description="Unique session identifier")
    status: SessionStatus = Field(..., description="Current session status")
    pid: Optional[int] = Field(default=None, description="Process ID of debugged script")
    message: str = Field(..., description="Status message")


class SetBreakpointRequest(BaseModel):
    """Request to set or remove a breakpoint."""
    filename: str = Field(..., description="File to set breakpoint in")
    line_number: int = Field(..., description="Line number for breakpoint")
    condition: Optional[str] = Field(default=None, description="Conditional breakpoint expression")
    temporary: bool = Field(default=False, description="Whether breakpoint is temporary")
    remove: bool = Field(default=False, description="Whether to remove the breakpoint")


class SetBreakpointResponse(BaseModel):
    """Response when setting/removing breakpoint."""
    breakpoint_id: Optional[str] = Field(default=None, description="Breakpoint identifier")
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Status message")


class StepRequest(BaseModel):
    """Request to step through code."""
    step_type: StepType = Field(..., description="Type of stepping operation")
    count: int = Field(default=1, description="Number of steps (for next/step)")
    line_number: Optional[int] = Field(default=None, description="Target line (for until)")


class StepResponse(BaseModel):
    """Response when stepping through code."""
    success: bool = Field(..., description="Whether step succeeded")
    current_file: Optional[str] = Field(default=None, description="Current file location")
    current_line: Optional[int] = Field(default=None, description="Current line number")
    current_function: Optional[str] = Field(default=None, description="Current function name")
    status: SessionStatus = Field(..., description="Session status after step")
    output: str = Field(default="", description="Debug output from step")


class InspectRequest(BaseModel):
    """Request to inspect variables or expressions."""
    expression: str = Field(..., description="Variable name or expression to inspect")
    frame_level: int = Field(default=0, description="Stack frame level (0=current)")


class InspectResponse(BaseModel):
    """Response with inspection results."""
    expression: str = Field(..., description="Expression that was inspected")
    value: Any = Field(..., description="Value of the expression")
    type_name: str = Field(..., description="Type of the value")
    repr_value: str = Field(..., description="String representation")
    success: bool = Field(..., description="Whether inspection succeeded")
    error_message: Optional[str] = Field(default=None, description="Error if inspection failed")


class ExecuteCommandRequest(BaseModel):
    """Request to execute arbitrary pdb command."""
    command: str = Field(..., description="PDB command to execute")


class ExecuteCommandResponse(BaseModel):
    """Response from executing pdb command."""
    command: str = Field(..., description="Command that was executed")
    output: str = Field(..., description="Output from command")
    success: bool = Field(..., description="Whether command succeeded")
    error_message: Optional[str] = Field(default=None, description="Error if command failed")


class SessionInfo(BaseModel):
    """Information about a debugging session."""
    session_id: str = Field(..., description="Session identifier")
    status: SessionStatus = Field(..., description="Current status")
    target_file: str = Field(..., description="File being debugged")
    current_file: Optional[str] = Field(default=None, description="Current file location")
    current_line: Optional[int] = Field(default=None, description="Current line number")
    current_function: Optional[str] = Field(default=None, description="Current function")
    breakpoints: List[Dict[str, Any]] = Field(default_factory=list, description="Active breakpoints")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")


class GetOutputResponse(BaseModel):
    """Response with debug session output."""
    session_id: str = Field(..., description="Session identifier")
    output: str = Field(..., description="Debug output")
    timestamp: str = Field(..., description="Output timestamp")
    has_more: bool = Field(default=False, description="Whether more output is available")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")