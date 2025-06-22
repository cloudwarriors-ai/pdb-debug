# ETL System Project - Claude Code Guide

## Project Overview
This is a Django-based ETL (Extract, Transform, Load) system with a hacker-themed frontend that manages data pipelines between platforms like Zoom, Dialpad, and RingCentral. The system features real-time job monitoring, JWT authentication, and a comprehensive WebSocket-based interface.

## Quick Start Commands

### Backend Operations
```bash
# Start backend (from project root)
docker-compose up -d backend

# Start backend directly (from /app/backend)
python3 manage.py runserver 0.0.0.0:8000 --settings=etl_system.settings_development

# Apply migrations
python3 manage.py migrate --settings=etl_system.settings_development

# Load fixtures
python3 manage.py loaddata api/fixtures/split_fixtures/*.json --settings=etl_system.settings_development
```

### Frontend Development
```bash
# Frontend is served from /app/frontend/templates/job-runner-hacker.html
# Static files: /app/frontend/static/
# Main entry point: http://127.0.0.1:8040
```

### Testing
```bash
# Run Django tests
python3 manage.py test --settings=etl_system.settings_development

# Test ETL endpoints
python3 test_etl_workflow_comprehensive.py
```

### PDB Debugging Gateway
```bash
# Start PDB REST API server for remote debugging
cd /app/pdb-rest-gateway
python3 simple_server.py  # Starts on port 8002

# Run comprehensive debugging tests
python3 /app/breakpoint-simulation/test_with_logging.py

# View debugging logs
python3 /app/pdb-rest-gateway/view_logs.py

# Test with sample application
cd /app/breakpoint-simulation
python3 test_debugging.py
```

## Architecture

### Backend Structure
- **Django Project**: `/app/backend/etl_system/`
- **Main App**: `/app/backend/api/`
- **ETL Core**: `/app/backend/api/etl/core/`
- **Platform Integrations**: `/app/backend/api/etl/platforms/`
- **Settings**: 
  - Development: `/app/backend/etl_system/settings_development.py`
  - Production: `/app/backend/etl_system/settings_production.py`

