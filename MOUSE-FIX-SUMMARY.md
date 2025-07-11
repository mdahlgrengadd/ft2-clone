# Mouse Coordinate Fix Summary

## Problem
The FastTracker II Clone had severe mouse coordinate offset issues when running in web browsers via Emscripten. Mouse clicks were severely misaligned, making the interface unusable. **Additionally, fullscreen mode with different aspect ratios caused even worse coordinate issues due to letterboxing/pillarboxing**.

## Root Cause
1. **SDL Coordinate System**: SDL's mouse coordinate reporting system doesn't align properly with the HTML5 Canvas element in Emscripten
2. **Fullscreen Letterboxing**: In fullscreen mode, when the screen aspect ratio differs from FastTracker II's aspect ratio (632x400 ≈ 1.58:1), the canvas gets letterboxed (black bars on top/bottom) or pillarboxed (black bars on sides), but the coordinate mapping was done across the entire canvas instead of just the rendered area

## Solution
Implemented a **DOM-based mouse coordinate system** with **aspect ratio-aware letterboxing/pillarboxing support**:

### Changes Made

#### 1. C Code Changes (`src/ft2_mouse.c`)
- Added Emscripten-specific mouse coordinate handling in `readMouseXY()` function
- Used `EM_ASM_INT` to directly query JavaScript for mouse coordinates
- **NEW**: Implemented letterboxing/pillarboxing detection and calculation
- **NEW**: Added aspect ratio comparison between canvas and FastTracker II (1.58:1)
- **NEW**: Proper coordinate mapping within the actual rendered area only
- Added coordinate scaling from rendered area dimensions to logical screen coordinates (632x400)

#### 2. JavaScript Changes (`web/shell.html`)
- Added `Module.lastMouseEvent` to store the most recent mouse event
- Implemented comprehensive mouse event capturing (`mousemove`, `mousedown`, `mouseup`, `click`)
- Added event listeners for both canvas and document to handle mouse movement outside canvas bounds
- **NEW**: Enhanced debug information display with render area and aspect ratio information
- **NEW**: JavaScript-side letterboxing/pillarboxing calculation for debug verification

### Technical Details

#### Aspect Ratio Handling
- **FastTracker II Aspect Ratio**: 632:400 = 1.58:1
- **Pillarboxing**: When canvas is wider than 1.58:1 (black bars on sides)
- **Letterboxing**: When canvas is taller than 1.58:1 (black bars on top/bottom)

#### Coordinate Transformation Flow
1. **JavaScript**: Capture mouse events with `clientX`/`clientY` coordinates
2. **JavaScript**: Calculate canvas-relative coordinates using `getBoundingClientRect()`
3. **C Code**: Access stored mouse event from JavaScript via `Module.lastMouseEvent`
4. **C Code**: Calculate aspect ratios and determine letterboxing/pillarboxing
5. **C Code**: Calculate actual rendered area within the canvas
6. **C Code**: Map coordinates from rendered area to logical screen coordinates (632x400)
7. **C Code**: Apply bounds checking and handle coordinates outside rendered area

#### Key Code Snippets

**C Code (ft2_mouse.c):**
```c
#ifdef __EMSCRIPTEN__
// Calculate actual rendered area (accounting for letterboxing/pillarboxing)
const double ft2AspectRatio = 632.0 / 400.0;
const double canvasAspectRatio = (double)canvasW / (double)canvasH;

int32_t renderW, renderH, renderX, renderY;

if (canvasAspectRatio > ft2AspectRatio) {
    // Canvas is wider than FT2 - pillarboxing (black bars on sides)
    renderH = canvasH;
    renderW = (int32_t)(canvasH * ft2AspectRatio);
    renderX = (canvasW - renderW) / 2;
    renderY = 0;
} else {
    // Canvas is taller than FT2 - letterboxing (black bars on top/bottom)
    renderW = canvasW;
    renderH = (int32_t)(canvasW / ft2AspectRatio);
    renderX = 0;
    renderY = (canvasH - renderH) / 2;
}

// Check if mouse is within the rendered area
if (canvasMouseX >= renderX && canvasMouseX < renderX + renderW &&
    canvasMouseY >= renderY && canvasMouseY < renderY + renderH) {
    // Mouse is within rendered area - map to logical coordinates
    int32_t relativeX = canvasMouseX - renderX;
    int32_t relativeY = canvasMouseY - renderY;
    
    mouse.x = (int32_t)((relativeX * SCREEN_W) / renderW);
    mouse.y = (int32_t)((relativeY * SCREEN_H) / renderH);
} else {
    // Mouse is outside rendered area (in letterbox/pillarbox) - clamp to edges
    // ... edge clamping logic
}
#endif
```

**JavaScript Debug (shell.html):**
```javascript
// Calculate letterboxing/pillarboxing like the C code does
const ft2AspectRatio = 632.0 / 400.0;
const canvasAspectRatio = rect.width / rect.height;

let renderW, renderH, renderX, renderY;

if (canvasAspectRatio > ft2AspectRatio) {
    // Pillarboxing (black bars on sides)
    renderH = rect.height;
    renderW = rect.height * ft2AspectRatio;
    renderX = (rect.width - renderW) / 2;
    renderY = 0;
} else {
    // Letterboxing (black bars on top/bottom)
    renderW = rect.width;
    renderH = rect.width / ft2AspectRatio;
    renderX = 0;
    renderY = (rect.height - renderH) / 2;
}
```

### Benefits
- **Precise Coordinates**: Mouse coordinates now accurately map to UI elements in all screen modes
- **Fullscreen Support**: Proper handling of letterboxing/pillarboxing in fullscreen mode
- **Aspect Ratio Aware**: Correctly handles different screen aspect ratios
- **Canvas-Aware**: Handles canvas scaling and positioning correctly
- **Browser Compatible**: Works across different browsers and viewport sizes
- **Responsive**: Adapts to canvas resizing and fullscreen mode transitions
- **Debug Support**: Enhanced debug overlay showing render area and aspect ratio information

### Testing
- Added debug overlay (press 'D' to toggle) showing:
  - Real-time coordinate mapping
  - Canvas vs. render area dimensions
  - Aspect ratio comparison
  - Letterboxing/pillarboxing detection
- Console output shows detailed coordinate transformation
- Visual feedback confirms accurate mouse positioning in all modes

### Debug Information
The debug overlay now shows:
- **Mouse Raw**: Global screen coordinates
- **Mouse Canvas**: Canvas-relative coordinates
- **Mouse FT2**: Final FastTracker II logical coordinates
- **Canvas Size**: Actual canvas dimensions
- **Render Area**: Calculated rendered area (WxH+X+Y format)
- **Aspect Info**: Canvas vs. FastTracker II aspect ratio comparison

### Files Modified
- `src/ft2_mouse.c` - Core mouse coordinate handling with fullscreen support
- `web/shell.html` - JavaScript mouse event capture and enhanced debug system

### Result
The mouse coordinate issue is now **completely resolved** for both windowed and fullscreen modes. The FastTracker II Clone interface is fully usable in web browsers with accurate mouse positioning and clicking, regardless of screen aspect ratio or fullscreen mode. 