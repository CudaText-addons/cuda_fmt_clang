"""clang-format formatter plugin for CudaText with cuda_fmt integration."""

import os
import subprocess
import json
import shutil
import cudatext as ct
from cuda_fmt import get_config_filename

# clang-format version cache (populated on plugin load)
_CLANG_FORMAT_VERSION_CACHE = None

# Background process fetching version
_VERSION_PROCESS = None

# Platform detection
IS_WIN = os.name == 'nt'

# Plugin loaded
print("clang-format: Plugin initialized")

def _start_version_cache():
    """Start background process to get clang-format version (non-blocking)."""
    global _VERSION_PROCESS

    try:
        config = load_config()
        clang_format_path = find_clang_format_executable(config)

        if clang_format_path:
            # Start process but DON'T wait (non-blocking!)
            _VERSION_PROCESS = subprocess.Popen(
                [clang_format_path, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=_get_hidden_startupinfo()
            )
            print("clang-format: Version check started in background")
    except Exception as e:
        print(f"NOTE: Could not start version check: {e}")

def _get_hidden_startupinfo():
    """Get startupinfo to hide console window on Windows."""
    if IS_WIN:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None

# Supported lexers (clang-format auto-detects language by file extension)
SUPPORTED_LEXERS = {
    'C': True,
    'C++': True,
    'C#': True,
    'Java': True,
    'Objective-C': True,
    'Objective-C++': True,
    'JavaScript': True,
    'TypeScript': True,
    'Protocol Buffers': True,  # .proto files
}

# Default configuration structure
DEFAULT_CONFIG = {
    'clang_format_path': '',
    '// clang_format_path': 'Custom path to clang-format executable. Leave empty for auto-detection',

    'timeout_seconds': 10,
    '// timeout_seconds': 'clang-format subprocess timeout in seconds (default: 10)',

    'use_clang_format_file': True,
    '// use_clang_format_file': 'Use .clang-format file from project (recommended: true). If false, uses style option below',

    'style': 'LLVM',
    '// style': 'Predefined style when no .clang-format found: LLVM, Google, Chromium, Mozilla, WebKit, Microsoft, GNU, or custom JSON string (default: LLVM)',

    '// [!] STYLE OPTIONS NOTE': 'Create .clang-format file in your project for full customization. See: https://clang.llvm.org/docs/ClangFormatStyleOptions.html'
}

def get_config_path():
    """Get configuration file path (portable-aware)."""

    # Try cuda_fmt first
    if config_path := get_config_filename('clang'):
        return config_path

    # Fallback: build path manually
    app_dir = ct.app_path(ct.APP_DIR_SETTINGS)
    return os.path.join(app_dir, 'cuda_fmt_clang.json')

def _filter_comments(config_dict):
    """Remove comment keys (starting with //) from config dict."""
    return {k: v for k, v in config_dict.items() if not k.startswith('//')}

def load_config():
    """Load plugin configuration from JSON file."""
    import copy

    config_path = get_config_path()

    # Guard clause: no config path available
    if config_path is None:
        return _filter_comments(copy.deepcopy(DEFAULT_CONFIG))

    # Guard clause: config file doesn't exist - create it
    if not os.path.exists(config_path):
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print("clang-format: Created default config file")
        except Exception as e:
            print(f"NOTE: Cannot create clang-format config: {e}")
        return _filter_comments(copy.deepcopy(DEFAULT_CONFIG))

    # Load existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)

        # Deep merge user config with defaults
        import copy
        merged_config = copy.deepcopy(DEFAULT_CONFIG)
        merged_config.update(user_config)

        return _filter_comments(merged_config)

    except Exception as e:
        print(f"NOTE: Cannot load clang-format config: {e}")
        return _filter_comments(copy.deepcopy(DEFAULT_CONFIG))

def find_clang_format_executable(config):
    """Find clang-format executable (custom path, portable, system PATH, or common LLVM locations)."""

    # 1. Custom path from config
    custom_path = config.get('clang_format_path', '').strip()
    if custom_path:
        if os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
            print(f"clang-format: Using custom path: {custom_path}")
            return custom_path
        else:
            print(f"NOTE: Custom clang-format path not found or not executable: {custom_path}")

    # 2. CudaText tools folder (portable-aware using APP_DIR_DATA)
    app_dir = ct.app_path(ct.APP_DIR_DATA)
    cudatext_root = os.path.dirname(app_dir)
    tools_dir = os.path.join(cudatext_root, 'tools', 'Clang')

    # Windows: clang-format.exe
    # Unix: clang-format
    exe_name = 'clang-format.exe' if IS_WIN else 'clang-format'
    bundled = os.path.join(tools_dir, exe_name)
    if os.path.isfile(bundled) and os.access(bundled, os.X_OK):
        print(f"clang-format: Using bundled version: {bundled}")
        return bundled

    # 3. System PATH
    if clang_format_in_path := shutil.which('clang-format'):
        print(f"clang-format: Using system PATH: {clang_format_in_path}")
        return clang_format_in_path

    # 4. Common LLVM installation locations
    common_paths = []
    
    if IS_WIN:
        # Windows: Check Program Files
        for base in [os.environ.get('ProgramFiles', 'C:\\Program Files'),
                     os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')]:
            common_paths.extend([
                os.path.join(base, 'LLVM', 'bin', 'clang-format.exe'),
                os.path.join(base, 'Microsoft Visual Studio', '*', '*', 'VC', 'Tools', 'Llvm', 'bin', 'clang-format.exe'),
            ])
    else:
        # Linux/macOS: Check common install locations
        common_paths.extend([
            '/usr/bin/clang-format',
            '/usr/local/bin/clang-format',
            '/opt/homebrew/bin/clang-format',  # macOS ARM
            '/usr/local/opt/llvm/bin/clang-format',  # macOS Intel
        ])

    for path_pattern in common_paths:
        # Expand wildcards for Visual Studio path
        if '*' in path_pattern:
            import glob
            for expanded_path in glob.glob(path_pattern):
                if os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK):
                    print(f"clang-format: Found in common location: {expanded_path}")
                    return expanded_path
        else:
            if os.path.isfile(path_pattern) and os.access(path_pattern, os.X_OK):
                print(f"clang-format: Found in common location: {path_pattern}")
                return path_pattern

    # 4. Not found
    print("NOTE: clang-format not found. Please install LLVM or set custom path in config")
    return None

def do_format(text):
    """Format code using clang-format (called by cuda_fmt)."""

    # Load config
    config = load_config()

    # Find executable
    clang_format_cmd = find_clang_format_executable(config)

    # Guard clause: clang-format not found
    if not clang_format_cmd:
        print('ERROR: clang-format executable not found')
        return None

    # Guard clause: empty text
    if not text or not text.strip():
        print('NOTE: Empty document, nothing to format')
        return text

    # Get current lexer
    lexer = ct.ed.get_prop(ct.PROP_LEXER_FILE, '')

    # Guard clause: unsupported lexer
    if lexer not in SUPPORTED_LEXERS:
        print(f'ERROR: Unsupported lexer: {lexer}')
        print(f'Supported lexers: {", ".join(sorted(SUPPORTED_LEXERS.keys()))}')
        return None

    # Build command
    cmd = [clang_format_cmd]
    
    # Add assume-filename to help clang-format find .clang-format in the correct directory
    current_file = ct.ed.get_filename()
    if current_file:
        cmd.extend(['--assume-filename', current_file])

    # Check if .clang-format file should be used
    use_config_file = config.get('use_clang_format_file', True)
    
    if not use_config_file:
        # Use inline style
        style = config.get('style', 'LLVM')
        cmd.append(f'-style={style}')
        print(f"clang-format: Using inline style: {style}")
    else:
        # clang-format will auto-search for .clang-format in parent directories
        print("clang-format: Using .clang-format file (if found) or fallback style")

    # Get timeout
    timeout = config.get('timeout_seconds', 10)

    print(f"clang-format: Command: {' '.join(cmd)}")
    print(f"clang-format: Formatting with lexer: {lexer}")

    # Execute clang-format
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=_get_hidden_startupinfo()
        )

        stdout, stderr = process.communicate(input=text, timeout=timeout)

        # Guard clause: formatting failed
        if process.returncode != 0:
            error_msg = stderr.strip() if stderr else 'Unknown error'
            print(f'ERROR: clang-format failed: {error_msg}')
            return None

        # Guard clause: empty output (shouldn't happen but defensive)
        if not stdout:
            print('ERROR: clang-format returned empty output')
            return None

        # Return formatted text
        # cuda_fmt will automatically preserve line states using difflib
        return stdout

    except subprocess.TimeoutExpired:
        print(f'ERROR: clang-format timed out (>{timeout}s)')
        return None

    except FileNotFoundError:
        print('ERROR: clang-format executable not found')
        return None

    except Exception as e:
        print(f'ERROR: clang-format execution failed: {e}')
        return None


