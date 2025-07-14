"""
Chrome Connector for MCP Gateway
Provides Chrome browser automation and chromeless launching capabilities
"""

import logging
import subprocess
import tempfile
import os
import platform
from typing import Dict, List, Any, Optional

from core.base_connector import BaseConnector
from core.models import ToolDefinition
from core.resource_models import ResourceDefinition

logger = logging.getLogger(__name__)


class ChromeConnector(BaseConnector):
    """Chrome browser automation connector."""

    def __init__(self, name: str = "chrome", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.is_macos = platform.system() == 'Darwin'
        self.chrome_path = self._find_chrome_executable()

    def _find_chrome_executable(self) -> str:
        """Find the Chrome executable path based on the platform."""
        if self.is_macos:
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:
            # Linux/Windows paths
            for path in [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/chrome",
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]:
                if os.path.exists(path):
                    return path
        return "google-chrome"  # Fallback to PATH

    def get_tools(self) -> List[ToolDefinition]:
        """Return the tools provided by this connector."""
        return [
            ToolDefinition(
                name="chrome_launch_chromeless",
                description="Launch Chrome in chromeless mode for dashboard viewing. Replaces existing Chrome instances by default.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to open in chromeless mode",
                            "default": "http://localhost:8090"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["kiosk", "app", "fullscreen"],
                            "description": "Launch mode: 'kiosk' (full kiosk), 'app' (chromeless window - default), 'fullscreen' (fullscreen window)",
                            "default": "app"
                        },
                        "single_instance": {
                            "type": "boolean",
                            "description": "Replace existing Chrome instances (default: true)",
                            "default": True
                        },
                        "disable_security": {
                            "type": "boolean",
                            "description": "Disable web security for local development (default: true)",
                            "default": True
                        },
                        "user_data_dir": {
                            "type": "string",
                            "description": "Custom user data directory (optional, uses ~/.chrome_dashboard for single instance)"
                        },
                        "additional_flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional Chrome command line flags"
                        }
                    },
                    "required": []
                }
            ),
            ToolDefinition(
                name="chrome_launch_app",
                description="Launch Chrome in app mode (chromeless window) for a specific URL",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to open as Chrome app"
                        },
                        "window_size": {
                            "type": "string",
                            "description": "Window size (e.g., '1920,1080')",
                            "default": "1920,1080"
                        },
                        "window_position": {
                            "type": "string",
                            "description": "Window position (e.g., '0,0')"
                        }
                    },
                    "required": ["url"]
                }
            ),
            ToolDefinition(
                name="chrome_kill_processes",
                description="Kill all Chrome processes (useful for cleanup)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "force": {
                            "type": "boolean",
                            "description": "Force kill Chrome processes (default: false)",
                            "default": False
                        },
                        "dashboard_only": {
                            "type": "boolean", 
                            "description": "Kill only dashboard Chrome instances (default: false)",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            ToolDefinition(
                name="chrome_list_dashboard_processes",
                description="List Chrome processes running with dashboard user data directory",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    def get_resources(self) -> List[ResourceDefinition]:
        """Return the resources provided by this connector."""
        return [
            ResourceDefinition(
                uri="chrome://running-processes",
                name="Chrome Running Processes",
                description="List of running Chrome processes",
                mimeType="application/json"
            )
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        try:
            if tool_name == "chrome_launch_chromeless":
                return self._launch_chromeless(arguments)
            elif tool_name == "chrome_launch_app":
                return self._launch_app(arguments)
            elif tool_name == "chrome_kill_processes":
                return self._kill_processes(arguments)
            elif tool_name == "chrome_list_dashboard_processes":
                return self._get_dashboard_chrome_processes()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            result = BrowserTemplates.format_result(False, "unknown_tool")
            result["error"] = str(e)
            return result

    def _launch_chromeless(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Launch Chrome in chromeless mode with single instance management."""
        url = arguments.get("url", "http://localhost:8090")
        mode = arguments.get("mode", "app")  # Default to app mode instead of kiosk
        disable_security = arguments.get("disable_security", True)
        user_data_dir = arguments.get("user_data_dir")
        additional_flags = arguments.get("additional_flags", [])
        single_instance = arguments.get("single_instance", True)

        # Check for existing dashboard Chrome processes and terminate them if single_instance is True
        if single_instance:
            existing_processes = self._get_dashboard_chrome_processes()
            if existing_processes.get("count", 0) > 0:
                logger.info(f"Found {existing_processes['count']} existing dashboard Chrome processes, terminating them...")
                # Kill specific dashboard processes
                for pid in existing_processes.get("dashboard_processes", []):
                    try:
                        import signal
                        os.kill(pid, signal.SIGTERM)
                        logger.info(f"Terminated Chrome process PID: {pid}")
                    except ProcessLookupError:
                        logger.info(f"Process PID {pid} already terminated")
                    except Exception as e:
                        logger.warning(f"Failed to terminate process PID {pid}: {e}")
                
                # Small delay to ensure processes are fully terminated
                import time
                time.sleep(1)

        # Use a consistent user data directory for single instance mode
        if not user_data_dir:
            if single_instance:
                # Use a consistent directory name for single instance
                user_data_dir = os.path.expanduser("~/.chrome_dashboard")
                os.makedirs(user_data_dir, exist_ok=True)
            else:
                user_data_dir = tempfile.mkdtemp(prefix="chrome_instance_")

        # Build Chrome command using optimized template
        cmd = BrowserTemplates.get_chrome_command(mode, url, user_data_dir, disable_security)
        cmd[0] = self.chrome_path  # Replace placeholder with actual path
        
        # Add any additional flags
        cmd.extend(additional_flags)
        
        try:
            # Launch Chrome in the background
            logger.info(f"Launching single Chrome instance with command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return {
                "success": True,
                "url": url,
                "mode": mode,
                "pid": process.pid,
                "user_data_dir": user_data_dir,
                "command": ' '.join(cmd),
                "single_instance": single_instance,
                "message": f"Chrome launched in {mode} mode (single instance: {single_instance})"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to launch Chrome: {str(e)}"
            }

    def _launch_app(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Launch Chrome in app mode for a specific URL."""
        url = arguments["url"]
        window_size = arguments.get("window_size", "1920,1080")
        window_position = arguments.get("window_position")
        
        # Create temporary user data directory
        user_data_dir = tempfile.mkdtemp(prefix="chrome_app_")
        
        cmd = [
            self.chrome_path,
            f"--app={url}",
            f"--user-data-dir={user_data_dir}",
            f"--window-size={window_size}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps"
        ]
        
        if window_position:
            cmd.append(f"--window-position={window_position}")
        
        try:
            logger.info(f"Launching Chrome app: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return {
                "success": True,
                "url": url,
                "mode": "app",
                "pid": process.pid,
                "window_size": window_size,
                "window_position": window_position,
                "user_data_dir": user_data_dir
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to launch Chrome app: {str(e)}"
            }

    def _kill_processes(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Kill Chrome processes."""
        force = arguments.get("force", False)
        dashboard_only = arguments.get("dashboard_only", False)
        
        try:
            if dashboard_only:
                # Kill only dashboard Chrome processes
                dashboard_processes = self._get_dashboard_chrome_processes()
                if dashboard_processes.get("count", 0) == 0:
                    return {
                        "success": True,
                        "message": "No dashboard Chrome processes found to terminate",
                        "dashboard_only": True
                    }
                
                terminated_pids = []
                for pid in dashboard_processes.get("dashboard_processes", []):
                    try:
                        import signal
                        if force:
                            os.kill(pid, signal.SIGKILL)
                        else:
                            os.kill(pid, signal.SIGTERM)
                        terminated_pids.append(pid)
                    except ProcessLookupError:
                        pass  # Process already terminated
                    except Exception as e:
                        logger.warning(f"Failed to terminate dashboard process PID {pid}: {e}")
                
                return {
                    "success": True,
                    "message": f"Terminated {len(terminated_pids)} dashboard Chrome processes",
                    "terminated_pids": terminated_pids,
                    "dashboard_only": True,
                    "force": force
                }
            else:
                # Kill all Chrome processes (original behavior)
                if self.is_macos:
                    if force:
                        cmd = ["killall", "-9", "Google Chrome"]
                    else:
                        cmd = ["killall", "Google Chrome"]
                else:
                    if force:
                        cmd = ["pkill", "-9", "-f", "chrome"]
                    else:
                        cmd = ["pkill", "-f", "chrome"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "All Chrome processes terminated",
                        "dashboard_only": False,
                        "force": force
                    }
                elif result.returncode == 1:
                    return {
                        "success": True,
                        "message": "No Chrome processes found to terminate",
                        "dashboard_only": False,
                        "force": force
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to kill Chrome processes: {result.stderr}",
                        "dashboard_only": False,
                        "force": force
                    }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error killing Chrome processes: {str(e)}"
            }

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI."""
        try:
            if uri == "chrome://running-processes":
                return self._get_running_processes()
            else:
                return {"error": f"Unknown resource URI: {uri}"}
                
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {str(e)}")
            result = BrowserTemplates.format_result(False, "unknown_resource")
            result["error"] = str(e)
            return result

    def _get_running_processes(self) -> Dict[str, Any]:
        """Get list of running Chrome processes."""
        try:
            if self.is_macos:
                cmd = ["pgrep", "-f", "Google Chrome"]
            else:
                cmd = ["pgrep", "-f", "chrome"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = [int(pid.strip()) for pid in result.stdout.split() if pid.strip()]
                return {
                    "running_processes": pids,
                    "count": len(pids)
                }
            else:
                return {
                    "running_processes": [],
                    "count": 0
                }
                
        except Exception as e:
            return {"error": f"Failed to get Chrome processes: {str(e)}"}

    def _get_dashboard_chrome_processes(self) -> Dict[str, Any]:
        """Get list of Chrome processes specifically running with our dashboard user data directory."""
        try:
            dashboard_dir = r"\.chrome_dashboard"  # Escape the dot for grep
            
            # Use ps and grep to find processes with our dashboard user data directory
            cmd = ["ps", "aux"]
            ps_result = subprocess.run(cmd, capture_output=True, text=True)
            
            if ps_result.returncode != 0:
                return {"error": "Failed to get process list"}
            
            # Filter for Chrome processes with our dashboard directory
            grep_cmd = ["grep", "-E", f"Google Chrome.*{dashboard_dir}"]
            grep_process = subprocess.Popen(grep_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            grep_output, _ = grep_process.communicate(input=ps_result.stdout)
            
            # Extract PIDs from the grep output
            pids = []
            for line in grep_output.strip().split('\n'):
                if line and 'grep' not in line:  # Exclude the grep process itself
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])  # PID is typically the second column in ps aux
                            pids.append(pid)
                        except ValueError:
                            continue
            
            return {
                "dashboard_processes": pids,
                "count": len(pids)
            }
                
        except Exception as e:
            return {"error": f"Failed to get dashboard Chrome processes: {str(e)}"}