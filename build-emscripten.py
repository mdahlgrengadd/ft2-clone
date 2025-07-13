#!/usr/bin/env python3
"""
FastTracker II Clone - Unified Emscripten Build Script
This script builds the project for WebAssembly using Emscripten on any platform.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

# ANSI color codes for cross-platform colored output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows unless we have colorama"""
        if platform.system() == 'Windows':
            try:
                import colorama
                colorama.init()
            except ImportError:
                cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.CYAN = cls.NC = ''

Colors.disable_on_windows()

def print_colored(message, color=Colors.NC):
    """Print colored message"""
    print(f"{color}{message}{Colors.NC}")

def run_command(cmd, description, cwd=None, check=True):
    """Run a command with colored output"""
    print_colored(f"Running: {description}", Colors.CYAN)
    print_colored(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}", Colors.YELLOW)
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check, cwd=cwd, 
                                  capture_output=False, text=True)
        else:
            result = subprocess.run(cmd, check=check, cwd=cwd, 
                                  capture_output=False, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"Error: Command failed with exit code {e.returncode}", Colors.RED)
        if check:
            sys.exit(1)
        return e

def check_emscripten():
    """Check if Emscripten is installed and available"""
    try:
        result = subprocess.run(['emcc', '--version'], capture_output=True, text=True, check=True)
        print_colored("Emscripten found!", Colors.GREEN)
        print_colored(f"Version: {result.stdout.splitlines()[0]}", Colors.YELLOW)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("Error: Emscripten not found!", Colors.RED)
        print_colored("Please install Emscripten SDK from: https://emscripten.org/docs/getting_started/downloads.html", Colors.RED)
        if platform.system() == 'Windows':
            print_colored("And activate it with: emsdk_env.bat", Colors.RED)
        else:
            print_colored("And activate it with: source /path/to/emsdk/emsdk_env.sh", Colors.RED)
        return False

def get_cpu_count():
    """Get number of CPU cores for parallel build"""
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except:
        return 4

def setup_build_environment():
    """Set up the build environment"""
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    build_dir = script_dir / "build_emscripten"
    
    print_colored("Setting up build environment...", Colors.GREEN)
    
    # Remove existing build directory
    if build_dir.exists():
        print_colored("Removing existing build directory...", Colors.YELLOW)
        shutil.rmtree(build_dir)
    
    # Create build directory structure
    print_colored("Creating build directory...", Colors.GREEN)
    build_dir.mkdir(exist_ok=True)
    (build_dir / "web").mkdir(exist_ok=True)
    (build_dir / "web" / "assets").mkdir(exist_ok=True)
    
    # Create web_user directory structure if it doesn't exist
    web_user_src = script_dir / "web" / "web_user"
    if not web_user_src.exists():
        print_colored("Creating web_user directory structure...", Colors.YELLOW)
        web_user_src.mkdir(parents=True, exist_ok=True)
        (web_user_src / "modules").mkdir(exist_ok=True)
        
        # Create a simple README
        readme_content = """# FT2 Clone Web User Directory

This directory is mapped to /home/web_user in the WebAssembly filesystem.
You can put your module files in the modules/ subdirectory.

Supported formats: .xm, .ft, .nst, .stk, .mod, .s3m, .stm, .fst, .digi, .bem, .it
"""
        (web_user_src / "README.md").write_text(readme_content)
    
    return script_dir, build_dir

def copy_assets(script_dir, build_dir):
    """Copy web assets if they exist"""
    # Copy web assets
    web_assets = script_dir / "web" / "assets"
    if web_assets.exists():
        print_colored("Copying web assets...", Colors.GREEN)
        shutil.copytree(web_assets, build_dir / "web" / "assets", dirs_exist_ok=True)
    
    # Copy web_user directory  
    web_user_src = script_dir / "web" / "web_user"
    web_user_dst = build_dir / "web" / "web_user"
    if web_user_src.exists():
        print_colored("Copying web_user directory for VFS mapping...", Colors.GREEN)
        shutil.copytree(web_user_src, web_user_dst, dirs_exist_ok=True)

