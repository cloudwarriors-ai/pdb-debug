"""
Enhanced logging system for PDB Gateway debugging operations.
"""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class PDBGatewayLogger:
    """Comprehensive logger for PDB Gateway operations."""
    
    def __init__(self, log_file: str = "/app/pdb-rest-gateway/pdb_gateway.log", 
                 console_output: bool = True, log_level: str = "INFO"):
        self.log_file = log_file
        self.console_output = console_output
        self.session_logs = {}
        
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("PDBGateway")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '🔧 %(asctime)s | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        self.log_info("PDB Gateway Logger initialized", {
            "log_file": log_file,
            "console_output": console_output,
            "log_level": log_level
        })
    
    def log_info(self, message: str, data: Optional[Dict] = None):
        """Log info level message."""
        self._log("INFO", message, data)
    
    def log_debug(self, message: str, data: Optional[Dict] = None):
        """Log debug level message."""
        self._log("DEBUG", message, data)
    
    def log_warning(self, message: str, data: Optional[Dict] = None):
        """Log warning level message."""
        self._log("WARNING", message, data)
    
    def log_error(self, message: str, data: Optional[Dict] = None):
        """Log error level message."""
        self._log("ERROR", message, data)
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None):
        """Internal logging method."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        if data:
            log_entry.update(data)
        
        # Format for file/console
        if data:
            formatted_data = json.dumps(data, indent=2, default=str)
            full_message = f"{message}\n{formatted_data}"
        else:
            full_message = message
        
        # Log using standard logger
        getattr(self.logger, level.lower())(full_message)
    
    def log_session_created(self, session_id: str, target_file: str, working_dir: str):
        """Log session creation."""
        self.log_info("DEBUG SESSION CREATED", {
            "session_id": session_id,
            "target_file": target_file,
            "working_directory": working_dir,
            "timestamp": time.time()
        })
        
        # Initialize session log
        self.session_logs[session_id] = {
            "created_at": time.time(),
            "target_file": target_file,
            "operations": []
        }
    
    def log_breakpoint_set(self, session_id: str, filename: str, line_number: int, 
                          condition: Optional[str] = None, temporary: bool = False):
        """Log breakpoint setting."""
        data = {
            "session_id": session_id,
            "filename": filename,
            "line_number": line_number,
            "condition": condition,
            "temporary": temporary,
            "breakpoint_id": f"{filename}:{line_number}"
        }
        
        self.log_info("BREAKPOINT SET", data)
        self._add_session_operation(session_id, "breakpoint_set", data)
    
    def log_breakpoint_removed(self, session_id: str, filename: str, line_number: int):
        """Log breakpoint removal."""
        data = {
            "session_id": session_id,
            "filename": filename,
            "line_number": line_number,
            "breakpoint_id": f"{filename}:{line_number}"
        }
        
        self.log_info("BREAKPOINT REMOVED", data)
        self._add_session_operation(session_id, "breakpoint_removed", data)
    
    def log_step_operation(self, session_id: str, step_type: str, count: int = 1,
                          result: Optional[Dict] = None):
        """Log step operation."""
        data = {
            "session_id": session_id,
            "step_type": step_type,
            "count": count,
            "success": result.get("success", False) if result else None,
            "current_location": {
                "file": result.get("current_file") if result else None,
                "line": result.get("current_line") if result else None
            }
        }
        
        self.log_info(f"STEP OPERATION: {step_type.upper()}", data)
        self._add_session_operation(session_id, "step", data)
    
    def log_variable_inspection(self, session_id: str, expression: str, 
                               result: Optional[Dict] = None):
        """Log variable inspection."""
        data = {
            "session_id": session_id,
            "expression": expression,
            "success": result.get("success", False) if result else None,
            "type_name": result.get("type_name") if result else None,
            "value_preview": result.get("repr_value", "")[:100] + "..." if result and result.get("repr_value") else None
        }
        
        self.log_info("VARIABLE INSPECTION", data)
        self._add_session_operation(session_id, "inspect", data)
    
    def log_command_execution(self, session_id: str, command: str, 
                             result: Optional[Dict] = None):
        """Log command execution."""
        data = {
            "session_id": session_id,
            "command": command,
            "success": result.get("success", False) if result else None,
            "output_length": len(result.get("output", "")) if result else 0
        }
        
        self.log_info("COMMAND EXECUTION", data)
        self._add_session_operation(session_id, "command", data)
    
    def log_session_terminated(self, session_id: str, reason: str = "manual"):
        """Log session termination."""
        data = {
            "session_id": session_id,
            "reason": reason,
            "duration": time.time() - self.session_logs.get(session_id, {}).get("created_at", time.time())
        }
        
        self.log_info("DEBUG SESSION TERMINATED", data)
        
        # Final session summary
        if session_id in self.session_logs:
            session_log = self.session_logs[session_id]
            operations_summary = {}
            for op in session_log["operations"]:
                op_type = op["operation_type"]
                operations_summary[op_type] = operations_summary.get(op_type, 0) + 1
            
            self.log_info("SESSION SUMMARY", {
                "session_id": session_id,
                "total_operations": len(session_log["operations"]),
                "operations_breakdown": operations_summary,
                "duration_seconds": data["duration"]
            })
            
            # Clean up session log
            del self.session_logs[session_id]
    
    def log_error_occurred(self, session_id: str, operation: str, error: str):
        """Log error during operation."""
        data = {
            "session_id": session_id,
            "operation": operation,
            "error": error
        }
        
        self.log_error("OPERATION ERROR", data)
        self._add_session_operation(session_id, "error", data)
    
    def _add_session_operation(self, session_id: str, operation_type: str, data: Dict):
        """Add operation to session log."""
        if session_id in self.session_logs:
            self.session_logs[session_id]["operations"].append({
                "timestamp": time.time(),
                "operation_type": operation_type,
                "data": data
            })
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of session operations."""
        if session_id in self.session_logs:
            session_log = self.session_logs[session_id]
            operations_summary = {}
            for op in session_log["operations"]:
                op_type = op["operation_type"]
                operations_summary[op_type] = operations_summary.get(op_type, 0) + 1
            
            return {
                "session_id": session_id,
                "target_file": session_log["target_file"],
                "duration": time.time() - session_log["created_at"],
                "total_operations": len(session_log["operations"]),
                "operations_breakdown": operations_summary,
                "recent_operations": session_log["operations"][-5:]  # Last 5 operations
            }
        return None
    
    def export_session_log(self, session_id: str, output_file: str):
        """Export detailed session log to file."""
        if session_id in self.session_logs:
            session_data = {
                "session_id": session_id,
                "export_timestamp": datetime.now().isoformat(),
                **self.session_logs[session_id]
            }
            
            with open(output_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            self.log_info("SESSION LOG EXPORTED", {
                "session_id": session_id,
                "output_file": output_file,
                "operations_count": len(session_data["operations"])
            })


# Global logger instance
_logger = None

def get_logger() -> PDBGatewayLogger:
    """Get global logger instance."""
    global _logger
    if _logger is None:
        _logger = PDBGatewayLogger()
    return _logger

def init_logger(log_file: str = "/app/pdb-rest-gateway/pdb_gateway.log", 
               console_output: bool = True, log_level: str = "INFO") -> PDBGatewayLogger:
    """Initialize global logger."""
    global _logger
    _logger = PDBGatewayLogger(log_file, console_output, log_level)
    return _logger