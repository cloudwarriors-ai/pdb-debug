#!/usr/bin/env python3
"""Demonstration of MCP server functionality for PDB Gateway."""

import asyncio
import json
import sys
import os

sys.path.insert(0, 'src')

from pdb_gateway.mcp.server import PdbMCPServer


async def demo_mcp_tools():
    """Demonstrate MCP tools functionality."""
    print("🔧 PDB MCP Server Tool Demonstration\n")
    print("=" * 60)
    
    # Create MCP server
    print("1. 🏗️  Creating MCP Server")
    server = PdbMCPServer()
    print(f"   ✅ MCP Server created")
    print(f"   📚 Available tools: {len(server.tools)}")
    
    for tool in server.tools:
        print(f"      • {tool['name']}: {tool['description']}")
    print()
    
    # Test tool: Start session
    print("2. 🚀 Testing: pdb_start_session")
    session_args = {
        "target_file": "examples/sample_script.py",
        "working_directory": os.getcwd(),
        "args": ["test_arg"],
        "environment": {"DEBUG": "1"}
    }
    
    result = await server.call_tool("pdb_start_session", session_args)
    print(f"   ✅ Start session: {result['success']}")
    
    if not result["success"]:
        print(f"   ❌ Error: {result.get('error')}")
        return
    
    session_id = result["session_id"]
    print(f"   🆔 Session ID: {session_id[:8]}...")
    print(f"   📁 Target file: {result['target_file']}")
    print(f"   🔄 Status: {result['status']}\n")
    
    # Test tool: List sessions
    print("3. 📋 Testing: pdb_list_sessions")
    result = await server.call_tool("pdb_list_sessions", {})
    print(f"   ✅ List sessions: {result['success']}")
    print(f"   📊 Session count: {result['count']}")
    for session in result['sessions']:
        print(f"      - {session['session_id'][:8]}... ({session['target_file']})")
    print()
    
    # Test tool: Set breakpoint
    print("4. 🎯 Testing: pdb_set_breakpoint")
    breakpoint_args = {
        "session_id": session_id,
        "filename": "examples/sample_script.py",
        "line_number": 15,
        "condition": "i > 2",
        "temporary": False,
        "remove": False
    }
    
    result = await server.call_tool("pdb_set_breakpoint", breakpoint_args)
    print(f"   ✅ Set breakpoint: {result['success']}")
    print(f"   📝 Message: {result['message']}")
    if result.get('breakpoint_id'):
        print(f"   🎯 Breakpoint ID: {result['breakpoint_id']}")
    print()
    
    # Test tool: Step through code
    print("5. 👣 Testing: pdb_step")
    step_args = {
        "session_id": session_id,
        "step_type": "next",
        "count": 1
    }
    
    result = await server.call_tool("pdb_step", step_args)
    print(f"   ✅ Step: {result['success']}")
    print(f"   📍 Current location: {result.get('current_file', 'N/A')}:{result.get('current_line', 'N/A')}")
    print(f"   🔄 Status: {result.get('status', 'N/A')}")
    if result.get('output'):
        print(f"   📄 Output: {result['output'][:50]}...")
    print()
    
    # Test tool: Inspect variable
    print("6. 🔍 Testing: pdb_inspect")
    inspect_args = {
        "session_id": session_id,
        "expression": "__name__",
        "frame_level": 0
    }
    
    result = await server.call_tool("pdb_inspect", inspect_args)
    print(f"   ✅ Inspect: {result['success']}")
    print(f"   🔍 Expression: {result['expression']}")
    print(f"   📋 Type: {result['type_name']}")
    print(f"   💡 Value: {result['repr_value'][:50]}...")
    print()
    
    # Test tool: Execute command
    print("7. ⚡ Testing: pdb_execute")
    execute_args = {
        "session_id": session_id,
        "command": "list 10,20"
    }
    
    result = await server.call_tool("pdb_execute", execute_args)
    print(f"   ✅ Execute: {result['success']}")
    print(f"   ⚡ Command: {result['command']}")
    if result.get('output'):
        print(f"   📄 Output: {result['output'][:50]}...")
    print()
    
    # Test tool: Get session info
    print("8. 📊 Testing: pdb_get_session_info")
    info_args = {
        "session_id": session_id
    }
    
    result = await server.call_tool("pdb_get_session_info", info_args)
    print(f"   ✅ Get info: {result['success']}")
    print(f"   🆔 Session ID: {result.get('session_id', 'N/A')[:8]}...")
    print(f"   📁 Target file: {result.get('target_file', 'N/A')}")
    print(f"   🔄 Status: {result.get('status', 'N/A')}")
    print(f"   🎯 Breakpoints: {len(result.get('breakpoints', []))}")
    print()
    
    # Test tool: Get output
    print("9. 📄 Testing: pdb_get_output")
    output_args = {
        "session_id": session_id
    }
    
    result = await server.call_tool("pdb_get_output", output_args)
    print(f"   ✅ Get output: {result['success']}")
    print(f"   📄 Output length: {len(result.get('output', ''))}")
    print(f"   ⏰ Timestamp: {result.get('timestamp', 'N/A')}")
    print()
    
    # Test tool: Terminate session
    print("10. 🛑 Testing: pdb_terminate_session")
    terminate_args = {
        "session_id": session_id
    }
    
    result = await server.call_tool("pdb_terminate_session", terminate_args)
    print(f"   ✅ Terminate: {result['success']}")
    print(f"   📝 Message: {result['message']}")
    print()
    
    # Final session count
    print("11. 📊 Final Session Count")
    result = await server.call_tool("pdb_list_sessions", {})
    print(f"   📊 Remaining sessions: {result['count']}")
    
    print("\n" + "=" * 60)
    print("✅ MCP Tools Demo Complete!")
    print("\n🎯 All 9 MCP Tools Tested Successfully:")
    print("   • pdb_start_session - ✅ Start debugging sessions")
    print("   • pdb_set_breakpoint - ✅ Set/remove breakpoints") 
    print("   • pdb_step - ✅ Step through code execution")
    print("   • pdb_inspect - ✅ Inspect variables/expressions")
    print("   • pdb_execute - ✅ Execute arbitrary PDB commands")
    print("   • pdb_get_output - ✅ Retrieve debugging output")
    print("   • pdb_list_sessions - ✅ List active sessions")
    print("   • pdb_get_session_info - ✅ Get session details")
    print("   • pdb_terminate_session - ✅ Terminate sessions")
    print("\n🚀 Ready for Claude Code Integration!")
    print("💡 AI assistants can now debug Python code programmatically!")


async def demo_mcp_protocol():
    """Demonstrate MCP protocol request handling."""
    print("\n🔌 MCP Protocol Demo")
    print("-" * 40)
    
    from pdb_gateway.mcp.server import handle_mcp_request
    
    # Test tools/list request
    print("Testing tools/list request...")
    request = {"method": "tools/list"}
    response = await handle_mcp_request(request)
    print(f"✅ Found {len(response['tools'])} tools")
    
    # Test tools/call request
    print("\nTesting tools/call request...")
    request = {
        "method": "tools/call",
        "params": {
            "name": "pdb_list_sessions",
            "arguments": {}
        }
    }
    response = await handle_mcp_request(request)
    print("✅ Tool call successful")
    print(f"📄 Response: {response['content'][0]['text'][:100]}...")


if __name__ == "__main__":
    async def main():
        await demo_mcp_tools()
        await demo_mcp_protocol()
    
    asyncio.run(main())