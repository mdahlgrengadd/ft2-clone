#!/bin/bash

echo "Testing Emscripten installation..."

# Check if emcc is available
if ! command -v emcc &> /dev/null; then
    echo "❌ Emscripten not found!"
    echo "Please install Emscripten SDK from: https://emscripten.org/docs/getting_started/downloads.html"
    exit 1
fi

echo "✅ Emscripten found!"
echo "Version:"
emcc --version

# Test basic compilation
echo "Testing basic compilation..."
cat > test.c << 'EOF'
#include <stdio.h>
int main() {
    printf("Hello from Emscripten!\n");
    return 0;
}
EOF

if emcc test.c -o test.html; then
    echo "✅ Basic compilation successful!"
    echo "Test files created: test.html, test.js, test.wasm"
    rm -f test.c test.html test.js test.wasm
    echo "✅ All tests passed! You can now build the FastTracker II Clone."
else
    echo "❌ Basic compilation failed!"
    echo "Please check your Emscripten installation."
    rm -f test.c
    exit 1
fi 