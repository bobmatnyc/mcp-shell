"""
Shell Command Templates
Optimized templates for shell operations and script management
"""

from typing import Dict, Any, List


class ShellTemplates:
    """Templates for shell command operations"""
    
    # Tool descriptions compressed
    TOOL_DESC = {
        "execute": "Execute shell command safely",
        "list_dir": "List files and directories", 
        "system_info": "Get system information"
    }
    
    # Parameter schemas compressed
    PARAMS = {
        "execute": {
            "command": {"type": "string", "description": "Shell command"},
            "working_dir": {"type": "string", "description": "Working directory (optional)"},
            "timeout": {"type": "number", "description": "Timeout seconds (max 60)"}
        },
        "list_dir": {
            "path": {"type": "string", "description": "Directory path (default: current)"},
            "show_hidden": {"type": "boolean", "description": "Show hidden files"}
        }
    }
    
    # Security patterns (compressed but maintained for safety)
    DANGEROUS_PATTERNS = ['rm -rf', 'sudo rm', 'format', 'del /s', '> /dev/', 'dd if=']
    
    # Common shell operations
    OPERATIONS = {
        "script_write": "Write scripts using: echo 'code' > script.py",
        "file_ops": "File operations: ls, cp, mv, mkdir",
        "system_info": "System info: ps, df, whoami",
        "text_processing": "Text: grep, sed, awk",
        "git_ops": "Git: status, diff, log"
    }
    
    # Error messages compressed
    ERRORS = {
        "no_command": "No command provided",
        "dangerous": "Command contains dangerous operations",
        "timeout": "Command timed out",
        "not_found": "Path not found",
        "not_dir": "Path is not a directory",
        "execution_error": "Error executing command"
    }
    
    # Success formats
    SUCCESS_FORMAT = """Command: {command}
Working Directory: {working_dir}
Exit Code: {exit_code}

{output}"""
    
    @classmethod
    def get_tool_definition(cls, tool_type: str, name: str) -> Dict[str, Any]:
        """Get optimized tool definition"""
        required_map = {
            "execute": ["command"],
            "list_dir": [],
            "system_info": []
        }
        
        return {
            "name": name,
            "description": cls.TOOL_DESC[tool_type],
            "input_schema": {
                "type": "object",
                "properties": cls.PARAMS.get(tool_type, {}),
                "required": required_map.get(tool_type, [])
            }
        }
    
    @classmethod
    def check_security(cls, command: str) -> tuple[bool, str]:
        """Check command security (compressed but thorough)"""
        command_lower = command.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in command_lower:
                return False, cls.ERRORS["dangerous"]
        return True, ""
    
    @classmethod
    def format_command_result(cls, command: str, working_dir: str, 
                            exit_code: int, stdout: str, stderr: str) -> str:
        """Format command execution result"""
        output_parts = []
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if not output_parts:
            output_parts.append("No output")
            
        return cls.SUCCESS_FORMAT.format(
            command=command,
            working_dir=working_dir,
            exit_code=exit_code,
            output="\n".join(output_parts)
        )
    
    @classmethod
    def get_shell_help(cls) -> str:
        """Get compressed shell help"""
        return f"""Shell Tools:
{cls.TOOL_DESC['execute']} - execute_command
{cls.TOOL_DESC['list_dir']} - list_directory
{cls.TOOL_DESC['system_info']} - get_system_info

Primary Uses:
• Script Writing: {cls.OPERATIONS['script_write']}
• {cls.OPERATIONS['file_ops']}
• {cls.OPERATIONS['system_info']}
• {cls.OPERATIONS['text_processing']}

Safety: Dangerous command detection, timeout protection (60s max)

For script execution with visual feedback, use Terminal connector"""
    
    @classmethod
    def get_user_scripts_guide(cls) -> str:
        """Get compressed user scripts guide"""
        return """User Scripts System:
Structure: user-scripts/{python,javascript,shell,applescript}/active/
Management: python user-scripts/manage.py {list,create,archive,restore}
Execution: execute_command('python user-scripts/python/active/script.py')
Templates: Available in templates/ subdirectories
Security: Active scripts .gitignored, validate inputs"""