def backup_and_restore_cmake(script_dir):
    """Context manager to backup and restore CMakeLists.txt"""
    class CMakeBackup:
        def __init__(self, script_dir):
            self.script_dir = script_dir
            self.cmake_file = script_dir / "CMakeLists.txt"
            self.emscripten_cmake = script_dir / "CMakeLists.emscripten.txt"
            self.backup_file = script_dir / "CMakeLists.txt.backup"
            
        def __enter__(self):
            # Backup existing CMakeLists.txt if it exists
            if self.cmake_file.exists():
                shutil.copy2(self.cmake_file, self.backup_file)
            
            # Copy Emscripten-specific CMakeLists.txt
            print_colored("Using Emscripten-specific CMakeLists.txt...", Colors.GREEN)
            shutil.copy2(self.emscripten_cmake, self.cmake_file)
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Restore original CMakeLists.txt
            if self.backup_file.exists():
                shutil.move(self.backup_file, self.cmake_file)
            elif self.cmake_file.exists():
                self.cmake_file.unlink()
    
    return CMakeBackup(script_dir)

def get_source_files(script_dir):
    """Get all source files for compilation"""
    source_patterns = [
        "src/*.c",
        "src/gfxdata/*.c", 
        "src/mixer/*.c",
        "src/scopes/*.c",
        "src/modloaders/*.c",
        "src/smploaders/*.c",
        "src/libflac/*.c"
    ]
    
    all_source_files = []
    for pattern in source_patterns:
        files = list(script_dir.glob(pattern))
        all_source_files.extend([str(f) for f in files])
    
    print_colored(f"Found {len(all_source_files)} source files", Colors.GREEN)
    return all_source_files

def build_with_direct_emcc(script_dir, build_dir):
    """Build using direct emcc compilation (like PowerShell script)"""
    print_colored("Building with direct emcc compilation...", Colors.GREEN)
    
    # Get source files
    source_files = get_source_files(script_dir)
    
    # Define compiler flags
    compiler_flags = [
        "-O3",
        "-DNDEBUG", 
        "-DHAS_LIBFLAC",
        "-D__EMSCRIPTEN__",
        "-Wall",
        "-Wno-unused-result",
        "-Wno-missing-field-initializers",
        "-Wno-strict-aliasing",
        "-I", "src",
        "-I", "src/libflac",
        "-I", "src/mixer", 
        "-I", "src/scopes"
    ]
    
    # Define linker flags
    linker_flags = [
        "-sUSE_SDL=2",
        "-sALLOW_MEMORY_GROWTH=1", 
        "-sINITIAL_MEMORY=67108864",
        "-sSTACK_SIZE=1048576",
        "-sASYNCIFY=1",
        "-sASYNCIFY_STACK_SIZE=65536",
        "-sEXPORTED_RUNTIME_METHODS=ccall,cwrap,FS",
        "-sEXPORTED_FUNCTIONS=_main,_malloc,_free,_refreshModuleDirectory",
        "-sFORCE_FILESYSTEM=1",
        "-lidbfs.js",
        f"--embed-file={script_dir}/src/gfxdata/bmp@/",
        f"--shell-file={script_dir}/web/shell.html"
    ]
    
    # Add preload files if they exist
    preload_flags = []
    web_user_dir = script_dir / "web" / "web_user"
    if web_user_dir.exists():
        preload_flags.extend([
            f"--preload-file={web_user_dir}@/home/web_user"
        ])
        print_colored("Including web_user directory in VFS", Colors.CYAN)
    
    # Output file
    output_file = build_dir / "web" / "ft2-clone.html"
    
    # Build the command
    cmd = ["emcc"] + compiler_flags + source_files + linker_flags + preload_flags + ["-o", str(output_file)]
    
    print_colored(f"Running emcc with {len(cmd)} arguments...", Colors.YELLOW)
    
    # Change to script directory for relative paths
    old_cwd = os.getcwd()
    try:
        os.chdir(script_dir)
        run_command(cmd, "Direct emcc compilation")
    finally:
        os.chdir(old_cwd)

