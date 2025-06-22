#!/usr/bin/env python3
"""Install MCP dependencies."""

import subprocess
import sys

def install_mcp():
    """Install MCP package."""
    try:
        # Try importing mcp first
        import mcp
        print("✅ MCP already installed")
        return True
    except ImportError:
        pass
    
    print("📦 Installing MCP...")
    
    # Install using pip
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "mcp"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MCP installed successfully")
            return True
        else:
            print(f"❌ Failed to install MCP: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing MCP: {e}")
        return False

if __name__ == "__main__":
    install_mcp()