#!/usr/bin/env python3
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