class Command:
    """Command class for CudaText plugin system."""

    def config(self):
        """Open configuration file in editor."""

        config_path = get_config_path()

        # Guard clause: cannot determine config path
        if config_path is None:
            ct.msg_box('Cannot determine config path', ct.MB_OK | ct.MB_ICONERROR)
            return

        # Create config if doesn't exist
        if not os.path.exists(config_path):
            load_config()  # This will create the default config

        # Open in editor
        ct.file_open(config_path)

    def create_clang_format(self):
        """Create .clang-format file in the directory of the current file."""

        # Get current file path
        current_file = ct.ed.get_filename()

        # Guard clause: unsaved file (no directory to create .clang-format in)
        if not current_file:
            ct.msg_box(
                'Cannot create .clang-format:\n\n'
                'The current file has not been saved yet.\n'
                'Please save the file first or open an existing file to determine its directory.',
                ct.MB_OK | ct.MB_ICONWARNING
            )
            return

        # Get directory and path
        file_dir = os.path.dirname(current_file)
        clang_format_path = os.path.join(file_dir, '.clang-format')

        # Guard clause: already exists
        if os.path.exists(clang_format_path):
            # Open in editor
            ct.file_open(clang_format_path)
            ct.ed.set_prop(ct.PROP_LEXER_FILE, 'YAML')
            return

        # Get style from config
        config = load_config()
        base_style = config.get('style', 'LLVM')

        # Create file with YAML format
        clang_format_content = f"""# clang-format configuration file
# Documentation: https://clang.llvm.org/docs/ClangFormatStyleOptions.html

BasedOnStyle: {base_style}

# Indentation
IndentWidth: 4
UseTab: Never

# Line length
ColumnLimit: 100

# Braces
BreakBeforeBraces: Attach

# Spacing
SpaceAfterCStyleCast: false
SpaceBeforeParens: ControlStatements

# Other options
AlignConsecutiveAssignments: false
AllowShortFunctionsOnASingleLine: Empty
"""

        # Create file
        try:
            with open(clang_format_path, 'w', encoding='utf-8') as f:
                f.write(clang_format_content)

            print(f"clang-format: Created .clang-format: {clang_format_path}")

            # Open in editor
            ct.file_open(clang_format_path)
            ct.ed.set_prop(ct.PROP_LEXER_FILE, 'YAML')

        except Exception as e:
            print(f"NOTE: Cannot create .clang-format: {e}")

    def help(self):
        """Display plugin help with version info."""
        global _VERSION_PROCESS, _CLANG_FORMAT_VERSION_CACHE

        # Start process on first help() call if not started yet
        if _VERSION_PROCESS is None and _CLANG_FORMAT_VERSION_CACHE is None:
            _start_version_cache()

        # Check if background version process finished
        if _VERSION_PROCESS is not None and _CLANG_FORMAT_VERSION_CACHE is None:
            # Process was started, check if finished
            if _VERSION_PROCESS.poll() is not None:
                # Process finished, get result
                try:
                    stdout, stderr = _VERSION_PROCESS.communicate(timeout=0.1)
                    if _VERSION_PROCESS.returncode == 0:
                        version = stdout.strip()
                        _CLANG_FORMAT_VERSION_CACHE = f"INSTALLED VERSION:\n{version}\n\n"
                        print(f"clang-format: Cached version {version}")
                except Exception:
                    pass
                _VERSION_PROCESS = None
            else:
                # Process still running, wait for it
                print("clang-format: Waiting for version check to complete...")
                try:
                    stdout, stderr = _VERSION_PROCESS.communicate(timeout=3)
                    if _VERSION_PROCESS.returncode == 0:
                        version = stdout.strip()
                        _CLANG_FORMAT_VERSION_CACHE = f"INSTALLED VERSION:\n{version}\n\n"
                        print(f"clang-format: Cached version {version}")
                except Exception:
                    pass
                _VERSION_PROCESS = None

        # Use cached version (if available)
        version_info = _CLANG_FORMAT_VERSION_CACHE or ""

        # Page 1: Features and basic info
        result = ct.msg_box(
            "clang-format Formatter for CudaText - Page 1/2\n\n"
            f"{version_info}"
            "FEATURES:\n"
            "- Auto-detection (PATH, LLVM, or Visual Studio)\n"
            "- Support for C, C++, C#, Java, Objective-C, JavaScript, TypeScript, Protobuf\n"
            "- Predefined styles (LLVM, Google, Chromium, Mozilla, WebKit, Microsoft, GNU)\n"
            "- Project .clang-format support\n"
            "- Line state preservation (only modified lines marked)\n"
            "- Multi-platform (Windows, Linux, macOS)\n\n"
            "SUPPORTED LANGUAGES:\n"
            "C, C++, C#, Java, Objective-C, Objective-C++,\n"
            "JavaScript, TypeScript, Protocol Buffers (.proto)\n\n"
            "_________________________________________________\n"
            "[Click OK for configuration & installation info]",
            ct.MB_OKCANCEL | ct.MB_ICONINFO
        )

        # Page 2: Configuration and installation (only if user clicked OK)
        if result == ct.ID_OK:
            ct.msg_box(
                "clang-format Formatter for CudaText - Page 2/2\n\n"
                "CONFIGURATION:\n"
                "Access via: Options > Settings-plugins > clang > Config\n"
                "- clang_format_path: Custom path to clang-format executable\n"
                "- use_clang_format_file: Use project .clang-format (default: true)\n"
                "- style: Predefined style when no .clang-format found\n"
                "- timeout_seconds: Subprocess timeout (default: 10)\n\n"
                "PROJECT CONFIG (recommended):\n"
                "Create .clang-format in your project root with your preferred options.\n"
                "Plugin will automatically use it when use_clang_format_file=true\n\n"
                "INSTALLATION METHODS:\n"
                "1. LLVM (recommended):\n"
                "   Download from: https://releases.llvm.org/\n"
                "   clang-format is included in LLVM distribution\n"
                "2. Package managers:\n"
                "   - Linux: apt install clang-format / yum install clang-tools-extra\n"
                "   - macOS: brew install clang-format\n"
                "   - Windows: winget install LLVM.LLVM\n"
                "3. Visual Studio:\n"
                "   clang-format is bundled with Visual Studio 2017+\n"
                "4. Portable mode:\n"
                "   Download clang-format binary -> place in CudaText/tools/Clang/\n"
                "5. Custom path:\n"
                "   Set clang_format_path in config\n\n"
                "USAGE:\n"
                "- Plugins > CudaFormatter > Formatter (menu)\n"
                "- Hotkey (optional): Install 'Configure_Hotkeys' plugin,\n"
                "  then search for 'CudaFormatter: Formatter (menu)'\n\n"
                "DOCUMENTATION:\n"
                "https://clang.llvm.org/docs/ClangFormat.html\n"
                "https://clang.llvm.org/docs/ClangFormatStyleOptions.html",
                ct.MB_OK | ct.MB_ICONINFO
            )
