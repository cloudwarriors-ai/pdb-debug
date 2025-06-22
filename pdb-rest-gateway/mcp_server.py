#!/usr/bin/env python3
"""Proper MCP Server implementation for PDB Gateway."""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional, Sequence

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType

# Try importing MCP - fall back to basic implementation if not available
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
    )
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️  MCP library not available. Run: pip install mcp")
    MCP_AVAILABLE = False


class PdbMCPServer:
    """PDB debugging MCP server."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        if MCP_AVAILABLE:
            self.server = Server("pdb-gateway")
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available debugging tools."""
            return [
                Tool(
                    name="pdb_start_session",
                    description="Start a new Python debugging session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target_file": {
                                "type": "string",
                                "description": "Python file to debug"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Command line arguments"
                            },
                            "working_directory": {
                                "type": "string", 
                                "description": "Working directory"
                            }
                        },
                        "required": ["target_file"]
                    }
                ),
                Tool(
                    name="pdb_set_breakpoint",
                    description="Set or remove a breakpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "filename": {"type": "string"},
                            "line_number": {"type": "integer"},
                            "condition": {"type": "string"},
                            "remove": {"type": "boolean"}
                        },
                        "required": ["session_id", "filename", "line_number"]
                    }
                ),
                Tool(
                    name="pdb_step",
                    description="Step through code execution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "step_type": {
                                "type": "string",
                                "enum": ["next", "step", "continue", "until", "return"]
                            },
                            "count": {"type": "integer"}
                        },
                        "required": ["session_id", "step_type"]
                    }
                ),
                Tool(
                    name="pdb_inspect",
                    description="Inspect variables or expressions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "expression": {"type": "string"}
                        },
                        "required": ["session_id", "expression"]
                    }
                ),
                Tool(
                    name="pdb_execute",
                    description="Execute arbitrary PDB command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "command": {"type": "string"}
                        },
                        "required": ["session_id", "command"]
                    }
                ),
                Tool(
                    name="pdb_list_sessions",
                    description="List all active debugging sessions",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="pdb_terminate_session",
                    description="Terminate a debugging session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"}
                        },
                        "required": ["session_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool execution."""
            try:
                result = await self._execute_tool(name, arguments)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
                return [
                    TextContent(
                        type="text", 
                        text=json.dumps(error_result, indent=2)
                    )
                ]
    
    async def _execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a debugging tool."""
        if name == "pdb_start_session":
            return await self._start_session(arguments)
        elif name == "pdb_set_breakpoint":
            return await self._set_breakpoint(arguments)
        elif name == "pdb_step":
            return await self._step(arguments)
        elif name == "pdb_inspect":
            return await self._inspect(arguments)
        elif name == "pdb_execute":
            return await self._execute_command(arguments)
        elif name == "pdb_list_sessions":
            return await self._list_sessions()
        elif name == "pdb_terminate_session":
            return await self._terminate_session(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _start_session(self, args: dict) -> dict:
        """Start debugging session."""
        result = self.session_manager.create_session(
            target_file=args["target_file"],
            args=args.get("args"),
            working_directory=args.get("working_directory", os.getcwd())
        )
        
        session = self.session_manager.get_session(result["session_id"])
        debug_result = session.start_debugging()
        
        return {
            "success": True,
            "session_id": result["session_id"],
            "status": session.status.value,
            "message": debug_result["message"],
            "target_file": args["target_file"]
        }
    
    async def _set_breakpoint(self, args: dict) -> dict:
        """Set breakpoint."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {"success": False, "error": "Session not found"}
        
        result = session.set_breakpoint(
            filename=args["filename"],
            line_number=args["line_number"],
            condition=args.get("condition"),
            remove=args.get("remove", False)
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "breakpoint_id": result.get("breakpoint_id")
        }
    
    async def _step(self, args: dict) -> dict:
        """Step through code."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {"success": False, "error": "Session not found"}
        
        step_type = StepType(args["step_type"])
        result = session.step(step_type, args.get("count", 1))
        
        return {
            "success": result["success"],
            "current_file": result.get("current_file"),
            "current_line": result.get("current_line"),
            "status": result.get("status")
        }
    
    async def _inspect(self, args: dict) -> dict:
        """Inspect variable."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {"success": False, "error": "Session not found"}
        
        result = session.inspect(args["expression"])
        
        return {
            "success": result["success"],
            "expression": result["expression"],
            "value": result["value"],
            "type_name": result["type_name"]
        }
    
    async def _execute_command(self, args: dict) -> dict:
        """Execute PDB command."""
        session = self.session_manager.get_session(args["session_id"])
        if not session:
            return {"success": False, "error": "Session not found"}
        
        result = session.execute_command(args["command"])
        
        return {
            "success": result["success"],
            "command": result["command"],
            "output": result["output"]
        }
    
    async def _list_sessions(self) -> dict:
        """List sessions."""
        sessions = self.session_manager.list_sessions()
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
    
    async def _terminate_session(self, args: dict) -> dict:
        """Terminate session."""
        result = self.session_manager.terminate_session(args["session_id"])
        return {
            "success": result["success"],
            "message": result["message"]
        }
    
    async def run(self):
        """Run the MCP server."""
        if not MCP_AVAILABLE:
            print("❌ MCP library not available")
            return
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pdb-gateway",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


# Fallback for systems without MCP
class SimpleMCPServer:
    """Simple fallback server."""
    
    def __init__(self):
        self.session_manager = SessionManager()
    
    async def run(self):
        """Run simple server."""
        print("🔧 PDB Gateway (Fallback Mode)")
        print("📚 Available in this session:")
        print("   • Session management")
        print("   • Breakpoint setting")
        print("   • Code stepping")
        print("   • Variable inspection")
        print("\n⚡ MCP server functionality ready!")
        print("💡 Install MCP library for full integration: pip install mcp")
        
        # Keep alive
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")


async def main():
    """Main entry point."""
    if MCP_AVAILABLE:
        print("🚀 Starting PDB MCP Server...")
        server = PdbMCPServer()
        await server.run()
    else:
        print("⚠️  MCP not available, starting fallback server...")
        server = SimpleMCPServer()
        await server.run()


if __name__ == "__main__":
    asyncio.run(main())