def build_with_cmake(script_dir, build_dir):
    """Build using CMake (recommended approach)"""
    print_colored("Building with CMake...", Colors.GREEN)
    
    with backup_and_restore_cmake(script_dir):
        # Configure with CMake
        print_colored("Running CMake configuration...", Colors.GREEN)
        cmake_cmd = ['emcmake', 'cmake', '-DCMAKE_BUILD_TYPE=Release', '..']
        run_command(cmake_cmd, "CMake configuration", cwd=build_dir)
        
        # Build with make
        print_colored("Building the project...", Colors.GREEN)
        cpu_count = get_cpu_count()
        make_cmd = ['emmake', 'make', f'-j{cpu_count}']
        run_command(make_cmd, f"Building with {cpu_count} parallel jobs", cwd=build_dir)

def verify_build(build_dir):
    """Verify that the build was successful"""
    html_file = build_dir / "web" / "ft2-clone.html"
    js_file = build_dir / "web" / "ft2-clone.js"
    wasm_file = build_dir / "web" / "ft2-clone.wasm"
    data_file = build_dir / "web" / "ft2-clone.data"
    
    if html_file.exists():
        print_colored("Build successful!", Colors.GREEN)
        print("Output files:")
        for file, desc in [
            (html_file, "Main HTML file"),
            (js_file, "JavaScript runtime"),
            (wasm_file, "WebAssembly binary"),
            (data_file, "Asset data")
        ]:
            if file.exists():
                size_mb = file.stat().st_size / (1024 * 1024)
                print_colored(f"  - {file.relative_to(build_dir)} ({size_mb:.1f} MB) - {desc}", Colors.CYAN)
            else:
                print_colored(f"  - {file.relative_to(build_dir)} - {desc} (NOT FOUND)", Colors.YELLOW)
        
        print_colored("\nTo run the application:", Colors.GREEN)
        print("1. Start a local web server in the build directory:")
        print_colored(f"   cd {build_dir}", Colors.YELLOW)
        print_colored("   python3 -m http.server 8000", Colors.YELLOW)
        print("   # or")
        print_colored("   python -m http.server 8000", Colors.YELLOW)
        print("")
        print("2. Open your browser and go to:")
        print_colored("   http://localhost:8000/web/ft2-clone.html", Colors.YELLOW)
        print("")
        print_colored("Note:", Colors.YELLOW)
        print("Due to browser security restrictions, you need to serve the files")
        print("from a web server. Opening the HTML file directly won't work.")
        
        return True
    else:
        print_colored("Build failed!", Colors.RED)
        print("Output file not found. Check the error messages above for details.")
        return False

def main():
    """Main build function"""
    print_colored("FastTracker II Clone - Unified Emscripten Build Script", Colors.GREEN)
    print_colored("=" * 60, Colors.GREEN)
    print_colored(f"Platform: {platform.system()} {platform.machine()}", Colors.BLUE)
    print_colored(f"Python: {sys.version.split()[0]}", Colors.BLUE)
    print("")
    
    # Check prerequisites
    if not check_emscripten():
        sys.exit(1)
    
    # Set up build environment
    script_dir, build_dir = setup_build_environment()
    
    # Copy assets
    copy_assets(script_dir, build_dir)
    
    try:
        # Try direct emcc compilation first (more reliable)
        build_with_direct_emcc(script_dir, build_dir)
        
        # Verify build success
        success = verify_build(build_dir)
        
        if success:
            print_colored("Build completed successfully!", Colors.GREEN)
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_colored("\nBuild interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
