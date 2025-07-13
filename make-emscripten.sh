#!/bin/bash

# FastTracker II Clone - Emscripten Build Script
# This script builds the project for WebAssembly using Emscripten

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}FastTracker II Clone - Emscripten Build Script${NC}"
echo "=================================================="

# Check if Python is available and use the unified script
if command -v python3 &> /dev/null; then
    echo -e "${CYAN}Using unified Python build script for better cross-platform support...${NC}"
    exec python3 "$(dirname "$0")/build-emscripten.py" "$@"
elif command -v python &> /dev/null; then
    echo -e "${CYAN}Using unified Python build script for better cross-platform support...${NC}"
    exec python "$(dirname "$0")/build-emscripten.py" "$@"
fi

echo -e "${YELLOW}Python not found, falling back to direct bash implementation...${NC}"

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

# Create web_user directory structure if it doesn't exist
if [ ! -d "../web/web_user" ]; then
    echo -e "${YELLOW}Creating web_user directory structure...${NC}"
    mkdir -p ../web/web_user/modules
    cat > ../web/web_user/README.md << 'EOF'
# FT2 Clone Web User Directory

This directory is mapped to /home/web_user in the WebAssembly filesystem.
You can put your module files in the modules/ subdirectory.

Supported formats: .xm, .ft, .nst, .stk, .mod, .s3m, .stm, .fst, .digi, .bem, .it
EOF
fi

# Copy web_user directory for VFS mapping
if [ -d "../web/web_user" ]; then
    echo -e "${GREEN}Copying web_user directory for VFS mapping...${NC}"
    cp -r ../web/web_user ./web/ 2>/dev/null || true
fi

# Run CMake with Emscripten
echo -e "${GREEN}Running CMake configuration...${NC}"
# Backup original CMakeLists.txt if it exists
if [ -f "../CMakeLists.txt" ]; then
    cp ../CMakeLists.txt ../CMakeLists.txt.backup
fi

# Copy Emscripten-specific CMakeLists.txt
cp ../CMakeLists.emscripten.txt ../CMakeLists.txt
emcmake cmake -DCMAKE_BUILD_TYPE=Release ..

# Build the project
echo -e "${GREEN}Building the project...${NC}"
emmake make -j$(nproc 2>/dev/null || echo 4)

# Restore original CMakeLists.txt
if [ -f "../CMakeLists.txt.backup" ]; then
    mv ../CMakeLists.txt.backup ../CMakeLists.txt
fi

# Check if build was successful
if [ -f "web/ft2-clone.html" ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo "Output files:"
    for file in "web/ft2-clone.html" "web/ft2-clone.js" "web/ft2-clone.wasm" "web/ft2-clone.data"; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" 2>/dev/null | cut -f1 || echo "?")
            echo -e "  - ${CYAN}$file${NC} ($size)"
        fi
    done
    echo ""
    echo -e "${GREEN}To run the application:${NC}"
    echo "1. Start a local web server in the build directory:"
    echo -e "   ${YELLOW}cd $BUILD_DIR${NC}"
    echo -e "   ${YELLOW}python3 -m http.server 8000${NC}"
    echo "   # or"
    echo -e "   ${YELLOW}python -m http.server 8000${NC}"
    echo ""
    echo "2. Open your browser and go to:"
    echo -e "   ${YELLOW}http://localhost:8000/web/ft2-clone.html${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} Due to browser security restrictions, you need to serve the files"
    echo "from a web server. Opening the HTML file directly won't work."
else
    echo -e "${RED}Build failed!${NC}"
    echo "Check the error messages above for details."
    exit 1
fi

echo -e "${GREEN}Build completed successfully!${NC}" 