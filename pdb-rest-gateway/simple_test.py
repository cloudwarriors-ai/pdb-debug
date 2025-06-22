#!/usr/bin/env python3
"""Simple test of PDB session without FastAPI dependencies."""

import sys
import os
sys.path.insert(0, 'src')

from pdb_gateway.core.pdb_session import PdbSession
from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType


def test_pdb_session():
    """Test PDB session functionality."""
    print("=== Testing PDB Session ===\n")
    
    # Test session creation
    print("1. Creating PDB session...")
    session = PdbSession(
        session_id="test-123",
        target_file="examples/sample_script.py",
        working_directory=os.getcwd()
    )
    print(f"Session created: {session.session_id}")
    print(f"Target file: {session.target_file}")
    print(f"Status: {session.status}\n")
    
    # Test session info
    print("2. Getting session info...")
    info = session.get_session_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Test breakpoint setting (without actual debugging)
    print("3. Testing breakpoint setting...")
    result = session.set_breakpoint("examples/sample_script.py", 15)
    print(f"Breakpoint result: {result}")
    print(f"Breakpoints: {session.breakpoints}\n")
    
    # Test command execution (simulation)
    print("4. Testing command execution...")
    result = session.execute_command("list")
    print(f"Execute result: {result}\n")
    
    # Test inspection (simulation)
    print("5. Testing variable inspection...")
    result = session.inspect("numbers")
    print(f"Inspect result: {result}\n")
    
    # Test step (simulation)
    print("6. Testing step operation...")
    result = session.step(StepType.NEXT)
    print(f"Step result: {result}\n")
    
    # Test termination
    print("7. Terminating session...")
    result = session.terminate()
    print(f"Termination result: {result}")
    print(f"Final status: {session.status}\n")
    
    print("=== Session Test Complete ===\n")


def test_session_manager():
    """Test session manager functionality."""
    print("=== Testing Session Manager ===\n")
    
    # Create manager
    print("1. Creating session manager...")
    manager = SessionManager(max_sessions=3, session_timeout=60)
    print(f"Manager created with max_sessions=3\n")
    
    # Create sessions
    print("2. Creating multiple sessions...")
    for i in range(3):
        result = manager.create_session(
            target_file=f"script_{i}.py",
            working_directory=os.getcwd()
        )
        print(f"Session {i}: {result}")
    print()
    
    # List sessions
    print("3. Listing sessions...")
    sessions = manager.list_sessions()
    for session in sessions:
        print(f"  {session}")
    print()
    
    # Test session limit
    print("4. Testing session limit...")
    try:
        result = manager.create_session("overflow.py")
        print(f"Overflow session: {result}")
    except RuntimeError as e:
        print(f"Expected error: {e}")
    print()
    
    # Terminate all
    print("5. Terminating all sessions...")
    result = manager.terminate_all_sessions()
    print(f"Termination result: {result}")
    print(f"Remaining sessions: {manager.get_session_count()}\n")
    
    print("=== Manager Test Complete ===\n")


if __name__ == "__main__":
    try:
        test_pdb_session()
        test_session_manager()
        print("🎉 All tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()