Formatter for CudaFormatter plugin.
It adds support for 15 languages: C, C++, C#, CUDA, Java, Objective-C, JavaScript (4 variants), TypeScript, GLSL, Protocol Buffers, and Verilog.
It uses "clang-format".

'clang-format' must be in your system PATH, LLVM installation, Visual Studio, or in the tools/Clang folder (portable use) inside CudaText directory.

clang-format is a powerful code formatter from the LLVM project that enforces consistent coding style:
https://clang.llvm.org/docs/ClangFormat.html

Installation examples:
- LLVM: Download from https://releases.llvm.org/ (clang-format included)
- Linux: sudo apt install clang-format
- macOS: brew install clang-format
- Windows: winget install LLVM.LLVM
- Visual Studio: bundled with VS 2017+
- Portable: Download clang-format binary and place in tools/Clang folder inside CudaText directory

Access formatting via menu: Plugins > CudaFormatter > Formatter (menu)
Access global configuration via menu: Plugins > CudaFormatter > Configure formatter...
Access local configuration via menu: Plugins > CudaFormatter > Configure formatter (local)...
Access help via menu: Plugins > CudaFormatter > Formatter help...
Hotkey (optional): Install 'Configure_Hotkeys' plugin, then search for "CudaFormatter: Formatter (menu)"

Supported languages (15):
C, C++, C#, CUDA C++, Java, Objective-C, Objective-C++,
JavaScript, JavaScript (ES6), JavaScript (ES6)L, JavaScript Babel,
TypeScript, GLSL, Protocol Buffers (.proto), Verilog HDL

Predefined styles:
LLVM, Google, Chromium, Mozilla, WebKit, Microsoft, GNU

Configuration modes:
1. Project config (recommended): Create .clang-format in your project root
2. Plugin config: Edit settings/cuda_fmt_clang.json

Example plugin config:
{
  "clang_format_path": "",
  "timeout_seconds": 10,
  "use_clang_format_file": true,
  "style": "LLVM"
}

When use_clang_format_file=true (default), clang-format searches for .clang-format in your project.
When false, uses style option from plugin config.

Example .clang-format:
BasedOnStyle: LLVM
IndentWidth: 4
ColumnLimit: 100
BreakBeforeBraces: Attach

Style options reference: https://clang.llvm.org/docs/ClangFormatStyleOptions.html

Author: Bruno Eduardo, https://github.com/Hanatarou

License: MIT
