#!/usr/bin/env python3
"""Test script for PDB REST API Gateway."""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://127.0.0.1:8001"


def test_api():
    """Test the PDB REST API."""
    print("=== PDB REST Gateway API Test ===\n")
    
    # 1. Check health
    print("1. Health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 2. Start debugging session
    print("2. Starting debugging session...")
    session_data = {
        "target_file": "sample_script.py",
        "working_directory": str(Path(__file__).parent)
    }
    
    response = requests.post(f"{BASE_URL}/debug/sessions", json=session_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return
    
    session_info = response.json()
    session_id = session_info["session_id"]
    print(f"Session created: {session_id}")
    print(f"Response: {session_info}\n")
    
    # 3. List sessions
    print("3. Listing active sessions...")
    response = requests.get(f"{BASE_URL}/debug/sessions")
    print(f"Status: {response.status_code}")
    print(f"Sessions: {response.json()}\n")
    
    # 4. Set breakpoint
    print("4. Setting breakpoint...")
    breakpoint_data = {
        "filename": "sample_script.py",
        "line_number": 15,
        "condition": None,
        "temporary": False,
        "remove": False
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/breakpoint",
        json=breakpoint_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 5. Step through code
    print("5. Stepping through code...")
    step_data = {
        "step_type": "next",
        "count": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/step",
        json=step_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 6. Inspect variable
    print("6. Inspecting variable...")
    inspect_data = {
        "expression": "numbers",
        "frame_level": 0
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/inspect",
        json=inspect_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 7. Execute command
    print("7. Executing pdb command...")
    execute_data = {
        "command": "list"
    }
    
    response = requests.post(
        f"{BASE_URL}/debug/sessions/{session_id}/execute",
        json=execute_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 8. Get output
    print("8. Getting debug output...")
    response = requests.get(f"{BASE_URL}/debug/sessions/{session_id}/output")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 9. Get session info
    print("9. Getting session info...")
    response = requests.get(f"{BASE_URL}/debug/sessions/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 10. Terminate session
    print("10. Terminating session...")
    response = requests.delete(f"{BASE_URL}/debug/sessions/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the server is running with:")
        print("uvicorn src.pdb_gateway.api.main:app --reload --port 8001")
    except Exception as e:
        print(f"Error: {e}")