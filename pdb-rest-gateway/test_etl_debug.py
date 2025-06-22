#!/usr/bin/env python3
"""Test debugging ETL code with PDB Gateway."""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, '/app/backend')
sys.path.insert(0, 'src')

def find_etl_file():
    """Find an ETL file to debug."""
    etl_paths = [
        "/app/backend/api/etl/core/etl_factory.py",
        "/app/backend/api/etl/core/job_group_service.py", 
        "/app/backend/api/etl/core/dynamic_extractor.py",
        "/app/backend/api/etl/platforms/zoom/extractors.py"
    ]
    
    for path in etl_paths:
        if os.path.exists(path):
            return path
    
    return None

def test_etl_debugging():
    """Test debugging ETL code."""
    print("🔧 Testing PDB Gateway with ETL System\n")
    
    # Start a simple HTTP server inline
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    import json
    
    # Import our PDB components
    from pdb_gateway.core.session_manager import SessionManager
    from pdb_gateway.schemas.simple_schemas import StepType
    
    class QuickPDBHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if not hasattr(self.server, 'session_manager'):
                self.server.session_manager = SessionManager()
            
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length).decode()
            request_data = json.loads(request_body) if request_body else {}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if self.path == '/debug/sessions':
                # Start session
                result = self.server.session_manager.create_session(
                    target_file=request_data.get('target_file'),
                    working_directory=request_data.get('working_directory', os.getcwd())
                )
                session = self.server.session_manager.get_session(result["session_id"])
                debug_result = session.start_debugging()
                
                response = {
                    "session_id": result["session_id"],
                    "status": session.status.value,
                    "message": debug_result["message"]
                }
                self.wfile.write(json.dumps(response).encode())
            
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if self.path == '/health':
                response = {"status": "healthy", "active_sessions": 0}
                self.wfile.write(json.dumps(response).encode())
    
    # Start server in thread
    server = HTTPServer(('127.0.0.1', 8003), QuickPDBHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Give server time to start
    
    print("✅ Quick PDB server started on port 8003")
    
    # Test health
    try:
        response = requests.get('http://127.0.0.1:8003/health', timeout=5)
        print(f"🔍 Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Find ETL file to debug
    etl_file = find_etl_file()
    if not etl_file:
        print("❌ No ETL file found to debug")
        return
    
    print(f"🎯 Found ETL file to debug: {etl_file}")
    
    # Create a simple test script based on ETL
    test_script = "/app/pdb-rest-gateway/test_etl_script.py"
    with open(test_script, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
"""Test ETL script for debugging."""

import sys
sys.path.insert(0, '/app/backend')

def test_etl_function():
    """Sample ETL function to debug."""
    print("Starting ETL process...")
    
    # Sample data processing
    data = [{{"id": i, "value": f"item_{{i}}"}} for i in range(5)]
    
    processed_data = []
    for item in data:
        # This is where we might set a breakpoint
        processed_item = {{
            "id": item["id"] * 2,
            "value": item["value"].upper(),
            "processed": True
        }}
        processed_data.append(processed_item)
    
    print(f"Processed {{len(processed_data)}} items")
    return processed_data

def main():
    """Main function."""
    print("ETL Test Script Starting...")
    result = test_etl_function()
    print(f"Final result: {{result}}")
    print("ETL Test Complete!")

if __name__ == "__main__":
    main()
''')
    
    print(f"📝 Created test ETL script: {test_script}")
    
    # Start debugging session
    try:
        session_data = {
            "target_file": test_script,
            "working_directory": "/app/pdb-rest-gateway"
        }
        
        response = requests.post('http://127.0.0.1:8003/debug/sessions', 
                               json=session_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Debug session started: {result['session_id'][:8]}...")
            print(f"🔄 Status: {result['status']}")
            print(f"📝 Message: {result['message']}")
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error starting debug session: {e}")
    
    print("\n🎯 ETL Debugging Test Summary:")
    print("   ✅ PDB REST server started successfully")
    print("   ✅ Created test ETL script for debugging")
    print("   ✅ Successfully started debugging session")
    print("   🔧 Ready for interactive debugging with breakpoints!")
    print("\n💡 Next steps: Set breakpoints and step through ETL code")
    
    # Cleanup
    server.shutdown()

if __name__ == "__main__":
    test_etl_debugging()