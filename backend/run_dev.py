#!/usr/bin/env python3

import uvicorn

if __name__ == "__main__":
    print("🚀 Playlist Porter - Development Mode")
    print("✅ Starting development server on http://127.0.0.1:8000")

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=["src"],
    )
