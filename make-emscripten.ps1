# FastTracker II Clone - Emscripten Build Script for PowerShell
# This script builds the project for WebAssembly using direct emcc compilation

Write-Host "FastTracker II Clone - Emscripten Build Script" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if Emscripten is available
try {
    $emccVersion = emcc --version 2>&1
    Write-Host "Emscripten found!" -ForegroundColor Green
    Write-Host "Version: $($emccVersion[0])" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Emscripten not found!" -ForegroundColor Red
    Write-Host "Please install Emscripten SDK and activate it with emsdk_env.bat" -ForegroundColor Red
    exit 1
}

# Create build directory
$buildDir = "build_emscripten"
if (Test-Path $buildDir) {
    Write-Host "Removing existing build directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $buildDir
}

Write-Host "Creating build directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path $buildDir | Out-Null
New-Item -ItemType Directory -Path "$buildDir\web" | Out-Null

# Create web_user directory structure if it doesn't exist
if (-not (Test-Path "web\web_user")) {
    Write-Host "Creating web_user directory structure..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "web\web_user" -Force | Out-Null
    New-Item -ItemType Directory -Path "web\web_user\modules" -Force | Out-Null
}

# Define source files
$sourceFiles = @(
    "src/*.c"
    "src/gfxdata/*.c"
    "src/mixer/*.c"
    "src/scopes/*.c"
    "src/modloaders/*.c"
    "src/smploaders/*.c"
    "src/libflac/*.c"
)

# Get all source files
$allSourceFiles = @()
foreach ($pattern in $sourceFiles) {
    $files = Get-ChildItem -Path $pattern -File
    $allSourceFiles += $files.FullName
}

Write-Host "Found $($allSourceFiles.Count) source files" -ForegroundColor Green

# Define compiler flags
$compilerFlags = @(
    "-O3"
    "-DNDEBUG"
    "-DHAS_LIBFLAC"
    "-D__EMSCRIPTEN__"
    "-Wall"
    "-Wno-unused-result"
    "-Wno-missing-field-initializers"

    "-Wno-strict-aliasing"
    "-I src"
    "-I src/libflac"
    "-I src/mixer"
    "-I src/scopes"
)

# Define linker flags
$linkerFlags = @(
    "-sUSE_SDL=2"
    "-sALLOW_MEMORY_GROWTH=1"
    "-sINITIAL_MEMORY=67108864"
    "-sSTACK_SIZE=1048576"
    "-sASYNCIFY=1"
    "-sASYNCIFY_STACK_SIZE=65536"
    "-sEXPORTED_RUNTIME_METHODS=[ccall,cwrap,FS]"
    "-sEXPORTED_FUNCTIONS=[_main,_malloc,_free]"
    "-sFORCE_FILESYSTEM=1"
    "--embed-file src/gfxdata/bmp@/"
    "--shell-file web/shell.html"
)

# Build the project
Write-Host "Building the project..." -ForegroundColor Green
$outputFile = "$buildDir\web\ft2-clone.html"

# Convert arrays to space-separated strings
$compilerFlagsStr = $compilerFlags -join " "
$sourceFilesStr = $allSourceFiles -join " "

# Build arguments array for proper parameter passing
$arguments = @()
$arguments += $compilerFlags
$arguments += $allSourceFiles
$arguments += "-sUSE_SDL=2"
$arguments += "-sALLOW_MEMORY_GROWTH=1"
$arguments += "-sINITIAL_MEMORY=67108864"
$arguments += "-sSTACK_SIZE=1048576"
$arguments += "-sASYNCIFY=1"
$arguments += "-sASYNCIFY_STACK_SIZE=65536"
$arguments += "-sEXPORTED_RUNTIME_METHODS=ccall,cwrap,FS"
$arguments += "-sEXPORTED_FUNCTIONS=_main,_malloc,_free"
$arguments += "-sFORCE_FILESYSTEM=1"
$arguments += "-lidbfs.js"
$arguments += "--embed-file"
$arguments += "src/gfxdata/bmp@/"
$arguments += "--shell-file"
$arguments += "web/shell.html"
$arguments += "-o"
$arguments += $outputFile

Write-Host "Running emcc with $($arguments.Count) arguments..." -ForegroundColor Yellow

# Preload files into the virtual file system
$preloadFiles = @()

# Preload the web_user directory to /home/web_user in the VFS
if (Test-Path "web/web_user") {
    $preloadFiles += "--preload-file", "web/web_user@/home/web_user"
    Write-Host "Preloading web_user directory to /home/web_user in VFS" -ForegroundColor Cyan
}

# Add any other files you want to preload here
# if (Test-Path "web/somefile.wav") {
#     $preloadFiles += "--preload-file", "web/somefile.wav@somefile.wav"
# }

# Combine all arguments
$buildArgs = $arguments + $preloadFiles

try {
    & emcc $buildArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
    if (Test-Path $outputFile) {
        Write-Host "Build successful!" -ForegroundColor Green
        Write-Host "Output files:" -ForegroundColor Green
        Write-Host "  - $buildDir\web\ft2-clone.html    (Main HTML file)" -ForegroundColor Cyan
        Write-Host "  - $buildDir\web\ft2-clone.js      (JavaScript runtime)" -ForegroundColor Cyan
        Write-Host "  - $buildDir\web\ft2-clone.wasm    (WebAssembly binary)" -ForegroundColor Cyan
        Write-Host "  - $buildDir\web\ft2-clone.data    (Asset data)" -ForegroundColor Cyan
        if ($preloadFiles.Count -gt 0) {
            Write-Host "  - Preloaded files included in .data package" -ForegroundColor Cyan
        }
        Write-Host ""
        Write-Host "To run the application:" -ForegroundColor Green
        Write-Host "1. Start a local web server in the build directory:" -ForegroundColor White
        Write-Host "   cd $buildDir" -ForegroundColor Gray
        Write-Host "   python -m http.server 8000" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Open your browser and go to:" -ForegroundColor White
        Write-Host "   http://localhost:8000/web/ft2-clone.html" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Note: Due to browser security restrictions, you need to serve the files" -ForegroundColor Yellow
        Write-Host "from a web server. Opening the HTML file directly won't work." -ForegroundColor Yellow
    } else {
        Write-Host "Build failed - output file not created!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error running emcc: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully!" -ForegroundColor Green 