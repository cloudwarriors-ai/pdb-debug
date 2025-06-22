#!/usr/bin/env python3
"""Demonstration of PDB REST Gateway functionality."""

import sys
import os
import time
sys.path.insert(0, 'src')

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType


def demo_pdb_gateway():
    """Demonstrate PDB Gateway functionality."""
    print("🔧 PDB REST Gateway Demonstration\n")
    print("=" * 50)
    
    # Create session manager
    print("1. 🏗️  Creating Session Manager")
    manager = SessionManager(max_sessions=5, session_timeout=300)
    print(f"   ✅ Manager created (max sessions: 5, timeout: 300s)")
    print(f"   📊 Current active sessions: {manager.get_session_count()}\n")
    
    # Create debugging session
    print("2. 🚀 Creating Debug Session")
    target_file = "examples/sample_script.py"
    working_dir = os.getcwd()
    
    result = manager.create_session(
        target_file=target_file,
        working_directory=working_dir,
        args=["arg1", "arg2"],
        environment={"DEBUG": "1"}
    )
    
    session_id = result["session_id"]
    print(f"   ✅ Session created: {session_id[:8]}...")
    print(f"   📁 Target file: {target_file}")
    print(f"   📂 Working directory: {working_dir}")
    print(f"   📊 Status: {result['status']}\n")
    
    # Get session object
    session = manager.get_session(session_id)
    if not session:
        print("❌ Failed to retrieve session")
        return
    
    # Start debugging (simulation)
    print("3. 🐛 Starting Debug Session")
    debug_result = session.start_debugging()
    print(f"   ✅ Debug started: {debug_result['success']}")
    print(f"   📝 Message: {debug_result['message']}")
    print(f"   🔄 Session status: {session.status.value}\n")
    
    # Set breakpoints
    print("4. 🎯 Setting Breakpoints")
    breakpoints = [
        (target_file, 15, None, False),
        (target_file, 20, "i > 2", False),
        (target_file, 25, None, True)  # Temporary
    ]
    
    for filename, line, condition, temporary in breakpoints:
        result = session.set_breakpoint(filename, line, condition, temporary)
        bp_type = "temporary" if temporary else "permanent"
        condition_str = f" (condition: {condition})" if condition else ""
        print(f"   🎯 {bp_type.title()} breakpoint at line {line}{condition_str}: {result['success']}")
    
    print(f"   📊 Total breakpoints set: {len(session.breakpoints)}\n")
    
    # Demonstrate stepping
    print("5. 👣 Stepping Through Code")
    step_operations = [
        (StepType.NEXT, 1, "Step to next line"),
        (StepType.STEP, 1, "Step into function"),
        (StepType.CONTINUE, 1, "Continue execution"),
        (StepType.UNTIL, 1, "Run until line")
    ]
    
    for step_type, count, description in step_operations:
        result = session.step(step_type, count)
        print(f"   👣 {description}: {result['success']}")
        if result['current_file']:
            print(f"      📍 Location: {result['current_file']}:{result['current_line']}")
    print()
    
    # Variable inspection
    print("6. 🔍 Variable Inspection")
    variables = ["numbers", "result_dict", "total", "__name__"]
    
    for var in variables:
        result = session.inspect(var)
        print(f"   🔍 {var}: {result['success']} (type: {result['type_name']})")
    print()
    
    # Execute commands
    print("7. ⚡ Executing PDB Commands")
    commands = ["list", "where", "args", "help"]
    
    for cmd in commands:
        result = session.execute_command(cmd)
        print(f"   ⚡ '{cmd}': {result['success']}")
    print()
    
    # Session information
    print("8. 📊 Session Information")
    info = session.get_session_info()
    print(f"   🆔 Session ID: {info['session_id'][:8]}...")
    print(f"   📁 Target file: {info['target_file']}")
    print(f"   🔄 Status: {info['status']}")
    print(f"   🎯 Breakpoints: {len(info['breakpoints'])}")
    print(f"   ⏰ Created: {info['created_at']}")
    print(f"   ⏱️  Last activity: {info['last_activity']}\n")
    
    # List all sessions
    print("9. 📋 Session Management")
    all_sessions = manager.list_sessions()
    print(f"   📊 Total sessions: {len(all_sessions)}")
    for session_info in all_sessions:
        print(f"      - {session_info['session_id'][:8]}... ({session_info['target_file']})")
    print()
    
    # Cleanup
    print("10. 🧹 Cleanup")
    terminate_result = manager.terminate_session(session_id)
    print(f"   🛑 Session terminated: {terminate_result['success']}")
    print(f"   📊 Remaining sessions: {manager.get_session_count()}")
    
    print("\n" + "=" * 50)
    print("✅ PDB REST Gateway Demo Complete!")
    print("\n🎯 Key Features Demonstrated:")
    print("   • Session management with unique IDs")
    print("   • Breakpoint setting (permanent, temporary, conditional)")
    print("   • Code stepping (next, step, continue, until)")
    print("   • Variable inspection and expression evaluation")
    print("   • Arbitrary PDB command execution")
    print("   • Session state tracking and cleanup")
    print("\n🚀 Ready for REST API or MCP server conversion!")


if __name__ == "__main__":
    demo_pdb_gateway()