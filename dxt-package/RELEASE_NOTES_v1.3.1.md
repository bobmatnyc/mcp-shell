# MCP Shell v1.3.1 - Desktop Extension Release 🚀

## 📦 New: DXT Package Distribution

**MCP Shell** is now available as a Desktop Extension (DXT) package for **one-click installation** in Claude Desktop!

### 🎯 What is MCP Shell?

MCP Shell transforms your mcp-desktop-gateway into a user-friendly Desktop Extension that provides universal shell connectivity for Claude Desktop. No more complex setup - just download and double-click to install.

## ✨ Key Features

### 🖥️ **Shell Execution** 
- Execute terminal commands directly from Claude
- Cross-platform support (macOS, Windows)
- Safe, controlled command execution

### 🍎 **AppleScript Automation** (macOS)
- Automate macOS applications
- Control Finder, Safari, and system functions
- Native macOS integration

### 🌐 **Chrome Browser Control**
- Automate web browser interactions
- Take screenshots and extract content
- Control tabs and navigation

### 📁 **File System Operations**
- Read, write, and manage files
- Directory navigation and manipulation
- Secure file access controls

## 📋 Installation

### Quick Install (Recommended)
1. **Download**: `mcp-shell-1.3.1.dxt` (8.6MB)
2. **Install**: Double-click the `.dxt` file
3. **Ready**: Restart Claude Desktop if prompted

### Manual Install
1. Open Claude Desktop → Settings → Extensions
2. Click "Install Extension"
3. Select `mcp-shell-1.3.1.dxt`
4. Follow installation prompts

## 🔧 Technical Details

- **Package Size**: 8.6MB compressed, 21.6MB unpacked
- **Files Included**: 1,611 files with all dependencies bundled
- **Python Version**: 3.11+ required
- **MCP Version**: 1.11.0
- **DXT Specification**: v0.1.0

## 🎉 What's New in This Release

### 🆕 DXT Package Format
- **First DXT release** of mcp-desktop-gateway
- Renamed to "MCP Shell" for better user recognition
- Complete dependency bundling for offline installation
- Official DXT specification compliance

### 🔄 Enhanced Distribution
- No more complex Python setup required
- One-click installation experience
- Automatic dependency management
- Cross-platform compatibility

### 📚 Improved Documentation
- Installation guide included
- Usage examples and best practices
- Troubleshooting information

## 🛠️ Requirements

- **Claude Desktop** (latest version recommended)
- **Python 3.11+** (bundled in package)
- **Operating System**: 
  - macOS 11+ (full feature support)
  - Windows 10+ (core features)

## 🔒 Security & Permissions

This extension requires the following permissions:
- `shell:execute` - Execute shell commands
- `files:read` - Read file system
- `files:write` - Write to file system  
- `network:local` - Local network access

**⚠️ Security Note**: Only install from trusted sources. This extension can execute system commands.

## 📖 Usage Examples

After installation, you can ask Claude to:

```
"Run `ls -la` to show directory contents"
"Open Finder and navigate to Downloads folder"  
"Take a screenshot of the current Chrome tab"
"Create a new text file with project notes"
"Execute a Python script in the current directory"
```

## 🔗 Links & Resources

- **Source Code**: [mcp-shell](https://github.com/bobmatnyc/mcp-shell)
- **Installation Guide**: `MCP_SHELL_INSTALL_GUIDE.md`
- **Issues & Support**: [GitHub Issues](https://github.com/bobmatnyc/mcp-shell/issues)
- **MCP Documentation**: [Model Context Protocol](https://mcp.so/)
- **DXT Specification**: [Desktop Extensions](https://github.com/anthropics/dxt)

## 🎯 Next Steps

1. **Download** the DXT package
2. **Install** in Claude Desktop
3. **Try** the example commands above
4. **Explore** automation possibilities
5. **Share** feedback and use cases

## 🙏 Credits

Built with:
- [MCP (Model Context Protocol)](https://mcp.so/) by Anthropic
- [DXT (Desktop Extensions)](https://github.com/anthropics/dxt) toolchain
- Python ecosystem libraries

---

**Happy Automating! 🤖✨**

*This is the first DXT package release of mcp-desktop-gateway. More extensions and features coming soon!*