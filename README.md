# CudaText plugin for clang-format code formatter

## 🎯 What is clang-format?

clang-format is a **powerful code formatter** from the LLVM project that enforces consistent coding style. It's the industry-standard formatter for C, C++, and related languages, used by **major projects** including:

- ✅ **C/C++ projects**: LLVM, Chromium, Mozilla, WebKit, Linux Kernel components
- ✅ **Languages**: C, C++, C#, CUDA, Java, Objective-C, JavaScript, TypeScript, GLSL, Protobuf, Verilog
- ✅ **Companies**: Google, Microsoft, Mozilla, Apple, Meta, NVIDIA

Unlike generic formatters, clang-format **understands code semantics** and produces highly readable, consistent output.

## 📦 Installation

### Install the Plugin
1. In CudaText: **Plugins > Addon Manager > Install**
2. Search for "clang" and install

### Install clang-format

#### Option 1: LLVM (Recommended)
- **Download**: https://releases.llvm.org/
- clang-format is included in the LLVM distribution
- Add `bin/` directory to system PATH

#### Option 2: Package Managers
- **Linux**: `sudo apt install clang-format` or `sudo yum install clang-tools-extra`
- **macOS**: `brew install clang-format`
- **Windows**: `winget install LLVM.LLVM`

#### Option 3: Visual Studio
- clang-format is **bundled** with Visual Studio 2017+ (automatically detected)
- Path: `C:\Program Files\Microsoft Visual Studio\<version>\<edition>\VC\Tools\Llvm\bin\`

#### Option 4: Portable Mode (CudaText)
- Download clang-format binary for your platform
- Create folder: `CudaText/tools/Clang/`
- Place `clang-format.exe` (Windows) or `clang-format` (Linux/macOS) in this folder
- Plugin will auto-detect it (no PATH needed)

#### Option 5: Standalone Binary
- Download clang-format binary for your platform
- Add to system PATH or specify custom path in plugin config

## ✨ Plugin Features

### Core Functionality
- 🔌 **Full cuda_fmt integration** - Works seamlessly with CudaText formatter framework
- 🔍 **Smart executable detection** - Auto-finds clang-format in PATH, LLVM, or Visual Studio
- 📁 **Project config support** - Automatically reads `.clang-format` from project
- ⚙️ **Predefined styles** - LLVM, Google, Chromium, Mozilla, WebKit, Microsoft, GNU
- 🌍 **Cross-platform** - Windows, Linux, macOS fully supported

### Advanced Features
- 🎨 **Line state preservation** - Only modified lines marked as changed (thanks to cuda_fmt difflib support)
- ↩️ **Single undo operation** - Format and undo with Ctrl+Z
- 🎯 **15 languages** - C, C++, C#, CUDA, Java, Objective-C/C++, JavaScript (4 variants), TypeScript, GLSL, Protobuf, Verilog
- 🔧 **Flexible configuration** - Use project `.clang-format` or predefined styles
- 📝 **Debug logging** - Shows which executable and command used
- ⚡ **Fast formatting** - Native compiled binary, no runtime dependencies

### User Experience
- 🎯 **KISS principle** - Simple, clean code with minimal complexity
- 📦 **Portable-ready** - Works great with CudaText portable installations
- 🔄 **Live config reload** - Changes to config take effect immediately (no restart needed)

## 🚀 Usage

### Menu Commands
- **Plugins > CudaFormatter > Formatter (menu)** - Format current file
- **Plugins > CudaFormatter > Configure formatter...** - Configure global options (cuda_fmt_clang.json)
- **Plugins > CudaFormatter > Configure formatter (local)...** - Configure local options (.clang-format)
- **Plugins > CudaFormatter > Formatter help...** - Show help

### Hotkey (Optional)
1. Install **Configure_Hotkeys** plugin (via Addon Manager)
2. Search for **"CudaFormatter: Formatter (menu)"**
3. Assign your preferred hotkey (e.g., Shift+Alt+F)

### Configuration

#### Global Config: `settings/cuda_fmt_clang.json`
```json
{
  "clang_format_path": "",
  "timeout_seconds": 10,
  "use_clang_format_file": true,
  "style": "LLVM"
}
```

**Available styles**: `LLVM`, `Google`, `Chromium`, `Mozilla`, `WebKit`, `Microsoft`, `GNU`

#### Project Config: `.clang-format` (Recommended)
Create `.clang-format` in your project root for team consistency:

```yaml
# Based on LLVM style with customizations
BasedOnStyle: LLVM

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

# Alignment
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false

# Functions
AllowShortFunctionsOnASingleLine: Empty
```

**Generate default .clang-format**: Use the plugin's **"Configure formatter (local)"** command to create a template.

## 🎨 Predefined Styles

clang-format comes with industry-standard styles:

| Style | Description | Used By |
|-------|-------------|---------|
| **LLVM** | LLVM project style | LLVM, Rust, Swift |
| **Google** | Google's C++ style guide | Google projects, Android |
| **Chromium** | Chromium project style | Chromium, Chrome |
| **Mozilla** | Mozilla coding style | Firefox, Thunderbird |
| **WebKit** | WebKit style guide | Safari, WebKit |
| **Microsoft** | Microsoft conventions | Visual Studio projects |
| **GNU** | GNU coding standards | GCC, Emacs |

## 📚 Additional Info

- **clang-format project**: https://clang.llvm.org/docs/ClangFormat.html
- **Style options reference**: https://clang.llvm.org/docs/ClangFormatStyleOptions.html
- **Interactive style configurator**: https://clang-format-configurator.site/
- **Author**: Bruno Eduardo, https://github.com/Hanatarou
- **License**: MIT

## 💡 Tips

1. **Team consistency**: Commit `.clang-format` to version control so all team members use the same style
2. **Visual Studio integration**: If you have VS installed, the plugin auto-detects its bundled clang-format
3. **Custom styles**: You can create highly customized `.clang-format` files - see the style options reference
4. **Performance**: clang-format is extremely fast, even on large files (C++ compiled binary)
