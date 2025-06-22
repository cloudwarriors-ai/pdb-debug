# PDB Debug Gateway

A comprehensive REST API and MCP server for remote Python debugging using pdb.

## 🚀 Features

- **Remote Debugging**: Debug Python applications via REST API calls
- **AI-Assisted Debugging**: MCP server integration for Claude Code
- **Session Management**: Multiple concurrent debugging sessions
- **Comprehensive Logging**: Complete audit trail of debugging operations
- **Multiple Breakpoint Types**: Regular, conditional, and temporary breakpoints
- **Variable Inspection**: Real-time inspection of variables and expressions
- **Step-by-Step Execution**: Programmatic control over code execution flow

## 🎯 What This Enables

### AI-Assisted Debugging
- Claude Code can automatically set breakpoints at suspicious code locations
- AI can step through execution to understand program flow
- Intelligent variable inspection to identify data corruption or logic errors
- Automated debugging reports with root cause analysis

### Remote Debugging at Scale  
- Debug production systems without direct server access
- Collaborative debugging with multiple developers
- Automated debugging pipelines integrated into CI/CD
- Cloud-native debugging for containerized applications

## 📁 Repository Structure

```
pdb-debug/
├── pdb-rest-gateway/          # Main PDB Gateway implementation
│   ├── src/pdb_gateway/       # Core library code
│   │   ├── api/              # REST API endpoints
│   │   ├── core/             # Debugging engine and session management
│   │   ├── mcp/              # MCP server implementation
│   │   └── schemas/          # Request/response schemas
│   ├── simple_server.py      # Standalone REST API server
│   ├── mcp_server.py         # MCP server for Claude Code
│   ├── requirements.txt      # Python dependencies
│   └── *.py                  # Test and demo scripts
├── breakpoint-simulation/     # Test applications and demos
│   ├── data_processor.py     # Sample data processing pipeline (295 lines)
│   ├── test_*.py            # Comprehensive test suites
│   └── *.md                 # Testing documentation
├── CLAUDE.md                 # Complete integration guide
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Start the PDB Gateway Server

```bash
# REST API server (port 8002)
cd pdb-rest-gateway
python3 simple_server.py

# OR MCP server for Claude Code integration
python3 mcp_server.py
```

### 2. Test with Sample Application

```bash
# Run comprehensive debugging tests
python3 breakpoint-simulation/test_with_logging.py

# Test real debugging scenarios
python3 breakpoint-simulation/test_debugging.py

# Analyze debugging logs
python3 pdb-rest-gateway/view_logs.py
```

### 3. Debug Your Own Applications

```bash
# Create debug session via REST API
curl -X POST http://localhost:8002/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"target_file": "your_script.py"}'

# Set breakpoint
curl -X POST http://localhost:8002/debug/sessions/{session_id}/breakpoint \
  -H "Content-Type: application/json" \
  -d '{"filename": "your_script.py", "line_number": 25}'

# Step through execution
curl -X POST http://localhost:8002/debug/sessions/{session_id}/step \
  -H "Content-Type: application/json" \
  -d '{"step_type": "continue"}'
```

## 🔧 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/debug/sessions` | Create new debugging session |
| GET | `/debug/sessions` | List active sessions |
| GET | `/debug/sessions/{id}` | Get session information |
| DELETE | `/debug/sessions/{id}` | Terminate session |
| POST | `/debug/sessions/{id}/breakpoint` | Set/remove breakpoint |
| POST | `/debug/sessions/{id}/step` | Step through execution |
| POST | `/debug/sessions/{id}/inspect` | Inspect variables |
| POST | `/debug/sessions/{id}/execute` | Execute PDB commands |
| GET | `/debug/sessions/{id}/output` | Get debug output |

## 🤖 MCP Tools for AI Assistants

When configured as an MCP server, provides these tools for Claude Code:

- `pdb_start_session` - Initialize debugging session
- `pdb_set_breakpoint` - Set/remove breakpoints
- `pdb_step` - Step through code execution
- `pdb_inspect` - Inspect variables and expressions
- `pdb_execute` - Execute arbitrary PDB commands
- `pdb_list_sessions` - List active sessions
- `pdb_terminate_session` - End debugging sessions

## 📊 Testing Results

Our comprehensive testing demonstrates:

- **47 operations** executed in 0.817 seconds (57.5 ops/sec)
- **10 breakpoints** set (regular, conditional, temporary)
- **8 step operations** (next, continue, step with counts)
- **14 variable inspections** (simple vars, complex expressions)
- **13 command executions** (list, where, args, locals, etc.)
- **Complete logging** with 29.8 KB audit trail

## 🎯 Use Cases

### Development & Debugging
- Interactive debugging of complex applications
- Root cause analysis of production issues
- Code behavior understanding and documentation
- Performance bottleneck identification

### AI-Assisted Development
- Automated bug detection and analysis
- Intelligent code review and suggestions
- Educational code walkthroughs
- Debugging knowledge capture and sharing

### Enterprise Applications
- Audit compliance with complete operation logging
- Security monitoring of debugging activities
- Collaborative debugging across teams
- Integration with CI/CD pipelines

## 📋 Requirements

- Python 3.7+
- Standard library modules (pdb, threading, json, etc.)
- Optional: FastAPI for REST server
- Optional: MCP library for Claude Code integration

## 🔍 Logging and Monitoring

All debugging operations are logged with:
- Timestamp tracking for all operations
- Success/failure status for each operation
- Complete parameter values and results
- Session duration and performance metrics
- Error tracking and debugging information

View logs with:
```bash
python3 pdb-rest-gateway/view_logs.py
tail -f pdb-rest-gateway/pdb_gateway.log
```

## 🚀 Future Possibilities

- **Predictive debugging** - AI predicts where bugs will occur
- **Self-healing code** - Systems that debug and fix themselves
- **Intelligent monitoring** - Continuous debugging of live systems
- **Code optimization** - AI suggests improvements based on execution analysis

## 📖 Documentation

See `CLAUDE.md` for complete integration guide including:
- ETL system integration examples
- Natural language debugging commands
- Comprehensive API documentation
- Troubleshooting and best practices

---

**🎯 This tool revolutionizes Python debugging by making it programmable, remote, intelligent, and scalable!**