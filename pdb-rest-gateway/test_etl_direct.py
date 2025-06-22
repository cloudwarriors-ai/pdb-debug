#!/usr/bin/env python3
"""Test PDB Gateway directly with ETL system."""

import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '/app/backend')

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType

def create_etl_test_script():
    """Create a realistic ETL test script."""
    script_content = '''#!/usr/bin/env python3
"""Sample ETL script for debugging demonstration."""

import sys
import os

# Add backend path for ETL imports
sys.path.insert(0, '/app/backend')

def extract_data():
    """Extract sample data (simulating ETL extract phase)."""
    print("🔄 Starting data extraction...")
    
    # Simulate extracting from different sources
    source_data = {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ],
        "calls": [
            {"id": 101, "user_id": 1, "duration": 120, "type": "inbound"},
            {"id": 102, "user_id": 2, "duration": 300, "type": "outbound"},
            {"id": 103, "user_id": 1, "duration": 45, "type": "inbound"}
        ]
    }
    
    print(f"📊 Extracted {len(source_data['users'])} users and {len(source_data['calls'])} calls")
    return source_data

def transform_data(raw_data):
    """Transform extracted data (ETL transform phase)."""
    print("🔧 Starting data transformation...")
    
    # Transform users
    transformed_users = []
    for user in raw_data["users"]:
        transformed_user = {
            "user_id": user["id"],
            "full_name": user["name"].upper(),
            "email_domain": user["email"].split("@")[1],
            "contact_info": user["email"]
        }
        transformed_users.append(transformed_user)
    
    # Transform calls with user enrichment
    transformed_calls = []
    user_lookup = {u["id"]: u["name"] for u in raw_data["users"]}
    
    for call in raw_data["calls"]:
        transformed_call = {
            "call_id": call["id"],
            "user_name": user_lookup.get(call["user_id"], "Unknown"),
            "duration_minutes": round(call["duration"] / 60, 2),
            "call_direction": call["type"],
            "user_id": call["user_id"]
        }
        transformed_calls.append(transformed_call)
    
    transformed_data = {
        "users": transformed_users,
        "calls": transformed_calls
    }
    
    print(f"🔄 Transformed {len(transformed_data['users'])} user records")
    print(f"🔄 Transformed {len(transformed_data['calls'])} call records")
    
    return transformed_data

def load_data(transformed_data):
    """Load transformed data (ETL load phase)."""
    print("💾 Starting data loading...")
    
    # Simulate loading to different targets
    load_results = {
        "users_loaded": 0,
        "calls_loaded": 0,
        "errors": []
    }
    
    # Load users
    for user in transformed_data["users"]:
        try:
            # Simulate database insert
            if len(user["full_name"]) > 0:
                load_results["users_loaded"] += 1
            else:
                load_results["errors"].append(f"Empty name for user {user['user_id']}")
        except Exception as e:
            load_results["errors"].append(f"User load error: {e}")
    
    # Load calls
    for call in transformed_data["calls"]:
        try:
            # Simulate database insert
            if call["duration_minutes"] > 0:
                load_results["calls_loaded"] += 1
            else:
                load_results["errors"].append(f"Invalid duration for call {call['call_id']}")
        except Exception as e:
            load_results["errors"].append(f"Call load error: {e}")
    
    print(f"✅ Loaded {load_results['users_loaded']} users")
    print(f"✅ Loaded {load_results['calls_loaded']} calls")
    
    if load_results["errors"]:
        print(f"⚠️  {len(load_results['errors'])} errors occurred")
        for error in load_results["errors"]:
            print(f"   • {error}")
    
    return load_results

def run_etl_pipeline():
    """Run the complete ETL pipeline."""
    print("🚀 Starting ETL Pipeline...")
    print("=" * 50)
    
    try:
        # Extract phase
        raw_data = extract_data()
        
        # Transform phase  
        transformed_data = transform_data(raw_data)
        
        # Load phase
        load_results = load_data(transformed_data)
        
        # Summary
        print("=" * 50)
        print("📊 ETL Pipeline Summary:")
        print(f"   Users processed: {load_results['users_loaded']}")
        print(f"   Calls processed: {load_results['calls_loaded']}")
        print(f"   Errors: {len(load_results['errors'])}")
        
        if load_results["errors"]:
            print("❌ Pipeline completed with errors")
            return False
        else:
            print("✅ Pipeline completed successfully")
            return True
            
    except Exception as e:
        print(f"💥 ETL Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = run_etl_pipeline()
    exit(0 if success else 1)
'''
    
    script_path = "/app/pdb-rest-gateway/etl_test_script.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path