### Frontend Structure
- **Templates**: `/app/frontend/templates/`
- **Static Assets**: `/app/frontend/static/`
- **Main Interface**: `job-runner-hacker.html` (Matrix/80's cyberpunk theme)
- **JavaScript Modules**: 
  - Authentication: `auth.js`
  - Job Management: `job-runner-hacker.js`
  - ETL Testing: `etl-testing-simple.js`
  - WebSocket: `websocket-hacker.js`

### Key Components
1. **Job Groups**: Collections of ETL jobs that run together
2. **Job Types**: Templates defining source→target platform mappings
3. **ETL Jobs**: Individual extraction/transformation/loading operations
4. **Real-time Monitoring**: WebSocket-based job status updates
5. **Authentication**: JWT-based with modal login interface

## Clean Code Principles Applied

### 1. Single Responsibility Principle (SRP)
- **Backend**: Each Django app handles one concern (auth, ETL, etc.)
- **Frontend**: Separate JavaScript modules for different functionalities
- **ETL Core**: Dedicated classes for extraction, transformation, loading
- **Example**: `JobGroupService` only handles job group operations

### 2. Open/Closed Principle
- **Platform Extensions**: New platforms added via `/app/backend/api/etl/platforms/`
- **ETL Factory Pattern**: Easily extensible for new platform types
- **Component Architecture**: Frontend components can be extended without modification

### 3. Dependency Inversion
- **ETL Factory**: Abstracts platform-specific implementations
- **Authentication**: JWT service abstracted from specific implementations
- **Database**: Django ORM abstracts database operations

### 4. Clean Architecture Layers
```
Presentation Layer (Frontend) → Application Layer (Django Views) → 
Domain Layer (ETL Core) → Infrastructure Layer (Platform APIs)
```

### 5. Meaningful Names
- **Classes**: `JobGroupService`, `ETLFactory`, `SimpleETLTesting`
- **Methods**: `createJobGroup()`, `executeExtract()`, `displayExtractedData()`
- **Variables**: `selectedJobType`, `createdJobGroup`, `extractedRecords`

### 6. Function Design
- **Small Functions**: Most functions under 20 lines
- **Single Purpose**: Each function does one thing well
- **No Side Effects**: Pure functions where possible
- **Example**: `log()` method only handles terminal output

### 7. Error Handling
- **Explicit Error Types**: Custom error classes in `error_types.py`
- **Graceful Degradation**: Frontend falls back to mock data if real API fails
- **User-Friendly Messages**: Clear error messages in terminal interface

### 8. Code Organization
- **Modular Structure**: Separate files for each major component
- **Logical Grouping**: Related functionality grouped together
- **Clear Separation**: Frontend/backend concerns completely separated

### 9. Testing Principles
- **Testable Code**: Dependencies injected, functions isolated
- **Comprehensive Tests**: Unit tests for ETL operations
- **Integration Tests**: End-to-end workflow testing

### 10. Documentation
- **Self-Documenting Code**: Clear names reduce need for comments
- **API Documentation**: Comprehensive docstrings for all public methods
- **Architecture Documentation**: Clear project structure documentation

## Authentication System

### CSRF Configuration
- **Development**: CSRF middleware disabled for JWT endpoints
- **Login Endpoint**: `@csrf_exempt` decorator applied
- **Frontend**: No CSRF tokens sent (JWT-based authentication)

### JWT Flow
1. User submits credentials via modal login
2. Backend validates and returns JWT tokens
3. Frontend stores tokens in localStorage
4. All API requests include `Authorization: Bearer <token>` header
5. Automatic token refresh on expiration

### Global Functions
```javascript
window.loginUser(email, password)     // Authentication
window.makeAuthenticatedRequest(url)  // API calls with auth
window.logout()                       // Logout and cleanup
```

## ETL Testing Workflow

### Simple Testing Process
1. **Select Job Type**: Choose from available ETL job types
2. **Create Job**: Generate job group and ETL job
3. **Run Test**: Execute real extraction with live API calls
4. **View Results**: Display extracted data in terminal format

### Real vs Mock Data
- **Production**: Real API calls to platform endpoints
- **Development**: Can fall back to mock data if platforms not configured
- **Testing**: Uses `test_mode: true` flag for safe operations

## Common Issues & Solutions

### Authentication Problems
```bash
# Error: "CSRF Failed: CSRF token missing"
# Solution: Restart backend to apply CSRF exemption
docker-compose down backend && docker-compose up -d backend
```

### Frontend Module Loading
```javascript
// Ensure auth.js exports to global scope
window.loginUser = loginUser;
window.makeAuthenticatedRequest = makeAuthenticatedRequest;
```

### WebSocket Connection Issues
```javascript
// Check WebSocket URL pattern
const wsUrl = `ws://127.0.0.1:8000/ws/job-status/${jobGroupId}/`;
```

## Development Workflow

### Code Style Guidelines
1. **JavaScript**: Use camelCase for variables and functions
2. **Python**: Follow PEP 8 conventions
3. **CSS**: Use kebab-case for class names
4. **HTML**: Semantic markup with meaningful IDs

### Git Workflow
1. **Feature Branches**: Create feature-specific branches
2. **Small Commits**: Commit frequently with clear messages
3. **Testing**: Test before committing
4. **Documentation**: Update CLAUDE.md when adding major features

### Debugging Tools
- **Frontend**: Browser developer tools + console logging
- **Backend**: Django debug toolbar + logging
- **ETL**: Comprehensive logging in `etl.log`
- **WebSocket**: Real-time connection monitoring

## File Locations Reference

### Critical Configuration Files
- **Django Settings**: `/app/backend/etl_system/settings_development.py`
- **URL Routing**: `/app/backend/api/urls.py`
- **Main Frontend**: `/app/frontend/templates/job-runner-hacker.html`
- **Authentication**: `/app/frontend/static/js/auth.js`

### ETL Core Files
- **Factory Pattern**: `/app/backend/api/etl/core/etl_factory.py`
- **Job Management**: `/app/backend/api/etl/core/job_group_service.py`
- **Platform Abstraction**: `/app/backend/api/etl/platforms/factory.py`

### Frontend Components
- **Job Runner**: `/app/frontend/static/js/job-runner-hacker.js`
- **ETL Testing**: `/app/frontend/static/js/etl-testing-simple.js`
- **WebSocket**: `/app/frontend/static/js/websocket-hacker.js`
- **Styling**: `/app/frontend/static/css/hacker-theme-all.css`

## Environment Variables
```bash
# Backend
SECRET_KEY=django-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-key

# Database
DATABASE_URL=sqlite:///db.sqlite3

# ETL Configuration
ETL_ENABLE_LLM=True
```

## Performance Considerations
- **Lazy Loading**: Frontend components initialize only when needed
- **Connection Pooling**: Database connections reused
- **Caching**: Job type data cached in frontend
- **WebSocket Efficiency**: Single connection per job group

## Security Notes
- **JWT Tokens**: Stored in localStorage (consider httpOnly cookies for production)
- **CSRF**: Disabled for development (re-enable for production with session auth)
- **API Keys**: Stored securely in environment variables
- **Input Validation**: All user inputs validated on backend

---

## PDB Debugging Gateway Integration

### Overview
This project includes a comprehensive **PDB REST Gateway** that enables remote debugging of Python applications via REST API and MCP server integration. This revolutionary tool allows AI assistants to debug code programmatically.

### Key Features
- **Remote Debugging**: Debug Python applications via REST API calls
- **AI-Assisted Debugging**: MCP server integration for Claude Code
- **Session Management**: Multiple concurrent debugging sessions
- **Comprehensive Logging**: Complete audit trail of debugging operations
- **Multiple Breakpoint Types**: Regular, conditional, and temporary breakpoints
- **Variable Inspection**: Real-time inspection of variables and expressions
- **Step-by-Step Execution**: Programmatic control over code execution flow

### Quick Start for Debugging

#### 1. Start the PDB Gateway Server
```bash
cd /app/pdb-rest-gateway
python3 simple_server.py  # REST API on port 8002
# OR
python3 mcp_server.py     # MCP server for Claude Code integration
```

#### 2. Debug ETL Components
```bash
# Test debugging with actual ETL files
python3 /app/breakpoint-simulation/test_real_etl.py

# Debug specific ETL components
# Files available for debugging:
# - /app/backend/api/etl/core/etl_factory.py
# - /app/backend/api/etl/core/job_group_service.py  
# - /app/backend/api/etl/core/dynamic_extractor.py
# - /app/backend/api/etl/platforms/zoom/extractors.py
```

#### 3. AI-Assisted Debugging Commands
When Claude Code has MCP access, you can use natural language debugging:

```
"Debug the ETL factory class and set breakpoints at key functions"
"Step through the data validation logic and inspect the validation_rules"
"Find why some records are failing validation in the transform process"
"Inspect the raw_data variable when the extraction completes"
"Set a conditional breakpoint for when validation fails"
```

### REST API Endpoints

The PDB Gateway provides these debugging endpoints:

```http
POST   /debug/sessions                    # Create debug session
GET    /debug/sessions                    # List active sessions  
GET    /debug/sessions/{id}              # Get session info
DELETE /debug/sessions/{id}              # Terminate session

POST   /debug/sessions/{id}/breakpoint   # Set/remove breakpoint
POST   /debug/sessions/{id}/step         # Step through execution
POST   /debug/sessions/{id}/inspect      # Inspect variables
POST   /debug/sessions/{id}/execute      # Execute PDB commands
GET    /debug/sessions/{id}/output       # Get debug output
```

### Example Debugging Workflow

#### 1. Create Debug Session
```bash
curl -X POST http://localhost:8002/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "target_file": "/app/backend/api/etl/core/etl_factory.py",
    "working_directory": "/app/backend"
  }'
