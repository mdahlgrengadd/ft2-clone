// Alternative mouse coordinate fix for Emscripten
// If the current SDL_GetWindowSize approach doesn't work,
// this version uses canvas element dimensions directly

#ifdef __EMSCRIPTEN__
#include <emscripten.h>

// Alternative approach: Get canvas size directly from DOM
EM_JS(int, get_canvas_width, (), {
    var canvas = document.getElementById('canvas');
    return canvas ? canvas.clientWidth : 632;
});

EM_JS(int, get_canvas_height, (), {
    var canvas = document.getElementById('canvas');
    return canvas ? canvas.clientHeight : 400;
});

// Alternative mouse coordinate calculation
void readMouseXY_Alternative(void)
{
    int32_t mx, my, windowX, windowY;

    if (mouse.setPosFlag)
    {
        if (!video.windowHidden)
            SDL_WarpMouseInWindow(video.window, mouse.setPosX, mouse.setPosY);
        mouse.setPosFlag = false;
        return;
    }

    // Get mouse coordinates from SDL
    if (video.fullscreen)
    {
        mouse.buttonState = SDL_GetMouseState(&mx, &my);
        mouse.absX = mx;
        mouse.absY = my;
    }
    else
    {
        mouse.buttonState = SDL_GetGlobalMouseState(&mx, &my);
        mouse.absX = mx;
        mouse.absY = my;
        SDL_GetWindowPosition(video.window, &windowX, &windowY);
        mx -= windowX;
        my -= windowY;
    }

    mouse.rawX = mx;
    mouse.rawY = my;

    // Alternative approach: Use canvas dimensions directly
    int32_t canvasW = get_canvas_width();
    int32_t canvasH = get_canvas_height();

    // Direct mapping to logical coordinates
    if (canvasW > 0 && canvasH > 0)
    {
        mouse.x = (mx * SCREEN_W) / canvasW;
        mouse.y = (my * SCREEN_H) / canvasH;
    }
    else
    {
        // Fallback: direct mapping
        mouse.x = mx;
        mouse.y = my;
    }

    // Bounds checking
    if (mouse.x < 0)
        mouse.x = 0;
    if (mouse.y < 0)
        mouse.y = 0;
    if (mouse.x >= SCREEN_W)
        mouse.x = SCREEN_W - 1;
    if (mouse.y >= SCREEN_H)
        mouse.y = SCREEN_H - 1;

    // Debug output
    static int32_t debugCount = 0;
    if (++debugCount % 60 == 0)
    {
        printf("ALT MOUSE: raw(%d,%d) canvas(%dx%d) screen(%dx%d) final(%d,%d)\n",
               mx, my, canvasW, canvasH, SCREEN_W, SCREEN_H, mouse.x, mouse.y);
    }
}

#endif