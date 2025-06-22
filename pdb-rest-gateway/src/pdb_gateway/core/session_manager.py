"""Session manager for handling multiple debugging sessions."""

import uuid
from typing import Dict, Optional, List
from threading import Lock
from datetime import datetime, timedelta

from .pdb_session import PdbSession
from ..schemas.simple_schemas import SessionStatus


class SessionManager:
    """Manages multiple PDB debugging sessions."""
    
    def __init__(self, max_sessions: int = 10, session_timeout: int = 3600):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout  # seconds
        self.sessions: Dict[str, PdbSession] = {}
        self._lock = Lock()
    
    def create_session(self, target_file: str, args: Optional[List[str]] = None,
                      working_directory: Optional[str] = None, 
                      environment: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Create a new debugging session."""
        with self._lock:
            # Check session limit
            self._cleanup_expired_sessions()
            
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest inactive session
                self._remove_oldest_inactive_session()
            
            if len(self.sessions) >= self.max_sessions:
                raise RuntimeError(f"Maximum number of sessions ({self.max_sessions}) reached")
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create new session
            session = PdbSession(
                session_id=session_id,
                target_file=target_file,
                args=args,
                working_directory=working_directory,
                environment=environment
            )
            
            self.sessions[session_id] = session
            
            return {
                "session_id": session_id,
                "status": session.status.value,
                "message": f"Session created for {target_file}"
            }
    
    def get_session(self, session_id: str) -> Optional[PdbSession]:
        """Get a session by ID."""
        with self._lock:
            return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all active sessions."""
        with self._lock:
            self._cleanup_expired_sessions()
            
            sessions_info = []
            for session in self.sessions.values():
                sessions_info.append({
                    "session_id": session.session_id,
                    "status": session.status.value,
                    "target_file": session.target_file,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity
                })
            
            return sessions_info
    
    def terminate_session(self, session_id: str) -> Dict[str, str]:
        """Terminate and remove a session."""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "message": f"Session {session_id} not found"
                }
            
            # Terminate the session
            result = session.terminate()
            
            # Remove from sessions dict
            del self.sessions[session_id]
            
            return {
                "success": True,
                "message": f"Session {session_id} terminated and removed"
            }
    
    def terminate_all_sessions(self) -> Dict[str, str]:
        """Terminate all sessions."""
        with self._lock:
            terminated_count = 0
            
            for session_id in list(self.sessions.keys()):
                session = self.sessions[session_id]
                session.terminate()
                del self.sessions[session_id]
                terminated_count += 1
            
            return {
                "success": True,
                "message": f"Terminated {terminated_count} sessions"
            }
    
    def get_session_count(self) -> int:
        """Get current number of active sessions."""
        with self._lock:
            self._cleanup_expired_sessions()
            return len(self.sessions)
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session.last_activity)
            if (current_time - last_activity).total_seconds() > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.sessions[session_id]
            session.terminate()
            del self.sessions[session_id]
    
    def _remove_oldest_inactive_session(self):
        """Remove the oldest inactive session."""
        oldest_session_id = None
        oldest_time = None
        
        for session_id, session in self.sessions.items():
            if session.status in [SessionStatus.TERMINATED, SessionStatus.ERROR]:
                last_activity = datetime.fromisoformat(session.last_activity)
                if oldest_time is None or last_activity < oldest_time:
                    oldest_time = last_activity
                    oldest_session_id = session_id
        
        if oldest_session_id:
            session = self.sessions[oldest_session_id]
            session.terminate()
            del self.sessions[oldest_session_id]