```

#### 2. Set Breakpoints
```bash
curl -X POST http://localhost:8002/debug/sessions/{session_id}/breakpoint \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "etl_factory.py",
    "line_number": 21,
    "condition": "job_type == \"extraction\""
  }'
```

#### 3. Step Through Code
```bash
curl -X POST http://localhost:8002/debug/sessions/{session_id}/step \
  -H "Content-Type: application/json" \
  -d '{
    "step_type": "continue"
  }'
```

#### 4. Inspect Variables
```bash
curl -X POST http://localhost:8002/debug/sessions/{session_id}/inspect \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "job_config"
  }'
```

### MCP Tools Available

When configured as an MCP server, Claude Code has access to these tools:
- `pdb_start_session` - Initialize debugging session
- `pdb_set_breakpoint` - Set/remove breakpoints
- `pdb_step` - Step through code execution  
- `pdb_inspect` - Inspect variables and expressions
- `pdb_execute` - Execute arbitrary PDB commands
- `pdb_list_sessions` - List active sessions
- `pdb_terminate_session` - End debugging sessions

### Debugging Logs and Analysis

#### View Debugging Activity
```bash
# Analyze all debugging operations
python3 /app/pdb-rest-gateway/view_logs.py

# Check main log file
tail -f /app/pdb-rest-gateway/pdb_gateway.log

