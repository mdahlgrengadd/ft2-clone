# Web User Directory

This directory is mapped to `/home/web_user` in the Emscripten virtual file system (VFS).

## Structure

- `modules/` - Contains music module files (.xm, .mod, .s3m, etc.)
  - `db_cydon.xm` - Sample FastTracker II module

## Usage

When the WebAssembly application runs, this entire directory structure becomes available at `/home/web_user` within the VFS. This allows the FastTracker II Clone to access files as if they were in a local file system.

## Adding Files

To add more files:

1. Place them in the appropriate subdirectory here
2. Rebuild the project with `make-emscripten.ps1` or `make-emscripten.sh`
3. The files will be embedded in the WebAssembly build

## VFS Path Mapping

- Local: `web/web_user/` → VFS: `/home/web_user/`
- Local: `web/web_user/modules/` → VFS: `/home/web_user/modules/`
