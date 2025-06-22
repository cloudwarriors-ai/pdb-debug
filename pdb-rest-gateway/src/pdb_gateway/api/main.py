"""FastAPI application for PDB REST Gateway."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from ..core.session_manager import SessionManager
from ..schemas.debug_schemas import (
    StartSessionRequest, StartSessionResponse,
    SetBreakpointRequest, SetBreakpointResponse,
    StepRequest, StepResponse,
    InspectRequest, InspectResponse,
    ExecuteCommandRequest, ExecuteCommandResponse,
    SessionInfo, GetOutputResponse, ErrorResponse
)

# Create FastAPI app
app = FastAPI(
    title="PDB REST Gateway",
    description="REST API for remote Python debugging using pdb",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session manager
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Dependency to get session manager."""
    return session_manager


@app.post("/debug/sessions", response_model=StartSessionResponse)
async def start_debug_session(
    request: StartSessionRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Start a new debugging session."""
    try:
        # Create session
        result = manager.create_session(
            target_file=request.target_file,
            args=request.args,
            working_directory=request.working_directory,
            environment=request.environment
        )
        
        # Start debugging
        session = manager.get_session(result["session_id"])
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        debug_result = session.start_debugging()
        
        return StartSessionResponse(
            session_id=result["session_id"],
            status=session.status,
            pid=None,  # TODO: Get actual PID
            message=debug_result["message"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/debug/sessions", response_model=List[SessionInfo])
async def list_debug_sessions(
    manager: SessionManager = Depends(get_session_manager)
):
    """List all active debugging sessions."""
    sessions = manager.list_sessions()
    
    session_infos = []
    for session_data in sessions:
        session = manager.get_session(session_data["session_id"])
        if session:
            session_infos.append(SessionInfo(**session.get_session_info()))
    
    return session_infos


@app.get("/debug/sessions/{session_id}", response_model=SessionInfo)
async def get_debug_session(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Get information about a specific debugging session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionInfo(**session.get_session_info())


@app.post("/debug/sessions/{session_id}/breakpoint", response_model=SetBreakpointResponse)
async def set_breakpoint(
    session_id: str,
    request: SetBreakpointRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Set or remove a breakpoint in the debugging session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = session.set_breakpoint(
        filename=request.filename,
        line_number=request.line_number,
        condition=request.condition,
        temporary=request.temporary,
        remove=request.remove
    )
    
    return SetBreakpointResponse(
        breakpoint_id=result.get("breakpoint_id"),
        success=result["success"],
        message=result["message"]
    )


@app.post("/debug/sessions/{session_id}/step", response_model=StepResponse)
async def step_debugger(
    session_id: str,
    request: StepRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Step through code in the debugging session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = session.step(
        step_type=request.step_type,
        count=request.count,
        line_number=request.line_number
    )
    
    return StepResponse(**result)


@app.post("/debug/sessions/{session_id}/inspect", response_model=InspectResponse)
async def inspect_variable(
    session_id: str,
    request: InspectRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Inspect a variable or expression in the debugging session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = session.inspect(
        expression=request.expression,
        frame_level=request.frame_level
    )
    
    return InspectResponse(**result)


@app.post("/debug/sessions/{session_id}/execute", response_model=ExecuteCommandResponse)
async def execute_command(
    session_id: str,
    request: ExecuteCommandRequest,
    manager: SessionManager = Depends(get_session_manager)
):
    """Execute an arbitrary PDB command in the debugging session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = session.execute_command(request.command)
    
    return ExecuteCommandResponse(**result)


@app.get("/debug/sessions/{session_id}/output", response_model=GetOutputResponse)
async def get_debug_output(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Get debugging output from the session."""
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    output = session.get_output()
    
    return GetOutputResponse(
        session_id=session_id,
        output=output,
        timestamp=session.last_activity,
        has_more=False  # TODO: Implement pagination
    )


@app.delete("/debug/sessions/{session_id}")
async def terminate_debug_session(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager)
):
    """Terminate a debugging session."""
    result = manager.terminate_session(session_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return {"message": result["message"]}


@app.delete("/debug/sessions")
async def terminate_all_sessions(
    manager: SessionManager = Depends(get_session_manager)
):
    """Terminate all debugging sessions."""
    result = manager.terminate_all_sessions()
    return {"message": result["message"]}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_session_count(),
        "timestamp": "2024-01-01T00:00:00"  # TODO: Use actual timestamp
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "PDB REST Gateway",
        "version": "0.1.0",
        "description": "REST API for remote Python debugging using pdb",
        "docs_url": "/docs",
        "active_sessions": session_manager.get_session_count()
    }