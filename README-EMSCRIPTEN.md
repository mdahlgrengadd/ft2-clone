# FastTracker II Clone - Emscripten Build

This project provides a unified, cross-platform build system for compiling FastTracker II Clone to WebAssembly using Emscripten.

## Prerequisites

1. **Emscripten SDK** - Download and install from [emscripten.org](https://emscripten.org/docs/getting_started/downloads.html)
2. **Python 3.x** (recommended) or Bash

### Installing Emscripten

1. Download the Emscripten SDK:
   ```bash
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   ```

2. Install and activate the latest version:
   ```bash
   ./emsdk install latest
   ./emsdk activate latest
   ```

3. Set up the environment variables:
   - **Linux/macOS**: `source ./emsdk_env.sh`
   - **Windows**: `emsdk_env.bat`

## Building

### Option 1: Unified Python Script (Recommended)

The Python script works on all platforms and provides the most reliable build experience:

```bash
python3 build-emscripten.py
```

### Option 2: Platform-Specific Scripts

#### Linux/macOS
```bash
./make-emscripten.sh
```

#### Windows (PowerShell)
```powershell
.\make-emscripten.ps1
```

#### Windows (Batch)
```cmd
make-emscripten.bat
```

## Build Output

After a successful build, you'll find the following files in `build_emscripten/web/`:

- `ft2-clone.html` - Main HTML file
- `ft2-clone.js` - JavaScript runtime
- `ft2-clone.wasm` - WebAssembly binary
- `ft2-clone.data` - Asset data (graphics, preloaded files)

## Running the Application

Due to browser security restrictions, you need to serve the files from a web server:

### Option 1: Using the included serve script
```bash
python3 serve.py [port]
```
Then open: `http://localhost:8000/web/ft2-clone.html` (or your chosen port)

### Option 2: Using Python's built-in server
```bash
cd build_emscripten
python3 -m http.server 8000
```
Then open: `http://localhost:8000/web/ft2-clone.html`

### Option 3: Using Node.js (if available)
```bash
cd build_emscripten
npx http-server
```

## Features

- **Cross-platform builds**: Works on Linux, macOS, and Windows
- **Unified build system**: Single Python script that works everywhere
- **File persistence**: Uses IndexedDB for persistent file storage
- **Drag & Drop support**: Drop module files directly onto the browser window
- **Module formats**: Supports .xm, .ft, .mod, .s3m, .it, and other tracker formats

## Directory Structure

- `web/web_user/` - Virtual user directory, mapped to `/home/web_user` in the WebAssembly filesystem
- `web/web_user/modules/` - Place your module files here or drag & drop them
- `web/assets/` - Additional web assets (optional)
- `web/shell.html` - HTML template for the application

## Troubleshooting

### Build fails with SDL errors
Make sure Emscripten is properly activated in your terminal session:
```bash
source /path/to/emsdk/emsdk_env.sh  # Linux/macOS
# or
emsdk_env.bat  # Windows
```

### "Permission denied" errors
Make scripts executable:
```bash
chmod +x build-emscripten.py make-emscripten.sh serve.py
```

### Browser shows blank page
1. Make sure you're serving from a web server (not opening the file directly)
2. Check the browser console for errors
3. Try a different browser (Chrome/Firefox recommended)

### Files don't persist between sessions
The application uses IndexedDB for persistence. Make sure:
1. You're using the same browser and domain
2. Your browser allows IndexedDB
3. You're not in private/incognito mode

## Development

The build system uses direct `emcc` compilation for reliability, avoiding some CMake complexities. The key flags used:

- `-sUSE_SDL=2` - Use Emscripten's SDL2 port
- `-sASYNCIFY=1` - Enable async/await support
- `-sFORCE_FILESYSTEM=1` - Include full filesystem support
- `-lidbfs.js` - Enable IndexedDB persistence

For more details, see the source code in `build-emscripten.py` or the platform-specific scripts.
