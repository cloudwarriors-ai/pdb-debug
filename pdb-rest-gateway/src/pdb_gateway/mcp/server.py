#!/usr/bin/env python3
"""MCP Server for PDB Gateway - Enables AI assistants to debug Python code."""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType, SessionStatus


class PdbMCPServer:
    """MCP Server for PDB Gateway debugging tools."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define MCP tools for debugging operations."""
        return [
            {
                "name": "pdb_start_session",
                "description": "Start a new Python debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_file": {
                            "type": "string",
                            "description": "Python file to debug"
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command line arguments for the script"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "Working directory for the script"
                        },
                        "environment": {
                            "type": "object",
                            "description": "Environment variables"
                        }
                    },
                    "required": ["target_file"]
                }
            },
            {
                "name": "pdb_set_breakpoint",
                "description": "Set or remove a breakpoint in debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        },
                        "filename": {
                            "type": "string",
                            "description": "File to set breakpoint in"
                        },
                        "line_number": {
                            "type": "integer",
                            "description": "Line number for breakpoint"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Conditional breakpoint expression"
                        },
                        "temporary": {
                            "type": "boolean",
                            "description": "Whether breakpoint is temporary"
                        },
                        "remove": {
                            "type": "boolean",
                            "description": "Whether to remove the breakpoint"
                        }
                    },
                    "required": ["session_id", "filename", "line_number"]
                }
            },
            {
                "name": "pdb_step",
                "description": "Step through code in debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        },
                        "step_type": {
                            "type": "string",
                            "enum": ["next", "step", "continue", "until", "return"],
                            "description": "Type of stepping operation"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of steps (for next/step)"
                        },
                        "line_number": {
                            "type": "integer",
                            "description": "Target line (for until)"
                        }
                    },
                    "required": ["session_id", "step_type"]
                }
            },
            {
                "name": "pdb_inspect",
                "description": "Inspect variables or expressions in debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        },
                        "expression": {
                            "type": "string",
                            "description": "Variable name or expression to inspect"
                        },
                        "frame_level": {
                            "type": "integer",
                            "description": "Stack frame level (0=current)"
                        }
                    },
                    "required": ["session_id", "expression"]
                }
            },
            {
                "name": "pdb_execute",
                "description": "Execute arbitrary PDB command in debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        },
                        "command": {
                            "type": "string",
                            "description": "PDB command to execute"
                        }
                    },
                    "required": ["session_id", "command"]
                }
            },
            {
                "name": "pdb_get_output",
                "description": "Get debugging output from session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "pdb_list_sessions",
                "description": "List all active debugging sessions",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "pdb_get_session_info",
                "description": "Get detailed information about a debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "pdb_terminate_session",
                "description": "Terminate a debugging session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Debugging session ID"
                        }
                    },
                    "required": ["session_id"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a debugging tool."""
        try:
            if name == "pdb_start_session":
                return await self._start_session(arguments)
            elif name == "pdb_set_breakpoint":
                return await self._set_breakpoint(arguments)
            elif name == "pdb_step":
                return await self._step(arguments)
            elif name == "pdb_inspect":
                return await self._inspect(arguments)
            elif name == "pdb_execute":
                return await self._execute(arguments)
            elif name == "pdb_get_output":
                return await self._get_output(arguments)
            elif name == "pdb_list_sessions":
                return await self._list_sessions(arguments)
            elif name == "pdb_get_session_info":
                return await self._get_session_info(arguments)
            elif name == "pdb_terminate_session":
                return await self._terminate_session(arguments)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    async def _start_session(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new debugging session."""
        result = self.session_manager.create_session(
            target_file=args["target_file"],
            args=args.get("args"),
            working_directory=args.get("working_directory"),
            environment=args.get("environment")
        )
        
        session = self.session_manager.get_session(result["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Failed to create session"
            }
        
        debug_result = session.start_debugging()
        
        return {
            "success": True,
            "session_id": result["session_id"],
            "status": session.status.value,
            "message": debug_result["message"],
            "target_file": args["target_file"]
        }
    
    async def _set_breakpoint(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set or remove a breakpoint."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        result = session.set_breakpoint(
            filename=args["filename"],
            line_number=args["line_number"],
            condition=args.get("condition"),
            temporary=args.get("temporary", False),
            remove=args.get("remove", False)
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "breakpoint_id": result.get("breakpoint_id"),
            "session_id": args["session_id"]
        }
    
    async def _step(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Step through code."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        step_type = StepType(args["step_type"])
        result = session.step(
            step_type=step_type,
            count=args.get("count", 1),
            line_number=args.get("line_number")
        )
        
        return {
            "success": result["success"],
            "current_file": result.get("current_file"),
            "current_line": result.get("current_line"),
            "current_function": result.get("current_function"),
            "status": result.get("status"),
            "output": result.get("output", ""),
            "session_id": args["session_id"]
        }
    
    async def _inspect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect a variable or expression."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        result = session.inspect(
            expression=args["expression"],
            frame_level=args.get("frame_level", 0)
        )
        
        return {
            "success": result["success"],
            "expression": result["expression"],
            "value": result["value"],
            "type_name": result["type_name"],
            "repr_value": result["repr_value"],
            "error_message": result.get("error_message"),
            "session_id": args["session_id"]
        }
    
    async def _execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a PDB command."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        result = session.execute_command(args["command"])
        
        return {
            "success": result["success"],
            "command": result["command"],
            "output": result["output"],
            "error_message": result.get("error_message"),
            "session_id": args["session_id"]
        }
    
    async def _get_output(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get debugging output."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        output = session.get_output()
        
        return {
            "success": True,
            "session_id": args["session_id"],
            "output": output,
            "timestamp": session.last_activity
        }
    
    async def _list_sessions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all active sessions."""
        sessions = self.session_manager.list_sessions()
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
    
    async def _get_session_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get session information."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        info = session.get_session_info()
        
        return {
            "success": True,
            **info
        }
    
    async def _terminate_session(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate a session."""
        result = self.session_manager.terminate_session(args["session_id"])
        
        return {
            "success": result["success"],
            "message": result["message"],
            "session_id": args["session_id"]
        }


# MCP Protocol Implementation (Simplified)
async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol request."""
    server = PdbMCPServer()
    
    if request.get("method") == "tools/list":
        return {
            "tools": server.tools
        }
    elif request.get("method") == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        result = await server.call_tool(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    else:
        return {
            "error": f"Unknown method: {request.get('method')}"
        }


async def main():
    """Main MCP server loop."""
    print("🔧 PDB MCP Server Starting...")
    print("📚 Available tools:")
    
    server = PdbMCPServer()
    for tool in server.tools:
        print(f"   • {tool['name']}: {tool['description']}")
    
    print("\n⚡ MCP Server ready for debugging requests!")
    print("📝 Example usage in Claude Code:")
    print("   - Start session: pdb_start_session")
    print("   - Set breakpoint: pdb_set_breakpoint")
    print("   - Step through: pdb_step")
    print("   - Inspect vars: pdb_inspect")
    print("\n🎯 Ready to help AI assistants debug Python code!")
    
    # In a real MCP server, this would handle stdin/stdout communication
    # For now, we'll just keep the server alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped.")


if __name__ == "__main__":
    asyncio.run(main())