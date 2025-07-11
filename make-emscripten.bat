@echo off
REM FastTracker II Clone - Emscripten Build Script for Windows
REM This script builds the project for WebAssembly using Emscripten

setlocal enabledelayedexpansion

echo FastTracker II Clone - Emscripten Build Script
echo ==================================================

REM Check if Emscripten is installed
emcc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Emscripten is not installed or not in PATH
    echo Please install Emscripten SDK from: https://emscripten.org/docs/getting_started/downloads.html
    echo And activate it with: emsdk_env.bat
    pause
    exit /b 1
)

echo Emscripten version:
emcc --version

REM Create build directory
set BUILD_DIR=build_emscripten
if exist "%BUILD_DIR%" (
    echo Removing existing build directory...
    rmdir /s /q "%BUILD_DIR%"
)

echo Creating build directory...
mkdir "%BUILD_DIR%"
cd "%BUILD_DIR%"

REM Create web assets directory
echo Creating web assets directory...
mkdir web\assets

REM Copy some sample files (if they exist)
if exist "..\web\assets" (
    xcopy /e /i /q "..\web\assets\*" "web\assets\" >nul 2>&1
)

REM Run CMake with Emscripten
echo Running CMake configuration...
emcmake cmake -DCMAKE_BUILD_TYPE=Release -f ..\CMakeLists.emscripten.txt ..
if %errorlevel% neq 0 (
    echo CMake configuration failed!
    pause
    exit /b 1
)

REM Build the project
echo Building the project...
emmake make -j4
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

REM Check if build was successful
if exist "web\ft2-clone.html" (
    echo Build successful!
    echo Output files:
    echo   - web\ft2-clone.html    ^(Main HTML file^)
    echo   - web\ft2-clone.js      ^(JavaScript runtime^)
    echo   - web\ft2-clone.wasm    ^(WebAssembly binary^)
    echo   - web\ft2-clone.data    ^(Asset data^)
    echo.
    echo To run the application:
    echo 1. Start a local web server in the build directory:
    echo    python -m http.server 8000
    echo    # or
    echo    python -m SimpleHTTPServer 8000  ^(Python 2^)
    echo.
    echo 2. Open your browser and go to:
    echo    http://localhost:8000/web/ft2-clone.html
    echo.
    echo Note: Due to browser security restrictions, you need to serve the files
    echo from a web server. Opening the HTML file directly won't work.
) else (
    echo Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo Build completed successfully!
pause 