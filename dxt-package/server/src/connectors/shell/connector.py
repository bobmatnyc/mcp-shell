"""Shell Connector for MCP Gateway.

Provides secure system command execution with Python 3.11+ features:
- Structured concurrency with TaskGroups for parallel execution  
- Exception groups for comprehensive error handling
- Modern type hints and validation
- Security scanning and input validation
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Final

from pydantic import BaseModel, Field, validator

from core.base_connector import BaseConnector
from core.models import (
    ToolContent, ToolDefinition, ToolResult,
    PromptDefinition, PromptResult
)
from core.resource_models import ResourceDefinition, ResourceResult
from templates.shell_templates import ShellTemplates

# Constants following Python 3.11+ best practices
DEFAULT_TIMEOUT: Final[int] = 30
MAX_TIMEOUT: Final[int] = 300  # 5 minutes maximum
DEFAULT_MAX_OUTPUT: Final[int] = 10000
MAX_OUTPUT_LENGTH: Final[int] = 100000

# Security: Dangerous command patterns to block
DANGEROUS_PATTERNS: Final[list[str]] = [
    "rm -rf", "sudo", "su -", "chmod 777", "mkfs", "dd if=", ":(){ :|:& };:",
    "wget http", "curl http", "nc -", "netcat", "/dev/sda", "/dev/hda"
]


class CommandRequest(BaseModel):
    """Pydantic model for shell command requests."""
    
    command: str = Field(..., min_length=1, max_length=1000, description="Shell command to execute")
    working_directory: str | None = Field(default=None, description="Working directory for command")
    timeout: int = Field(default=DEFAULT_TIMEOUT, ge=1, le=MAX_TIMEOUT, description="Command timeout")
    
    @validator('command')
    def validate_command_security(cls, v: str) -> str:
        """Validate command for security issues."""
        if not v.strip():
            raise ValueError("Command cannot be empty")
            
        # Check for dangerous patterns
        command_lower = v.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in command_lower:
                raise ValueError(f"Command contains potentially dangerous pattern: {pattern}")
        
        return v.strip()


class DirectoryListRequest(BaseModel):
    """Pydantic model for directory listing requests."""
    
    path: str = Field(default=".", description="Directory path to list")
    show_hidden: bool = Field(default=False, description="Show hidden files")
    detailed: bool = Field(default=False, description="Show detailed file information")
    
    @validator('path')
    def validate_path(cls, v: str) -> str:
        """Validate directory path."""
        if not v or '..' in v:
            raise ValueError("Invalid path")
        return v


class ShellConnector(BaseConnector):
    """Shell connector for executing system commands with Python 3.11+ features.
    
    Features:
        - Secure command validation with Pydantic
        - Structured concurrency with TaskGroups
        - Exception groups for comprehensive error handling
        - Modern type hints and async patterns
    """
    
    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        """Initialize shell connector with modern Python patterns."""
        super().__init__(name, config)
        self.allowed_commands = self.config.get('allowed_commands', [])
        self.working_directory = self.config.get('working_directory', os.getcwd())
        self.timeout = self.config.get('timeout', DEFAULT_TIMEOUT)
        self.max_output_length = self.config.get('max_output_length', DEFAULT_MAX_OUTPUT)
    
    async def execute_parallel_commands(
        self, 
        commands: list[str], 
        timeout: int = DEFAULT_TIMEOUT
    ) -> list[dict[str, Any]]:
        """Execute multiple commands in parallel using Python 3.11 TaskGroups.
        
        Args:
            commands: List of shell commands to execute
            timeout: Maximum execution time for each command
            
        Returns:
            List of execution results
            
        Raises:
            ExceptionGroup: If any commands fail (Python 3.11+ feature)
        """
        results: list[dict[str, Any]] = []
        
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self._execute_single_command(cmd, timeout))
                    for cmd in commands
                ]
            
            # Collect results from completed tasks
            results = [task.result() for task in tasks]
            
        except* subprocess.CalledProcessError as eg:
            # Handle command execution errors using exception groups
            self.logger.error("Command execution errors: %s", [str(e) for e in eg.exceptions])
            raise
        except* asyncio.TimeoutError as eg:
            # Handle timeout errors
            self.logger.error("Command timeout errors: %s", [str(e) for e in eg.exceptions])
            raise
            
        return results
    
    async def _execute_single_command(
        self, 
        command: str, 
        timeout: int = DEFAULT_TIMEOUT
    ) -> dict[str, Any]:
        """Execute a single command asynchronously.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time
            
        Returns:
            Dictionary with execution results
        """
        # Validate command using Pydantic
        request = CommandRequest(command=command, timeout=timeout)
        
        try:
            process = await asyncio.create_subprocess_shell(
                request.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_directory
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=request.timeout
            )
            
            return {
                "command": request.command,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace')[:self.max_output_length],
                "stderr": stderr.decode('utf-8', errors='replace')[:self.max_output_length],
                "success": process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            self.logger.warning("Command timed out: %s", command)
            raise
        except Exception as e:
            self.logger.error("Command execution failed: %s", e)
            raise
        
    def get_tools(self) -> List[ToolDefinition]:
        """Define shell tools using optimized templates"""
        return [
            ToolDefinition(**ShellTemplates.get_tool_definition("execute", "execute_command")),
            ToolDefinition(**ShellTemplates.get_tool_definition("list_dir", "list_directory")),
            ToolDefinition(**ShellTemplates.get_tool_definition("system_info", "get_system_info"))
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute shell tools"""
        
        if tool_name == "execute_command":
            return await self._execute_command(arguments)
        elif tool_name == "list_directory":
            return await self._list_directory(arguments)
        elif tool_name == "get_system_info":
            return await self._get_system_info(arguments)
        else:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Unknown tool: {tool_name}")],
                is_error=True,
                error_message=f"Tool '{tool_name}' not found"
            )
    
    async def _execute_command(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a shell command"""
        command = arguments.get("command", "").strip()
        working_dir = arguments.get("working_dir", self.working_directory)
        timeout = min(arguments.get("timeout", self.timeout), 60)  # Max 60 seconds
        
        if not command:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Error: {ShellTemplates.ERRORS['no_command']}")],
                is_error=True,
                error_message="Command is required"
            )
        
        # Security check using template
        is_safe, error_msg = ShellTemplates.check_security(command)
        if not is_safe:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Error: {error_msg}")],
                is_error=True,
                error_message="Dangerous command blocked"
            )
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    content=[ToolContent(type="text", text=f"Error: {ShellTemplates.ERRORS['timeout']} after {timeout} seconds")],
                    is_error=True,
                    error_message="Command timeout"
                )
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Limit output length
            if len(stdout_text) > self.max_output_length:
                stdout_text = stdout_text[:self.max_output_length] + "\n... (output truncated)"
            if len(stderr_text) > self.max_output_length:
                stderr_text = stderr_text[:self.max_output_length] + "\n... (output truncated)"
            
            # Format result using template
            result_text = ShellTemplates.format_command_result(
                command, working_dir, process.returncode, stdout_text, stderr_text
            )
            
            return ToolResult(
                content=[ToolContent(type="text", text=result_text)],
                is_error=(process.returncode != 0)
            )
            
        except Exception as e:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Error: {ShellTemplates.ERRORS['execution_error']}: {str(e)}")],
                is_error=True,
                error_message=str(e)
            )
    
    async def _list_directory(self, arguments: Dict[str, Any]) -> ToolResult:
        """List directory contents"""
        path = arguments.get("path", ".")
        show_hidden = arguments.get("show_hidden", False)
        
        try:
            # Expand path
            expanded_path = os.path.expanduser(path)
            abs_path = os.path.abspath(expanded_path)
            
            if not os.path.exists(abs_path):
                return ToolResult(
                    content=[ToolContent(type="text", text=f"Error: {ShellTemplates.ERRORS['not_found']}: {abs_path}")],
                    is_error=True,
                    error_message=ShellTemplates.ERRORS['not_found']
                )
            
            if not os.path.isdir(abs_path):
                return ToolResult(
                    content=[ToolContent(type="text", text=f"Error: {ShellTemplates.ERRORS['not_dir']}: {abs_path}")],
                    is_error=True,
                    error_message=ShellTemplates.ERRORS['not_dir']
                )
            
            # List contents
            items = []
            for item in sorted(os.listdir(abs_path)):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(abs_path, item)
                item_type = "DIR" if os.path.isdir(item_path) else "FILE"
                
                try:
                    size = os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M:%S")
                    items.append(f"{item_type:4} {size:>10} {modified} {item}")
                except (OSError, PermissionError):
                    items.append(f"{item_type:4} {'N/A':>10} {'N/A':>19} {item}")
            
            result = f"Directory: {abs_path}\n"
            result += f"{'TYPE':4} {'SIZE':>10} {'MODIFIED':>19} NAME\n"
            result += "-" * 60 + "\n"
            result += "\n".join(items) if items else "Directory is empty"
            
            return ToolResult(
                content=[ToolContent(type="text", text=result)]
            )
            
        except Exception as e:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Error listing directory: {str(e)}")],
                is_error=True,
                error_message=str(e)
            )
    
    async def _get_system_info(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get system information"""
        try:
            import platform
            
            info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "current_directory": os.getcwd(),
                "user": os.environ.get("USER", "unknown"),
                "shell": os.environ.get("SHELL", "unknown")
            }
            
            result = "=== System Information ===\n"
            for key, value in info.items():
                result += f"{key.title().replace('_', ' ')}: {value}\n"
            
            return ToolResult(
                content=[ToolContent(type="text", text=result)]
            )
            
        except Exception as e:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Error getting system info: {str(e)}")],
                is_error=True,
                error_message=str(e)
            )
    
    def get_resources(self) -> List[ResourceDefinition]:
        """Define shell resources"""
        return [
            ResourceDefinition(
                uri="shell://env",
                name="Environment Variables",
                description="Current environment variables",
                mimeType="application/json"
            ),
            ResourceDefinition(
                uri="shell://cwd",
                name="Current Working Directory",
                description="Current working directory information",
                mimeType="application/json"
            )
        ]
    
    async def read_resource(self, uri: str) -> ResourceResult:
        """Read shell resources"""
        
        if uri == "shell://env":
            env_vars = dict(os.environ)
            # Filter out sensitive variables
            sensitive_keys = ['password', 'secret', 'key', 'token', 'auth']
            filtered_env = {
                k: v for k, v in env_vars.items() 
                if not any(sensitive in k.lower() for sensitive in sensitive_keys)
            }
            
            return ResourceResult(
                content=json.dumps(filtered_env, indent=2),
                mimeType="application/json"
            )
        
        elif uri == "shell://cwd":
            cwd_info = {
                "current_directory": os.getcwd(),
                "absolute_path": os.path.abspath("."),
                "exists": os.path.exists("."),
                "is_writable": os.access(".", os.W_OK),
                "parent_directory": os.path.dirname(os.getcwd())
            }
            
            return ResourceResult(
                content=json.dumps(cwd_info, indent=2),
                mimeType="application/json"
            )
        
        else:
            raise ValueError(f"Resource not found: {uri}")
    
    def get_prompts(self) -> List[PromptDefinition]:
        """Define shell prompts"""
        return [
            self._create_prompt_definition(
                name="shell_help",
                description="Get help with shell commands and safety guidelines",
                arguments=[]
            ),
            self._create_prompt_definition(
                name="system_analysis",
                description="Perform basic system analysis",
                arguments=[]
            ),
            self._create_prompt_definition(
                name="user_scripts_guide",
                description="Learn about the user scripts management system",
                arguments=[]
            )
        ]
    
    async def execute_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> PromptResult:
        """Execute shell prompts"""
        
        if prompt_name == "shell_help":
            content = ShellTemplates.get_shell_help()
            
            return PromptResult(
                content=content,
                metadata={"connector": self.name, "prompt": prompt_name}
            )
        
        elif prompt_name == "system_analysis":
            content = """System Analysis Steps:
1. get_system_info
2. list_directory
3. Check shell://env resource
4. execute_command "ps aux | head -20"
5. execute_command "df -h"
6. execute_command "free -h" (Linux) or "vm_stat" (macOS)

Provides system overview."""
            
            return PromptResult(
                content=content,
                metadata={"connector": self.name, "prompt": prompt_name}
            )
        
        elif prompt_name == "user_scripts_guide":
            content = ShellTemplates.get_user_scripts_guide()
            
            return PromptResult(
                content=content,
                metadata={"connector": self.name, "prompt": prompt_name}
            )
        
        else:
            return await super().execute_prompt(prompt_name, arguments)