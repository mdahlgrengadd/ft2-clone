#!/usr/bin/env python3
"""
Simple HTTP server with proper WASM MIME type support for FastTracker II Clone
"""
import http.server
import socketserver
import mimetypes
import os
import sys

# Add WASM MIME type
mimetypes.add_type('application/wasm', '.wasm')

class WASSupportHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        # Add cache control for development
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def guess_type(self, path):
        mimetype, encoding = super().guess_type(path)
        # Ensure WASM files get correct MIME type
        if path.endswith('.wasm'):
            return 'application/wasm', encoding
        return mimetype, encoding
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.date_time_string()}] {format % args}")

def run_server(port=8000):
    """Run the development server"""
    try:
        with socketserver.TCPServer(("", port), WASSupportHandler) as httpd:
            print(f"🎵 FastTracker II Clone Development Server")
            print(f"✅ Serving at http://localhost:{port}")
            print(f"🌐 Open: http://localhost:{port}/web/ft2-clone.html")
            print(f"🧪 Test storage: http://localhost:{port}/persistent-storage-test.html")
            print(f"⚡ WASM MIME type: application/wasm")
            print(f"🔧 CORS headers enabled")
            print(f"\nPress Ctrl+C to stop the server\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python serve-ft2.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8000.")
    
    # Change to build directory if it exists
    if os.path.exists('build_emscripten'):
        os.chdir('build_emscripten')
        print(f"📁 Working directory: {os.getcwd()}")
    
    run_server(port)