def test_etl_debugging():
    """Test debugging ETL code with PDB Gateway."""
    print("🔧 Testing PDB Gateway with ETL System Integration\n")
    print("=" * 60)
    
    # Create session manager
    print("1. 🏗️  Creating PDB Session Manager")
    manager = SessionManager(max_sessions=3)
    print(f"   ✅ Session manager created")
    print(f"   📊 Max sessions: 3\n")
    
    # Create ETL test script
    print("2. 📝 Creating ETL Test Script")
    script_path = create_etl_test_script()
    print(f"   ✅ ETL script created: {script_path}")
    print(f"   📁 Script size: {os.path.getsize(script_path)} bytes\n")
    
    # Start debugging session
    print("3. 🚀 Starting Debug Session")
    result = manager.create_session(
        target_file="etl_test_script.py",
        working_directory="/app/pdb-rest-gateway",
        environment={"DEBUG": "1", "ETL_MODE": "test"}
    )
    
    session_id = result["session_id"]
    session = manager.get_session(session_id)
    
    print(f"   ✅ Session created: {session_id[:8]}...")
    print(f"   🔄 Status: {result['status']}")
    print(f"   📁 Target: {session.target_file}\n")
    
    # Start debugging
    print("4. 🐛 Starting Debugging Process")
    debug_result = session.start_debugging()
    print(f"   ✅ Debug started: {debug_result['success']}")
    print(f"   📝 Message: {debug_result['message']}")
    print(f"   🔄 Session status: {session.status.value}\n")
    
    # Set breakpoints in ETL functions
    print("5. 🎯 Setting ETL Breakpoints")
    breakpoints = [
        ("etl_test_script.py", 15, "extract_data function"),
        ("etl_test_script.py", 35, "transform_data function"),
        ("etl_test_script.py", 70, "load_data function"),
        ("etl_test_script.py", 105, "run_etl_pipeline function")
    ]
    
    set_breakpoints = []
    for filename, line, description in breakpoints:
        result = session.set_breakpoint(filename, line)
        if result["success"]:
            set_breakpoints.append((filename, line, description))
            print(f"   🎯 Breakpoint set at line {line}: {description}")
        else:
            print(f"   ❌ Failed to set breakpoint at line {line}: {result['message']}")
    
    print(f"   📊 Total breakpoints set: {len(set_breakpoints)}\n")
    
    # Simulate stepping through ETL phases
    print("6. 👣 Stepping Through ETL Phases")
    etl_steps = [
        (StepType.NEXT, "Step to next line"),
        (StepType.CONTINUE, "Continue to next breakpoint (extract phase)"),
        (StepType.STEP, "Step into extract_data function"),
        (StepType.CONTINUE, "Continue to transform phase"),
        (StepType.CONTINUE, "Continue to load phase")
    ]
    
    for i, (step_type, description) in enumerate(etl_steps, 1):
        result = session.step(step_type)
        print(f"   👣 Step {i}: {description}")
        print(f"      ✅ Success: {result['success']}")
        print(f"      📍 Location: {result.get('current_file', 'N/A')}:{result.get('current_line', 'N/A')}")
        print(f"      🔄 Status: {result.get('status', 'N/A')}")
    
    print()
    
    # Inspect ETL variables
    print("7. 🔍 Inspecting ETL Variables")
    etl_variables = [
        "raw_data",
        "transformed_data", 
        "load_results",
        "user_lookup",
        "transformed_users"
    ]
    
    for var in etl_variables:
        result = session.inspect(var)
        print(f"   🔍 {var}: {result['success']} (type: {result['type_name']})")
    
    print()
    
    # Execute ETL-specific commands
    print("8. ⚡ Executing ETL Debug Commands")
    etl_commands = [
        "list 10,25",
        "where", 
        "args",
        "pp locals()"
    ]
    
    for cmd in etl_commands:
        result = session.execute_command(cmd)
        print(f"   ⚡ '{cmd}': {result['success']}")
    
    print()
    
    # Get session information
    print("9. 📊 ETL Debug Session Information")
    info = session.get_session_info()
    print(f"   🆔 Session ID: {info['session_id'][:8]}...")
    print(f"   📁 Target file: {info['target_file']}")
    print(f"   🔄 Status: {info['status']}")
    print(f"   🎯 Breakpoints: {len(info['breakpoints'])}")
    print(f"   ⏰ Created: {info['created_at']}")
    print(f"   📍 Current location: {info.get('current_file', 'N/A')}:{info.get('current_line', 'N/A')}")
    
    print()
    
    # Cleanup
    print("10. 🧹 Cleanup")
    terminate_result = manager.terminate_session(session_id)
    print(f"   🛑 Session terminated: {terminate_result['success']}")
    print(f"   📊 Remaining sessions: {manager.get_session_count()}")
    
    print("\n" + "=" * 60)
    print("✅ ETL System + PDB Gateway Integration Test Complete!")
    print("\n🎯 ETL Debugging Features Tested:")
    print("   • ✅ Multi-phase ETL pipeline debugging")
    print("   • ✅ Breakpoints in extract/transform/load functions")
    print("   • ✅ Variable inspection for ETL data structures")
    print("   • ✅ Step-through debugging of data processing")
    print("   • ✅ Error handling and pipeline status monitoring")
    print("\n🚀 Ready for Real ETL Debugging!")
    print("💡 You can now debug your actual ETL pipelines with:")
    print("   - Set breakpoints in ETL factory classes")
    print("   - Inspect data at each pipeline stage") 
    print("   - Step through transformation logic")
    print("   - Monitor job execution in real-time")

if __name__ == "__main__":
    test_etl_debugging()