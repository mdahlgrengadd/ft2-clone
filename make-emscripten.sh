#!/bin/bash

# FastTracker II Clone - Emscripten Build Script
# This script builds the project for WebAssembly using Emscripten

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}FastTracker II Clone - Emscripten Build Script${NC}"
echo "=================================================="

# Check if Emscripten is installed
if ! command -v emcc &> /dev/null; then
    echo -e "${RED}Error: Emscripten is not installed or not in PATH${NC}"
    echo "Please install Emscripten SDK from: https://emscripten.org/docs/getting_started/downloads.html"
    echo "And activate it with: source /path/to/emsdk/emsdk_env.sh"
    exit 1
fi

echo -e "${GREEN}Emscripten version:${NC}"
emcc --version

# Create build directory
BUILD_DIR="build_emscripten"
if [ -d "$BUILD_DIR" ]; then
    echo -e "${YELLOW}Removing existing build directory...${NC}"
    rm -rf "$BUILD_DIR"
fi

echo -e "${GREEN}Creating build directory...${NC}"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Create web assets directory
echo -e "${GREEN}Creating web assets directory...${NC}"
mkdir -p web/assets

# Copy some sample files (if they exist)
if [ -d "../web/assets" ]; then
    cp -r ../web/assets/* web/assets/ 2>/dev/null || true
fi

# Run CMake with Emscripten
echo -e "${GREEN}Running CMake configuration...${NC}"
emcmake cmake -DCMAKE_BUILD_TYPE=Release -f ../CMakeLists.emscripten.txt ..

# Build the project
echo -e "${GREEN}Building the project...${NC}"
emmake make -j$(nproc 2>/dev/null || echo 4)

# Check if build was successful
if [ -f "web/ft2-clone.html" ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo "Output files:"
    echo "  - web/ft2-clone.html    (Main HTML file)"
    echo "  - web/ft2-clone.js      (JavaScript runtime)"
    echo "  - web/ft2-clone.wasm    (WebAssembly binary)"
    echo "  - web/ft2-clone.data    (Asset data)"
    echo ""
    echo -e "${GREEN}To run the application:${NC}"
    echo "1. Start a local web server in the build directory:"
    echo "   python3 -m http.server 8000"
    echo "   # or"
    echo "   node -e \"require('http').createServer(require('fs').readFileSync('./web/ft2-clone.html')).listen(8000)\""
    echo ""
    echo "2. Open your browser and go to:"
    echo "   http://localhost:8000/web/ft2-clone.html"
    echo ""
    echo -e "${YELLOW}Note:${NC} Due to browser security restrictions, you need to serve the files"
    echo "from a web server. Opening the HTML file directly won't work."
else
    echo -e "${RED}Build failed!${NC}"
    echo "Check the error messages above for details."
    exit 1
fi

echo -e "${GREEN}Build completed successfully!${NC}" 