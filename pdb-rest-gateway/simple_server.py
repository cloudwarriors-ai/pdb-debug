#!/usr/bin/env python3
"""Simple HTTP server for testing PDB functionality without FastAPI."""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

sys.path.insert(0, 'src')

from pdb_gateway.core.session_manager import SessionManager
from pdb_gateway.schemas.simple_schemas import StepType


class PdbHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for PDB REST API."""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "active_sessions": self.server.session_manager.get_session_count()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/debug/sessions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            sessions = self.server.session_manager.list_sessions()
            self.wfile.write(json.dumps(sessions).encode())
            
        elif path.startswith('/debug/sessions/') and path.endswith('/output'):
            session_id = path.split('/')[-2]
            session = self.server.session_manager.get_session(session_id)
            
            if not session:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Session not found"}).encode())
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "session_id": session_id,
                "output": session.get_output(),
                "timestamp": session.last_activity
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode()
        
        try:
            request_data = json.loads(request_body) if request_body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        
        if path == '/debug/sessions':
            # Start new session
            try:
                result = self.server.session_manager.create_session(
                    target_file=request_data.get('target_file'),
                    args=request_data.get('args'),
                    working_directory=request_data.get('working_directory', os.getcwd())
                )
                
                session = self.server.session_manager.get_session(result["session_id"])
                debug_result = session.start_debugging()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {
                    "session_id": result["session_id"],
                    "status": session.status.value,
                    "message": debug_result["message"]
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif '/breakpoint' in path:
            # Set breakpoint
            session_id = path.split('/')[-2]
            session = self.server.session_manager.get_session(session_id)
            
            if not session:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Session not found"}).encode())
                return
            
            result = session.set_breakpoint(
                filename=request_data.get('filename'),
                line_number=request_data.get('line_number'),
                condition=request_data.get('condition'),
                temporary=request_data.get('temporary', False),
                remove=request_data.get('remove', False)
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif '/step' in path:
            # Step through code
            session_id = path.split('/')[-2]
            session = self.server.session_manager.get_session(session_id)
            
            if not session:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Session not found"}).encode())
                return
            
            step_type = StepType(request_data.get('step_type', 'next'))
            result = session.step(
                step_type=step_type,
                count=request_data.get('count', 1),
                line_number=request_data.get('line_number')
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        if path.startswith('/debug/sessions/') and len(path.split('/')) == 4:
            # Delete specific session
            session_id = path.split('/')[-1]
            result = self.server.session_manager.terminate_session(session_id)
            self.wfile.write(json.dumps(result).encode())
        elif path == '/debug/sessions':
            # Delete all sessions
            result = self.server.session_manager.terminate_all_sessions()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


class PdbHTTPServer(HTTPServer):
    """HTTP server with session manager."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_manager = SessionManager()


def run_server(port=8002):
    """Run the simple HTTP server."""
    server = PdbHTTPServer(('127.0.0.1', port), PdbHTTPHandler)
    print(f"🚀 PDB REST Gateway running on http://127.0.0.1:{port}")
    print("📚 Available endpoints:")
    print("  GET  /health")
    print("  GET  /debug/sessions")
    print("  POST /debug/sessions")
    print("  POST /debug/sessions/{id}/breakpoint")
    print("  POST /debug/sessions/{id}/step")
    print("  GET  /debug/sessions/{id}/output")
    print("  DELETE /debug/sessions/{id}")
    print("\n⚡ Ready for debugging! Press Ctrl+C to stop.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.session_manager.terminate_all_sessions()


if __name__ == "__main__":
    run_server()