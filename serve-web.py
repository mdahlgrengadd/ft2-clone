#!/usr/bin/env python3
"""
Simple web server for serving FastTracker II Clone WebAssembly build
Fixes caching and MIME type issues
"""

import http.server
import socketserver
import mimetypes
import os
import sys
from pathlib import Path

# Add WASM MIME type
mimetypes.add_type('application/wasm', '.wasm')


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add headers to prevent caching issues
        self.send_header(
            'Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        # Set proper MIME types
        if self.path.endswith('.wasm'):
            self.send_header('Content-Type', 'application/wasm')
        elif self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html')

        super().end_headers()

    def do_GET(self):
        # Handle root requests
        if self.path == '/':
            self.path = '/index.html'

        # Handle missing favicon.ico
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return

        # Handle service worker requests
        if self.path.endswith('/sw.js'):
            self.send_response(404)
            self.end_headers()
            return

        return super().do_GET()


def main():
    PORT = 8000

    # Change to build directory if we're not already there
    if not os.path.exists('web'):
        if os.path.exists('build_emscripten'):
            os.chdir('build_emscripten')
        else:
            print("Error: Cannot find build_emscripten directory")
            sys.exit(1)

    # Create index.html for easier navigation
    create_index_html()

    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"FastTracker II Clone Web Server")
        print(f"Serving at http://localhost:{PORT}")
        print(f"")
        print(
            f"🎵 FastTracker II Clone: http://localhost:{PORT}/web/ft2-clone.html")
        print(f"📋 Test Page: http://localhost:{PORT}/test-fix.html")
        print(f"")
        print(f"Press Ctrl+C to stop the server")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")


def create_index_html():
    """Create a simple index page for navigation"""
    index_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastTracker II Clone - Web Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        .button {
            background-color: #e74c3c;
            color: white;
            padding: 15px 30px;
            margin: 10px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #c0392b;
        }
        .info {
            background-color: #2c3e50;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .logo {
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎵 FastTracker II Clone</div>
        <h1>WebAssembly Build Server</h1>
        
        <div class="info">
            <p>Welcome to the FastTracker II Clone WebAssembly build server!</p>
            <p>This server is configured to handle WebAssembly files correctly.</p>
        </div>
        
        <a href="/web/ft2-clone.html" class="button">🚀 Launch FastTracker II Clone</a>
        <a href="/test-fix.html" class="button">🧪 Test Page</a>
        
        <div class="info">
            <h3>🔧 Server Features:</h3>
            <ul style="text-align: left;">
                <li>✅ Proper WASM MIME types</li>
                <li>✅ No-cache headers (fixes reload issues)</li>
                <li>✅ CORS headers for local development</li>
                <li>✅ Handles missing favicon.ico</li>
                <li>✅ Filters out service worker requests</li>
            </ul>
        </div>
    </div>
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)


if __name__ == '__main__':
    main()
