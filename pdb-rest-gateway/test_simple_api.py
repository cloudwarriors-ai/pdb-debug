#!/usr/bin/env python3
"""Test the simple HTTP server API."""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://127.0.0.1:8002"


def test_simple_api():
    """Test the simple PDB REST API."""
    print("🧪 Testing PDB REST Gateway Simple API\n")
    
    # 1. Health check
    print("1. 🔍 Health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start with: python3 simple_server.py")
        return
    
    # 2. Start debugging session
    print("2. 🚀 Starting debugging session...")
    session_data = {
        "target_file": "examples/sample_script.py",
        "working_directory": str(Path.cwd())
    }
    
    response = requests.post(f"{BASE_URL}/debug/sessions", json=session_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.text}")
        return
    
    session_info = response.json()
    session_id = session_info["session_id"]
    print(f"   ✅ Session created: {session_id[:8]}...")
    print(f"   📊 Response: {session_info}\n")
    
    # 3. List sessions
    print("3. 📋 Listing active sessions...")
    response = requests.get(f"{BASE_URL}/debug/sessions")
    sessions = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   📝 Active sessions: {len(sessions)}")
    for session in sessions:
        print(f"      - {session['session_id'][:8]}... ({session['target_file']})")
    print()
    
    # 4. Set breakpoint
    print("4. 🎯 Setting breakpoint...")
    breakpoint_data = {
        "filename": "examples/sample_script.py",
        "line_number": 15,
        "remove": False
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/breakpoint",
        json=breakpoint_data
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   🎯 Breakpoint: {result['success']} - {result['message']}\n")
    
    # 5. Step through code
    print("5. 👣 Stepping through code...")
    step_data = {
        "step_type": "next",
        "count": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/step",
        json=step_data
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   👣 Step result: {result['success']}")
    print(f"   📍 Current location: {result.get('current_file', 'N/A')}:{result.get('current_line', 'N/A')}\n")
    
    # 6. Get debug output
    print("6. 📄 Getting debug output...")
    response = requests.get(f"{BASE_URL}/debug/sessions/{session_id}/output")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   📄 Output length: {len(result.get('output', ''))}")
    if result.get('output'):
        print(f"   📝 Sample output: {result['output'][:100]}...")
    print()
    
    # 7. Test another step
    print("7. 👣 Another step...")
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/step",
        json={"step_type": "continue"}
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   👣 Continue result: {result['success']}\n")
    
    # 8. Terminate session
    print("8. 🛑 Terminating session...")
    response = requests.delete(f"{BASE_URL}/debug/sessions/{session_id}")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   🛑 Termination: {result.get('success', False)} - {result.get('message', 'N/A')}\n")
    
    # 9. Final session count
    print("9. 📊 Final session count...")
    response = requests.get(f"{BASE_URL}/health")
    result = response.json()
    print(f"   🔢 Active sessions: {result.get('active_sessions', 0)}\n")
    
    print("🎉 Test completed successfully!")


if __name__ == "__main__":
    test_simple_api()