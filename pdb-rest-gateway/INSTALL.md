# Installing PDB Gateway as MCP Server

## 1. Install MCP Library

```bash
pip install mcp
```

## 2. Configure Claude Desktop

Add this to your Claude Desktop configuration file:

**On macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pdb-gateway": {
      "command": "python3",
      "args": ["/absolute/path/to/pdb-rest-gateway/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/pdb-rest-gateway/src"
      }
    }
  }
}
```

## 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop.

## 4. Verify Installation

In Claude Code, you should see the PDB Gateway tools available:
- `pdb_start_session`
- `pdb_set_breakpoint` 
- `pdb_step`
- `pdb_inspect`
- `pdb_execute`
- `pdb_list_sessions`
- `pdb_terminate_session`

## 5. Test Usage

Try asking Claude Code to:
```
Debug this Python file using pdb tools - set a breakpoint and step through the code
```

## Troubleshooting

- Ensure Python paths are absolute, not relative
- Check that `mcp` library is installed in the Python environment
- Verify Claude Desktop has been restarted after config changes
- Check Claude Desktop logs for MCP server errors