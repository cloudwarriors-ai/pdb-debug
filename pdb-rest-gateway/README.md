# PDB REST Gateway

A REST API and MCP server for remote Python debugging using pdb.

## Overview

This tool provides programmatic access to Python's pdb debugger through:
- REST API endpoints for manual testing and integration
- MCP (Model Context Protocol) server for AI assistant debugging
- Session-based debugging with concurrent session support
- Real-time debugging interaction via WebSocket/SSE

## Architecture

```
pdb-rest-gateway/
├── src/pdb_gateway/
│   ├── api/           # FastAPI REST endpoints
│   ├── core/          # Core debugging logic
│   ├── mcp/           # MCP server implementation
│   └── schemas/       # JSON schemas for requests/responses
├── tests/             # Unit and integration tests
├── docs/              # Documentation
└── examples/          # Usage examples
```

## Quick Start

### REST API Mode
```bash
cd pdb-rest-gateway
pip install -r requirements.txt
python -m uvicorn src.pdb_gateway.api.main:app --reload --port 8001
```

### MCP Server Mode
```bash
# Coming soon - will be MCP server implementation
python -m src.pdb_gateway.mcp.server
```

## API Endpoints

- `POST /debug/sessions` - Start new debugging session
- `POST /debug/sessions/{id}/breakpoint` - Set/remove breakpoints
- `POST /debug/sessions/{id}/step` - Step through code
- `GET /debug/sessions/{id}/inspect` - Inspect variables
- `GET /debug/sessions/{id}/output` - Get debugging output
- `DELETE /debug/sessions/{id}` - End session

## MCP Tools

- `pdb_start_session` - Initialize debugging session
- `pdb_set_breakpoint` - Set/remove breakpoints  
- `pdb_step` - Step through code (next, step, continue)
- `pdb_inspect` - Inspect variables and stack
- `pdb_execute` - Execute arbitrary pdb commands
- `pdb_get_output` - Retrieve debugging output

## Development Status

- [x] Research and architecture design
- [ ] Core debugging engine
- [ ] REST API implementation
- [ ] Session management
- [ ] MCP server conversion
- [ ] Integration testing