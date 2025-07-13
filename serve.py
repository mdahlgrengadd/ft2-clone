#!/usr/bin/env python3
"""
Simple HTTP server for serving the FT2 Clone WebAssembly build
This serves the build output with proper MIME types for WebAssembly
"""

import os
import sys
import http.server
import socketserver
from pathlib import Path

# Set up proper MIME types for WebAssembly
class WebAssemblyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        # Handle the return value properly - it can be a string or tuple
        result = super().guess_type(path)
        if isinstance(result, tuple):
            mimetype, encoding = result
        else:
            mimetype = result
            encoding = None
        
        # Add WebAssembly and other specific MIME types
        if path.endswith('.wasm'):
            return 'application/wasm'
        elif path.endswith('.data'):
            return 'application/octet-stream'
        elif path.endswith('.html') or path.endswith('.htm'):
            return 'text/html'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.css'):
            return 'text/css'
        
        return mimetype
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        # Ensure UTF-8 encoding for HTML files
        if hasattr(self, '_content_type') and self._content_type and 'html' in self._content_type:
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()
    
    def send_header(self, keyword, value):
        # Capture content type for later use
        if keyword.lower() == 'content-type':
            self._content_type = value
        super().send_header(keyword, value)

def main():
    # Default port
    port = 8000
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Find build directory
    script_dir = Path(__file__).parent
    build_dir = script_dir / "build_emscripten"
    
    if not build_dir.exists():
        print(f"Error: Build directory not found: {build_dir}")
        print("Please run the build script first:")
        print("  python3 build-emscripten.py")
        print("  # or")
        print("  ./make-emscripten.sh")
        sys.exit(1)
    
    # Check if build output exists
    html_file = build_dir / "web" / "ft2-clone.html"
    if not html_file.exists():
        print(f"Error: Build output not found: {html_file}")
        print("Please run the build script first.")
        sys.exit(1)
    
    # Change to build directory
    os.chdir(build_dir)
    
    # Start server
    try:
        with socketserver.TCPServer(("", port), WebAssemblyHTTPRequestHandler) as httpd:
            print(f"Serving FT2 Clone at http://localhost:{port}/")
            print(f"Open your browser to: http://localhost:{port}/web/ft2-clone.html")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {port} is already in use")
            print(f"Try a different port: python3 {sys.argv[0]} {port + 1}")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
