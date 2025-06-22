#!/usr/bin/env python3
"""Run the PDB REST Gateway server."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.pdb_gateway.api.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )