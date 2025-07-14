"""
Browser Automation Templates  
Optimized templates for Chrome browser control
"""

from typing import Dict, Any, List


class BrowserTemplates:
    """Templates for browser automation operations"""
    
    # Tool descriptions compressed
    TOOL_DESC = {
        "chromeless": "Launch Chrome in chromeless mode for dashboards",
        "app": "Launch Chrome app mode for specific URL",
        "kill": "Kill Chrome processes",
        "list": "List Chrome dashboard processes"
    }
    
    # Parameter sets compressed
    PARAMS = {
        "launch": {
            "url": {"type": "string", "description": "URL to open", "default": "http://localhost:8090"},
            "mode": {"type": "string", "enum": ["kiosk", "app", "fullscreen"], "description": "Launch mode", "default": "app"},
            "single_instance": {"type": "boolean", "description": "Replace existing instances", "default": True},
            "disable_security": {"type": "boolean", "description": "Disable web security", "default": True}
        },
        "app_launch": {
            "url": {"type": "string", "description": "URL for Chrome app"},
            "window_size": {"type": "string", "description": "Window size", "default": "1920,1080"}
        },
        "kill": {
            "force": {"type": "boolean", "description": "Force kill", "default": False},
            "dashboard_only": {"type": "boolean", "description": "Kill dashboard only", "default": False}
        }
    }
    
    # Chrome flags compressed
    CHROME_FLAGS = {
        "common": [
            "--no-first-run",
            "--no-default-browser-check", 
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate"
        ],
        "security": [
            "--disable-web-security",
            "--allow-running-insecure-content"
        ],
        "performance": [
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows"
        ]
    }
    
    # Success messages
    SUCCESS = {
        "launched": "Chrome launched in {mode} mode",
        "terminated": "Chrome processes terminated",
        "no_processes": "No Chrome processes found"
    }
    
    # Error messages
    ERRORS = {
        "launch_failed": "Failed to launch Chrome",
        "kill_failed": "Failed to kill Chrome processes",
        "unknown_tool": "Unknown tool",
        "unknown_resource": "Unknown resource URI"
    }
    
    @classmethod
    def get_tool_definition(cls, tool_type: str, name: str) -> Dict[str, Any]:
        """Get optimized tool definition"""
        param_map = {
            "chromeless": "launch",
            "app": "app_launch", 
            "kill": "kill",
            "list": {}
        }
        
        schema = {"type": "object", "properties": param_map.get(tool_type, {})}
        if tool_type in ["chromeless", "app"]:
            schema["required"] = ["url"] if tool_type == "app" else []
        
        return {
            "name": name,
            "description": cls.TOOL_DESC[tool_type],
            "input_schema": schema
        }
    
    @classmethod
    def get_chrome_command(cls, mode: str, url: str, user_data_dir: str, 
                          disable_security: bool = True) -> List[str]:
        """Generate optimized Chrome command"""
        cmd = ["chrome"]  # Placeholder for actual path
        
        # Mode flags
        mode_flags = {
            "kiosk": ["--kiosk", url],
            "app": [f"--app={url}"],
            "fullscreen": ["--start-fullscreen", url]
        }
        cmd.extend(mode_flags.get(mode, mode_flags["app"]))
        
        # Add user data dir
        cmd.append(f"--user-data-dir={user_data_dir}")
        
        # Add common flags
        cmd.extend(cls.CHROME_FLAGS["common"])
        
        # Add security flags if requested
        if disable_security:
            cmd.extend(cls.CHROME_FLAGS["security"])
            
        # Add performance flags
        cmd.extend(cls.CHROME_FLAGS["performance"])
        
        return cmd
    
    @classmethod
    def format_result(cls, success: bool, message_key: str, **kwargs) -> Dict[str, Any]:
        """Format standardized result"""
        if success:
            return {
                "success": True,
                "message": cls.SUCCESS[message_key].format(**kwargs)
            }
        else:
            return {
                "success": False,
                "error": cls.ERRORS[message_key]
            }
    
    @classmethod
    def get_browser_help(cls) -> str:
        """Get compressed browser automation help"""
        return f"""Chrome Tools:
{cls.TOOL_DESC['chromeless']} - chrome_launch_chromeless
{cls.TOOL_DESC['app']} - chrome_launch_app
{cls.TOOL_DESC['kill']} - chrome_kill_processes  
{cls.TOOL_DESC['list']} - chrome_list_dashboard_processes

Modes: kiosk (full), app (chromeless window), fullscreen
Features: Single instance, security disabled for dev, process management"""