#!/usr/bin/env python3
"""
Admin Server Launcher
Starts the admin interface server on port 8007
"""

import os
import sys
import webbrowser
import time
from pathlib import Path


def main():
    # Get the project root directory
    project_root = Path(__file__).parent

    # Check if admin directory exists
    admin_dir = project_root / "admin"
    if not admin_dir.exists():
        print("❌ Error: Admin directory not found!")
        print(f"   Expected at: {admin_dir}")
        sys.exit(1)

    # Check if admin_api.py exists
    admin_api = project_root / "app" / "admin_api.py"
    if not admin_api.exists():
        print("❌ Error: admin_api.py not found!")
        print(f"   Expected at: {admin_api}")
        sys.exit(1)

    print("🚀 Starting Admin Server...")
    print("=" * 60)
    print(f"📁 Project Root: {project_root}")
    print(f"🌐 Admin URL: http://localhost:8007")
    print(f"📡 API Base: http://localhost:8007/api")
    print("=" * 60)
    print("\n💡 The admin interface will open in your browser automatically.")
    print("   Press Ctrl+C to stop the server.\n")

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8007")

    import threading

    threading.Thread(target=open_browser, daemon=True).start()

    # Start the server
    os.chdir(project_root)
    os.system(
        "python3 -m uvicorn app.admin_api:app --host 127.0.0.1 --port 8007 --reload"
    )


if __name__ == "__main__":
    main()
