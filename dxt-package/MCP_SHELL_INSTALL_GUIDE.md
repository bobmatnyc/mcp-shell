# MCP Shell - Desktop Extension Installation Guide

## Overview

MCP Shell is a Desktop Extension (DXT) package that provides universal shell connectivity for Claude Desktop. It enables shell command execution, AppleScript automation, Chrome browser control, and file system operations directly from Claude Desktop.

## Features

- **Shell Execution**: Run terminal commands and scripts
- **AppleScript Support**: macOS automation capabilities
- **Chrome Automation**: Browser interaction and control
- **File Operations**: File system management
- **Multi-Platform**: Windows and macOS support

## Installation

### Method 1: Direct Installation (Recommended)
1. Download the `mcp-shell-1.3.1.dxt` file
2. Double-click the `.dxt` file to install in Claude Desktop
3. Restart Claude Desktop if prompted

### Method 2: Manual Installation
1. Open Claude Desktop
2. Go to Settings → Extensions
3. Click "Install Extension" 
4. Select the `mcp-shell-1.3.1.dxt` file
5. Follow the installation prompts

## Verification

After installation, you should be able to:
- Execute shell commands through Claude
- Run AppleScript on macOS
- Interact with Chrome browser
- Perform file operations

## Usage Examples

Once installed, you can ask Claude to:
- "Run `ls -la` to show directory contents"
- "Open Finder and navigate to Downloads" (macOS)
- "Take a screenshot of the current Chrome tab"
- "Create a new file with specific content"

## Requirements

- Claude Desktop (latest version)
- Python 3.11 or higher
- macOS 11+ or Windows 10+

## Source Code

This extension is built from the open-source MCP Desktop Gateway:
- Repository: https://github.com/bobmatnyc/mcp-desktop-gateway
- License: MIT

## Support

For issues or questions:
- GitHub Issues: https://github.com/bobmatnyc/mcp-desktop-gateway/issues
- Documentation: https://github.com/bobmatnyc/mcp-desktop-gateway#readme

## Security Note

This extension requires shell execution permissions. Only install from trusted sources.