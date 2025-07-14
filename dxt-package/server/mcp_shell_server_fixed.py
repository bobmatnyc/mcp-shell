#!/usr/bin/env python3
"""
MCP Shell - Standalone MCP Server for Desktop Extension (DXT)

Provides shell execution, file operations, and system automation tools
for Claude Desktop via Model Context Protocol.

Based on the official Anthropic MCP SDK patterns.
"""

import asyncio
import logging
import os
import subprocess
import sys
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-shell")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolRequest,
        ListToolsRequest,
    )
    logger.info("MCP imports successful")
except ImportError as e:
    logger.error(f"Failed to import MCP: {e}")
    sys.exit(1)

class MCPShellServer:
    """Standalone MCP Shell server for Claude Desktop"""
    
    def __init__(self):
        logger.info("Initializing MCP Shell Server...")
        self.server = Server("mcp-shell")
        self.setup_handlers()
        logger.info("MCP Shell Server initialized")
    
    def setup_handlers(self):
        """Set up MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools for Claude Desktop"""
            logger.info("Tools requested - returning tool list")
            
            tools = [
                Tool(
                    name="execute_shell",
                    description="Execute shell commands safely with timeout protection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command to execute"
                            },
                            "working_directory": {
                                "type": "string", 
                                "description": "Working directory for command (optional)",
                                "default": "."
                            }
                        },
                        "required": ["command"]
                    }
                ),
                Tool(
                    name="read_file",
                    description="Read and return the contents of a text file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="write_file", 
                    description="Write content to a file, creating directories if needed",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                Tool(
                    name="list_directory",
                    description="List contents of a directory with file information",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to directory to list",
                                "default": "."
                            }
                        }
                    }
                )
            ]
            
            # Add macOS-specific tools
            if platform.system() == "Darwin":
                tools.append(Tool(
                    name="run_applescript",
                    description="Execute AppleScript commands for macOS automation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "string", 
                                "description": "AppleScript code to execute"
                            }
                        },
                        "required": ["script"]
                    }
                ))
            
            logger.info(f"Returning {len(tools)} tools")
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls from Claude Desktop"""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                if name == "execute_shell":
                    return await self._execute_shell(arguments)
                elif name == "read_file":
                    return await self._read_file(arguments) 
                elif name == "write_file":
                    return await self._write_file(arguments)
                elif name == "list_directory":
                    return await self._list_directory(arguments)
                elif name == "run_applescript" and platform.system() == "Darwin":
                    return await self._run_applescript(arguments)
                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg)
                    return [TextContent(type="text", text=error_msg)]
                    
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]
    
    async def _execute_shell(self, args: Dict[str, Any]) -> List[TextContent]:
        """Execute shell command safely"""
        command = args["command"]
        working_dir = args.get("working_directory", ".")
        
        logger.info(f"Executing command: {command} in {working_dir}")
        
        try:
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return code: {result.returncode}"
            
            return [TextContent(type="text", text=output)]
            
        except subprocess.TimeoutExpired:
            return [TextContent(
                type="text",
                text="Command timed out after 30 seconds"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing command: {str(e)}"
            )]
    
    async def _read_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Read file contents"""
        file_path = args["file_path"]
        
        try:
            path = Path(file_path)
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"File not found: {file_path}"
                )]
            
            content = path.read_text(encoding='utf-8')
            return [TextContent(
                type="text", 
                text=f"Content of {file_path}:\n\n{content}"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error reading file: {str(e)}"
            )]
    
    async def _write_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Write content to file"""
        file_path = args["file_path"] 
        content = args["content"]
        
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return [TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to {file_path}"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error writing file: {str(e)}"
            )]
    
    async def _list_directory(self, args: Dict[str, Any]) -> List[TextContent]:
        """List directory contents"""
        directory_path = args.get("directory_path", ".")
        
        try:
            path = Path(directory_path)
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"Directory not found: {directory_path}"
                )]
            
            if not path.is_dir():
                return [TextContent(
                    type="text", 
                    text=f"Path is not a directory: {directory_path}"
                )]
            
            items = []
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")
            
            content = f"Contents of {directory_path}:\n\n" + "\n".join(items)
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing directory: {str(e)}"
            )]
    
    async def _run_applescript(self, args: Dict[str, Any]) -> List[TextContent]:
        """Execute AppleScript (macOS only)"""
        script = args["script"]
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = ""
            if result.stdout:
                output += f"Output: {result.stdout.strip()}\n"
            if result.stderr:
                output += f"Error: {result.stderr.strip()}\n"
            output += f"Return code: {result.returncode}"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing AppleScript: {str(e)}"
            )]

async def main():
    """Main entry point for MCP Shell server"""
    logger.info("Starting MCP Shell server...")
    
    try:
        shell_server = MCPShellServer()
        logger.info("Server created successfully")
        
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Starting stdio server...")
            await shell_server.server.run(
                read_stream,
                write_stream,
                shell_server.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("MCP Shell Server starting...")
    asyncio.run(main())