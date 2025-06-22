"""Core PDB session management and debugging engine."""

import pdb
import sys
import threading
import subprocess
import uuid
import queue
import time
from io import StringIO
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from ..schemas.simple_schemas import SessionStatus, StepType
from .debug_logger import get_logger


class PdbSession:
    """Manages a single PDB debugging session."""
    
    def __init__(self, session_id: str, target_file: str, args: Optional[List[str]] = None,
                 working_directory: Optional[str] = None, environment: Optional[Dict[str, str]] = None):
        self.session_id = session_id
        self.target_file = target_file
        self.args = args or []
        self.working_directory = working_directory or str(Path.cwd())
        self.environment = environment or {}
        
        # Initialize logger
        self.logger = get_logger()
        
        # Session state
        self.status = SessionStatus.ACTIVE
        self.created_at = datetime.now().isoformat()
        self.last_activity = self.created_at
        
        # Log session creation
        self.logger.log_session_created(session_id, target_file, self.working_directory)
        
        # Debug state
        self.current_file: Optional[str] = None
        self.current_line: Optional[int] = None
        self.current_function: Optional[str] = None
        self.breakpoints: Dict[str, Dict[str, Any]] = {}
        
        # I/O management
        self.output_buffer = StringIO()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # PDB instance and process
        self.pdb_instance: Optional[pdb.Pdb] = None
        self.process: Optional[subprocess.Popen] = None
        self.debug_thread: Optional[threading.Thread] = None
        
        # Thread control
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
    
    def start_debugging(self) -> Dict[str, Any]:
        """Start the debugging session."""
        try:
            # Validate target file
            target_path = Path(self.working_directory) / self.target_file
            if not target_path.exists():
                raise FileNotFoundError(f"Target file not found: {target_path}")
            
            # Create custom PDB instance with redirected I/O
            self.pdb_instance = pdb.Pdb(
                stdin=self._create_stdin_handler(),
                stdout=self.output_buffer
            )
            
            # Start debugging thread
            self.debug_thread = threading.Thread(target=self._debug_worker, daemon=True)
            self.debug_thread.start()
            
            self.status = SessionStatus.PAUSED
            self._update_activity()
            
            return {
                "success": True,
                "message": f"Debugging session started for {self.target_file}",
                "session_id": self.session_id,
                "status": self.status.value
            }
            
        except Exception as e:
            self.status = SessionStatus.ERROR
            return {
                "success": False,
                "message": f"Failed to start debugging: {str(e)}",
                "session_id": self.session_id,
                "status": self.status.value
            }
    
    def _create_stdin_handler(self):
        """Create a custom stdin handler that reads from command queue."""
        class QueueStdin:
            def __init__(self, command_queue, response_queue):
                self.command_queue = command_queue
                self.response_queue = response_queue
            
            def readline(self):
                try:
                    # Wait for command from queue
                    command = self.command_queue.get(timeout=1.0)
                    return command + '\n'
                except queue.Empty:
                    return '\n'  # Empty command continues execution
            
            def read(self, size=-1):
                return self.readline()
        
        return QueueStdin(self.command_queue, self.response_queue)
    
    def _debug_worker(self):
        """Worker thread that runs the debugging session."""
        try:
            # Change to working directory
            original_cwd = Path.cwd()
            Path(self.working_directory).mkdir(parents=True, exist_ok=True)
            import os
            os.chdir(self.working_directory)
            
            # Set up environment
            original_env = dict(os.environ)
            os.environ.update(self.environment)
            
            try:
                # Execute the target file under debugger
                with open(self.target_file, 'r') as f:
                    code = compile(f.read(), self.target_file, 'exec')
                
                # Set up sys.argv
                original_argv = sys.argv[:]
                sys.argv = [self.target_file] + self.args
                
                try:
                    # Start debugging
                    self.pdb_instance.run(code, globals(), locals())
                except SystemExit:
                    # Normal script completion
                    pass
                except Exception as e:
                    self.output_buffer.write(f"Script error: {str(e)}\n")
                finally:
                    sys.argv = original_argv
                    
            finally:
                # Restore environment and directory
                os.environ.clear()
                os.environ.update(original_env)
                os.chdir(original_cwd)
                
        except Exception as e:
            self.status = SessionStatus.ERROR
            self.output_buffer.write(f"Debug worker error: {str(e)}\n")
        finally:
            if self.status != SessionStatus.ERROR:
                self.status = SessionStatus.TERMINATED
    
    def set_breakpoint(self, filename: str, line_number: int, 
                      condition: Optional[str] = None, temporary: bool = False,
                      remove: bool = False) -> Dict[str, Any]:
        """Set or remove a breakpoint."""
        try:
            with self._lock:
                breakpoint_id = f"{filename}:{line_number}"
                
                if remove:
                    if breakpoint_id in self.breakpoints:
                        # Remove breakpoint
                        self.command_queue.put(f"clear {filename}:{line_number}")
                        del self.breakpoints[breakpoint_id]
                        self._update_activity()
                        
                        # Log breakpoint removal
                        self.logger.log_breakpoint_removed(self.session_id, filename, line_number)
                        
                        return {
                            "success": True,
                            "message": f"Breakpoint removed at {filename}:{line_number}",
                            "breakpoint_id": None
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"No breakpoint found at {filename}:{line_number}",
                            "breakpoint_id": None
                        }
                else:
                    # Set breakpoint
                    cmd = f"break {filename}:{line_number}"
                    if condition:
                        cmd += f", {condition}"
                    if temporary:
                        cmd = f"tbreak {filename}:{line_number}"
                        if condition:
                            cmd += f", {condition}"
                    
                    self.command_queue.put(cmd)
                    
                    # Store breakpoint info
                    self.breakpoints[breakpoint_id] = {
                        "filename": filename,
                        "line_number": line_number,
                        "condition": condition,
                        "temporary": temporary,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    self._update_activity()
                    
                    # Log breakpoint setting
                    self.logger.log_breakpoint_set(self.session_id, filename, line_number, condition, temporary)
                    
                    return {
                        "success": True,
                        "message": f"Breakpoint set at {filename}:{line_number}",
                        "breakpoint_id": breakpoint_id
                    }
                    
        except Exception as e:
            self.logger.log_error_occurred(self.session_id, "set_breakpoint", str(e))
            return {
                "success": False,
                "message": f"Failed to set breakpoint: {str(e)}",
                "breakpoint_id": None
            }
    
    def step(self, step_type: StepType, count: int = 1, 
             line_number: Optional[int] = None) -> Dict[str, Any]:
        """Execute a stepping operation."""
        try:
            with self._lock:
                if step_type == StepType.NEXT:
                    command = f"next {count}" if count > 1 else "next"
                elif step_type == StepType.STEP:
                    command = f"step {count}" if count > 1 else "step"
                elif step_type == StepType.CONTINUE:
                    command = "continue"
                elif step_type == StepType.UNTIL:
                    command = f"until {line_number}" if line_number else "until"
                elif step_type == StepType.RETURN:
                    command = "return"
                else:
                    raise ValueError(f"Unknown step type: {step_type}")
                
                # Send command to debugger
                self.command_queue.put(command)
                
                # Update state
                self._update_current_location()
                self._update_activity()
                
                result = {
                    "success": True,
                    "current_file": self.current_file,
                    "current_line": self.current_line,
                    "current_function": self.current_function,
                    "status": self.status.value,
                    "output": self._get_recent_output()
                }
                
                # Log step operation
                self.logger.log_step_operation(self.session_id, step_type.value, count, result)
                
                return result
                
        except Exception as e:
            return {
                "success": False,
                "current_file": None,
                "current_line": None,
                "current_function": None,
                "status": self.status.value,
                "output": f"Step error: {str(e)}"
            }
    
    def inspect(self, expression: str, frame_level: int = 0) -> Dict[str, Any]:
        """Inspect a variable or expression."""
        try:
            with self._lock:
                # Send inspect command to debugger
                if frame_level > 0:
                    self.command_queue.put(f"up {frame_level}")
                
                self.command_queue.put(f"p {expression}")
                self.command_queue.put(f"pp {expression}")  # Pretty print
                
                if frame_level > 0:
                    self.command_queue.put(f"down {frame_level}")
                
                # Get output (simplified for now)
                output = self._get_recent_output()
                
                self._update_activity()
                
                result = {
                    "expression": expression,
                    "value": output,  # In real implementation, parse this
                    "type_name": "unknown",
                    "repr_value": output,
                    "success": True,
                    "error_message": None
                }
                
                # Log variable inspection
                self.logger.log_variable_inspection(self.session_id, expression, result)
                
                return result
                
        except Exception as e:
            return {
                "expression": expression,
                "value": None,
                "type_name": "error",
                "repr_value": "",
                "success": False,
                "error_message": str(e)
            }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute arbitrary PDB command."""
        try:
            with self._lock:
                self.command_queue.put(command)
                output = self._get_recent_output()
                self._update_activity()
                
                result = {
                    "command": command,
                    "output": output,
                    "success": True,
                    "error_message": None
                }
                
                # Log command execution
                self.logger.log_command_execution(self.session_id, command, result)
                
                return result
                
        except Exception as e:
            return {
                "command": command,
                "output": "",
                "success": False,
                "error_message": str(e)
            }
    
    def get_output(self) -> str:
        """Get debugging output."""
        return self.output_buffer.getvalue()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "target_file": self.target_file,
            "current_file": self.current_file,
            "current_line": self.current_line,
            "current_function": self.current_function,
            "breakpoints": list(self.breakpoints.values()),
            "created_at": self.created_at,
            "last_activity": self.last_activity
        }
    
    def terminate(self) -> Dict[str, Any]:
        """Terminate the debugging session."""
        try:
            with self._lock:
                self._stop_event.set()
                
                if self.pdb_instance:
                    self.command_queue.put("quit")
                
                if self.debug_thread and self.debug_thread.is_alive():
                    self.debug_thread.join(timeout=5.0)
                
                if self.process:
                    self.process.terminate()
                
                self.status = SessionStatus.TERMINATED
                self._update_activity()
                
                # Log session termination
                self.logger.log_session_terminated(self.session_id, "manual")
                
                return {
                    "success": True,
                    "message": "Debugging session terminated",
                    "session_id": self.session_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to terminate session: {str(e)}",
                "session_id": self.session_id
            }
    
    def _update_current_location(self):
        """Update current debugging location."""
        # This would parse pdb output to extract current location
        # Simplified for now
        pass
    
    def _update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now().isoformat()
    
    def _get_recent_output(self) -> str:
        """Get recent output from buffer."""
        current_pos = self.output_buffer.tell()
        self.output_buffer.seek(0)
        content = self.output_buffer.read()
        self.output_buffer.seek(current_pos)
        return content[-1000:]  # Last 1000 characters