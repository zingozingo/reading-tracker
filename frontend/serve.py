#!/usr/bin/env python3
"""
Simple HTTP server to serve the BookTracker frontend
Serves the HTML dashboard on port 3000
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers for API access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom log format
        sys.stderr.write("%s - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

def main():
    print("\n" + "="*60)
    print("🚀 BookTracker Frontend Server")
    print("="*60)
    print(f"\n📁 Serving directory: {DIRECTORY}")
    print(f"🌐 Server starting on port {PORT}...")

    try:
        # Allow socket reuse to prevent "Address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"\n✅ Server running successfully!")
            print(f"\n📱 Access the dashboard at:")
            print(f"   → http://localhost:{PORT}")
            print(f"   → http://127.0.0.1:{PORT}")
            print(f"\n🔌 Make sure the API is running:")
            print(f"   → uvicorn main:app --reload (port 8000)")
            print(f"\n📖 API Documentation available at:")
            print(f"   → http://localhost:8000/docs")
            print(f"\n💡 Tips:")
            print(f"   • Press Ctrl+C to stop the server")
            print(f"   • Press 'R' key in the dashboard to refresh data")
            print(f"   • The dashboard auto-refreshes every 30 seconds")
            print("\n" + "="*60 + "\n")

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"   Try one of these solutions:")
            print(f"   1. Kill the process using port {PORT}:")
            print(f"      lsof -ti:{PORT} | xargs kill -9")
            print(f"   2. Use a different port by modifying PORT in serve.py")
        else:
            print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()