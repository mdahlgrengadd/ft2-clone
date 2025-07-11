# FastTracker II Clone - WebAssembly/Emscripten Build

This document explains how to build and run the FastTracker II Clone in a web browser using Emscripten.

## Prerequisites

1. **Emscripten SDK**: Install the Emscripten SDK from https://emscripten.org/docs/getting_started/downloads.html
2. **CMake**: Version 3.7 or higher
3. **Git**: To clone the repository (if not already done)

## Installation

### 1. Install Emscripten SDK

```bash
# Download and install Emscripten SDK
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest

# Activate Emscripten environment (run this in each new terminal session)
source ./emsdk_env.sh
```

### 2. Verify Installation

```bash
emcc --version
```

## Building

### Option 1: Using the build script (Recommended)

**Linux/macOS:**
```bash
chmod +x make-emscripten.sh
./make-emscripten.sh
```

**Windows:**
```cmd
make-emscripten.bat
```

### Option 2: Manual build

```bash
# Create build directory
mkdir build_emscripten
cd build_emscripten

# Configure with CMake
emcmake cmake -DCMAKE_BUILD_TYPE=Release -f ../CMakeLists.emscripten.txt ..

# Build
emmake make -j4
```

## Running

1. **Start a local web server** in the build directory:
   ```bash
   # Python 3
   python3 -m http.server 8000
   
   # Python 2
   python -m SimpleHTTPServer 8000
   
   # Node.js (if you have it)
   npx http-server -p 8000
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000/web/ft2-clone.html
   ```

## Features and Limitations

### Available Features
- Complete FastTracker II interface
- Module playback (XM, MOD, S3M, etc.)
- Sample editing and effects
- Pattern editing
- Built-in libFLAC support
- File drag-and-drop support
- Fullscreen mode

### Limitations (Web-specific)
- **No MIDI support** (browsers don't support MIDI input/output reliably)
- **No audio recording** (microphone access requires special permissions)
- **File I/O restrictions** (can only access files provided by the user)
- **Performance** may be slightly lower than native builds
- **Memory usage** is higher due to WebAssembly overhead

## File Management

The web version uses Emscripten's virtual filesystem:

- Use the "Load Module" button to load music files
- Files are temporarily stored in the browser's memory
- No permanent file storage (files are lost when page is reloaded)
- Supported formats: .xm, .mod, .s3m, .it, .stm, .smp, .wav, .flac, .aiff

## Troubleshooting

### Build Issues

1. **"emcc command not found"**
   - Make sure Emscripten is installed and activated
   - Run `source /path/to/emsdk/emsdk_env.sh`

2. **CMake configuration fails**
   - Ensure you're using the correct CMakeLists file: `CMakeLists.emscripten.txt`
   - Check that all source files are present

3. **Link errors**
   - The build automatically excludes MIDI-related files
   - Ensure libFLAC sources are available in `src/libflac/`

### Runtime Issues

1. **Page won't load**
   - Must be served from a web server (not opened directly)
   - Check browser console for error messages

2. **No audio**
   - Click somewhere on the page to enable audio context
   - Check browser audio settings

3. **Files won't load**
   - Use the "Load Module" button, don't drag files directly
   - Check that file format is supported

## Browser Compatibility

- **Chrome/Chromium**: Full support
- **Firefox**: Full support
- **Safari**: Full support (macOS/iOS)
- **Edge**: Full support
- **Internet Explorer**: Not supported

## Performance Tips

1. **Use Chrome or Firefox** for best performance
2. **Close other tabs** to free up memory
3. **Use smaller modules** for better performance
4. **Enable hardware acceleration** in browser settings

## Development

### Adding Web-specific Features

To add features specific to the web version, use the `__EMSCRIPTEN__` preprocessor define:

```c
#ifdef __EMSCRIPTEN__
    // Web-specific code
#endif
```

### Debugging

1. **Enable debug build:**
   ```bash
   emcmake cmake -DCMAKE_BUILD_TYPE=Debug -f ../CMakeLists.emscripten.txt ..
   ```

2. **Use browser developer tools** to debug JavaScript/WebAssembly

3. **Check the console** for error messages

## License

This web build uses the same license as the main project (BSD 3-Clause). See LICENSE file for details.

## Contributing

Please report any web-specific issues on the main project repository. When reporting issues, please mention:
- Browser and version
- Operating system
- Console error messages
- Steps to reproduce

## Resources

- [Emscripten Documentation](https://emscripten.org/docs/)
- [WebAssembly Documentation](https://webassembly.org/)
- [SDL2 with Emscripten](https://wiki.libsdl.org/SDL2/README/emscripten)
- [Original FastTracker II Clone](https://github.com/8bitbubsy/ft2-clone) 