# View exported session details
ls /app/pdb-rest-gateway/session_*_log.json
```

#### Log Information Includes
- **Timestamp tracking** for all operations
- **Breakpoint management** (set/remove with conditions)
- **Step operations** (next, step, continue, until, return)
- **Variable inspections** with success/failure status
- **Command executions** with output lengths
- **Session lifecycle** from creation to termination
- **Performance metrics** (operations per second)

### Integration with ETL System

The PDB Gateway is specifically configured to debug ETL components:

#### Common ETL Debugging Scenarios
1. **Job Creation Issues**: Debug ETL factory initialization
2. **Data Extraction Problems**: Step through extractor logic
3. **Transformation Errors**: Inspect data at each transform stage
4. **Validation Failures**: Set conditional breakpoints for invalid data
5. **Loading Issues**: Monitor data loading and error handling

#### ETL-Specific Debugging Tips
- Set breakpoints in `etl_factory.py` line 21 for job creation
- Use conditional breakpoints like `len(extracted_data) == 0` 
- Inspect `job_config`, `platform_settings`, and `extraction_result`
- Step through `run_job()` method to see complete pipeline flow
- Monitor `validation_errors` and `transformation_results`

### File Locations

#### PDB Gateway Files
- **Main Server**: `/app/pdb-rest-gateway/simple_server.py`
- **MCP Server**: `/app/pdb-rest-gateway/mcp_server.py`
- **Core Logic**: `/app/pdb-rest-gateway/src/pdb_gateway/`
- **Test Applications**: `/app/breakpoint-simulation/`
- **Logs**: `/app/pdb-rest-gateway/pdb_gateway.log`

#### Sample Applications
- **Data Processor**: `/app/breakpoint-simulation/data_processor.py` (295 lines)
- **ETL Test**: `/app/breakpoint-simulation/test_real_etl.py`
- **Comprehensive Test**: `/app/breakpoint-simulation/test_with_logging.py`

## Notes for Future Claude Sessions
- This project uses a hacker/Matrix theme for the frontend interface
- ETL testing should use real API calls, not simulations
- WebSocket connections are critical for real-time job monitoring
- The authentication flow has been customized to work without CSRF for JWT
- All major functionality has been refactored to follow clean code principles
- **NEW**: PDB Gateway enables remote debugging via REST API and MCP server
- **NEW**: Claude Code can debug Python applications autonomously via MCP tools
- **NEW**: Complete debugging audit trail available in logs for troubleshooting
- **NEW**: Supports debugging of live ETL processes and data pipeline issues