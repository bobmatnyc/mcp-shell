# MCP Shell 🚀

**Universal shell connectivity for Claude Desktop via Model Context Protocol (MCP)**

MCP Shell is a Desktop Extension (DXT) that provides seamless shell command execution, AppleScript automation, Chrome browser control, and file system operations directly from Claude Desktop.

## 🎯 Quick Start

### 📦 One-Click Installation (Recommended)

1. **Download**: [mcp-shell-1.3.1.dxt](https://github.com/bobmatnyc/mcp-shell/releases/latest) (8.6MB)
2. **Install**: Double-click the `.dxt` file 
3. **Ready**: Restart Claude Desktop if prompted

### 🛠️ Manual Installation

```bash
# Download the latest release
curl -L -o mcp-shell.dxt https://github.com/bobmatnyc/mcp-shell/releases/latest/download/mcp-shell-1.3.1.dxt

# Install in Claude Desktop
# Double-click mcp-shell.dxt or use Claude Desktop → Settings → Extensions
```

## ✨ Features

### 🖥️ **Shell Execution**
Execute terminal commands directly from Claude:
```
"Run `ls -la` to show directory contents"
"Execute `python my_script.py` with error handling"
"Check system status with `top -l 1`"
```

### 🍎 **AppleScript Automation** (macOS)
Automate macOS applications and system functions:
```
"Open Finder and navigate to Downloads folder"
"Take a screenshot and save to Desktop"
"Control iTunes/Music app playback"
```

### 🌐 **Chrome Browser Control**
Automate web browser interactions:
```
"Take a screenshot of the current Chrome tab"
"Extract text content from the active webpage"
"Navigate to a specific URL and capture data"
```

### 📁 **File System Operations**
Secure file and directory management:
```
"Create a new file with specific content"
"Read and analyze log files"
"Organize files by date or type"
```

## 🔧 Technical Details

- **Package Size**: 8.6MB compressed, 21.6MB unpacked
- **Dependencies**: All bundled (no external setup required)
- **Python Version**: 3.11+ (included in package)
- **MCP Version**: 1.11.0+
- **Platforms**: macOS 11+, Windows 10+

## 🏗️ Development Setup

### Prerequisites
- Python 3.11+
- Node.js 16+ (for DXT building)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/bobmatnyc/mcp-shell.git
cd mcp-shell

# Install Python dependencies
pip install -r requirements.txt

# Install DXT toolchain
npm install -g @anthropic-ai/dxt

# Run in development mode
python run_mcp_gateway.py
```

### Building DXT Package
```bash
# Build the DXT package
cd dxt-package
dxt pack

# Output: mcp-shell-1.3.1.dxt
```

## 📖 Usage Examples

After installation, you can ask Claude to perform various automation tasks:

### Shell Operations
```
"Show me the current directory contents"
"Check disk usage with df -h"
"Find all Python files in this project"
"Run the test suite and show results"
```

### File Management
```
"Create a backup of the config directory"
"Find and list all large files over 100MB"
"Organize downloads folder by file type"
"Search for files containing specific text"
```

### System Automation (macOS)
```
"Open Terminal and run a command"
"Take a screenshot of the entire screen"
"Get system information and current processes"
"Control window management and app switching"
```

### Web Automation
```
"Take a screenshot of the current webpage"
"Extract all links from the active Chrome tab"
"Navigate to a URL and capture the page title"
"Monitor a webpage for changes"
```

## 🔒 Security & Permissions

MCP Shell requires the following permissions:
- **Shell Execution**: Execute terminal commands
- **File System**: Read and write files
- **Network**: Local network access for MCP communication
- **System**: macOS AppleScript access (macOS only)

**⚠️ Security Note**: Only install from trusted sources. This extension can execute system commands with your user permissions.

## 🗂️ Project Structure

```
mcp-shell/
├── src/                    # Core source code
│   ├── connectors/        # Individual connector modules
│   ├── core/              # Core framework and utilities
│   ├── templates/         # Prompt templates
│   └── mcp_gateway.py     # Main MCP server
├── config/                # Configuration files
├── dxt-package/          # DXT package build
├── tests/                # Test suite
├── run_mcp_gateway.py    # Entry point
├── requirements.txt      # Python dependencies
└── pyproject.toml       # Project configuration
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific connector tests
python -m pytest tests/unit/connectors/shell/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📋 Requirements

- **Claude Desktop** (latest version)
- **Python 3.11+** (bundled in DXT package)
- **Operating System**:
  - macOS 11+ (full feature support)
  - Windows 10+ (core features)

## 🔗 Links & Resources

- **Releases**: [GitHub Releases](https://github.com/bobmatnyc/mcp-shell/releases)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/bobmatnyc/mcp-shell/issues)
- **Documentation**: [MCP Protocol](https://mcp.so/)
- **DXT Specification**: [Desktop Extensions](https://github.com/anthropics/dxt)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Model Context Protocol and DXT specification
- [Claude Desktop](https://claude.ai) for the MCP integration
- The open-source community for the foundational libraries

## 🚀 What's Next?

- Enhanced Chrome automation capabilities
- Windows-specific automation connectors
- Plugin system for custom connectors
- Advanced file operation templates
- Integration with more desktop applications

---

**Happy Automating! 🤖✨**

*Transform your Claude Desktop into a powerful automation hub with MCP Shell.*