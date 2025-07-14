"""
Hello World Connector for MCP Gateway
Demonstrates basic functionality with diagnostics, echo, and test tools
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List

from core.base_connector import BaseConnector
from core.models import (
    ToolContent, ToolDefinition, ToolResult,
    PromptDefinition, PromptResult
)
from core.resource_models import ResourceDefinition, ResourceResult


class HelloWorldConnector(BaseConnector):
    """Hello World connector demonstrating MCP Gateway capabilities"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.start_time = datetime.now()
        self.request_count = 0
        self.last_requests = []
    
    def get_tools(self) -> List[ToolDefinition]:
        """Define available tools"""
        return [
            ToolDefinition(
                name="hello_world",
                description="Greet user with gateway info",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name (optional)"}
                    }
                }
            ),
            ToolDefinition(
                name="gateway_diagnostics",
                description="Get gateway diagnostics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "verbose": {"type": "boolean", "description": "Detailed diagnostics"}
                    }
                }
            ),
            ToolDefinition(
                name="echo",
                description="Echo input with metadata",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo"},
                        "include_metadata": {"type": "boolean", "description": "Include metadata"}
                    },
                    "required": ["message"]
                }
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the requested tool"""
        self.request_count += 1
        self._log_request("tool", tool_name, arguments)
        
        if tool_name == "hello_world":
            user_name = arguments.get("name", "User")
            message = f"""Hello {user_name}! 👋

MCP Gateway - Operational ✅
Connector: {self.name} v{self.version}
Uptime: {self._get_uptime()}
Requests: {self.request_count}"""
            
            return ToolResult(
                content=[ToolContent(type="text", text=message)]
            )
        
        elif tool_name == "gateway_diagnostics":
            verbose = arguments.get("verbose", False)
            diagnostics = self._get_diagnostics(verbose)
            
            return ToolResult(
                content=[ToolContent(type="text", text=diagnostics)]
            )
        
        elif tool_name == "echo":
            message = arguments.get("message", "")
            include_metadata = arguments.get("include_metadata", False)
            
            response = f"Echo: {message}"
            
            if include_metadata:
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "request_number": self.request_count,
                    "message_length": len(message),
                    "connector": self.name,
                    "service": "mcp-gateway"
                }
                response += f"\n\nMetadata:\n{json.dumps(metadata, indent=2)}"
            
            return ToolResult(
                content=[ToolContent(type="text", text=response)]
            )
        
        else:
            return ToolResult(
                content=[ToolContent(type="text", text=f"Unknown tool: {tool_name}")],
                is_error=True,
                error_message=f"Tool '{tool_name}' not found in {self.name}"
            )
    
    def get_resources(self) -> List[ResourceDefinition]:
        """Define available resources"""
        return [
            ResourceDefinition(
                uri="gateway://hello/config",
                name="Hello World Configuration",
                description="Current hello world connector configuration",
                mimeType="application/json"
            ),
            ResourceDefinition(
                uri="gateway://hello/status",
                name="Connector Status",
                description="Hello world connector status and metrics",
                mimeType="application/json"
            ),
            ResourceDefinition(
                uri="gateway://hello/logs",
                name="Activity Logs",
                description="Recent hello world connector activity",
                mimeType="text/plain"
            )
        ]
    
    async def read_resource(self, uri: str) -> ResourceResult:
        """Read the requested resource"""
        self.request_count += 1
        self._log_request("resource", uri, {})
        
        if uri == "gateway://hello/config":
            config = {
                "connector": {
                    "name": self.name,
                    "version": self.version,
                    "type": "hello_world"
                },
                "features": {
                    "tools": ["hello_world", "gateway_diagnostics", "echo"],
                    "resources": ["config", "status", "logs"],
                    "prompts": ["quick_test", "debug_info"]
                },
                "configuration": self.config
            }
            
            return ResourceResult(
                content=json.dumps(config, indent=2),
                mimeType="application/json"
            )
        
        elif uri == "gateway://hello/status":
            status = {
                "status": "operational",
                "connector": self.name,
                "uptime": self._get_uptime(),
                "metrics": {
                    "total_requests": self.request_count,
                    "start_time": self.start_time.isoformat(),
                    "current_time": datetime.now().isoformat()
                }
            }
            
            return ResourceResult(
                content=json.dumps(status, indent=2),
                mimeType="application/json"
            )
        
        elif uri == "gateway://hello/logs":
            logs = f"=== {self.name} Activity Logs ===\n\n"
            logs += f"Connector Started: {self.start_time.isoformat()}\n"
            logs += f"Total Requests: {self.request_count}\n\n"
            
            if self.last_requests:
                logs += "Recent Requests:\n"
                for req in self.last_requests[-10:]:
                    logs += f"  [{req['timestamp']}] {req['type']}: {req['name']} {req['args']}\n"
            else:
                logs += "No requests logged yet.\n"
            
            return ResourceResult(
                content=logs,
                mimeType="text/plain"
            )
        
        else:
            raise ValueError(f"Resource not found: {uri}")
    
    def get_prompts(self) -> List[PromptDefinition]:
        """Define available prompts"""
        return [
            self._create_prompt_definition(
                name="hello_quick_test",
                description="Quick connector test",
                arguments=[]
            ),
            self._create_prompt_definition(
                name="hello_debug_info",
                description="Debug connector info",
                arguments=[]
            )
        ]
    
    async def execute_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> PromptResult:
        """Execute the requested prompt"""
        if prompt_name == "hello_quick_test":
            content = """Test Hello World connector:
1. hello_world tool
2. gateway_diagnostics (verbose=true)
3. echo "MCP Gateway is working!" (include_metadata=true)
4. Read gateway://hello/status
5. Read gateway://hello/logs

Verifies connector functionality."""
            
            return PromptResult(
                content=content,
                metadata={"connector": self.name, "prompt": prompt_name}
            )
        
        elif prompt_name == "hello_debug_info":
            content = """Debug Hello World connector:
1. gateway_diagnostics (verbose=true)
2. Read resources: config, status, logs
3. Test echo tool with timestamp
4. Summarize health

Troubleshooting helper."""
            
            return PromptResult(
                content=content,
                metadata={"connector": self.name, "prompt": prompt_name}
            )
        
        else:
            return await super().execute_prompt(prompt_name, arguments)
    
    def _get_uptime(self) -> str:
        """Calculate and format uptime"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def _get_diagnostics(self, verbose: bool = False) -> str:
        """Generate diagnostics information"""
        diag = f"""=== Gateway Diagnostics ===
Connector: {self.name} v{self.version} ✅
Python: {sys.version.split()[0]} | Platform: {sys.platform}
Uptime: {self._get_uptime()} | Requests: {self.request_count}
Tools: 3 | Resources: 3 | Prompts: 2"""
        
        if verbose:
            import os
            diag += f"""

Detailed: PID {os.getpid()} | CWD {os.getcwd()}
Config: {json.dumps(self.config)}
Recent Requests:"""
            
            if self.last_requests:
                for req in self.last_requests[-5:]:
                    diag += f"\n  - [{req['timestamp']}] {req['type']}: {req['name']}"
            else:
                diag += "\n  - No requests logged yet"
        
        return diag
    
    def _log_request(self, req_type: str, name: str, args: Dict[str, Any]):
        """Log request for activity tracking"""
        request = {
            "timestamp": datetime.now().isoformat(),
            "type": req_type,
            "name": name,
            "args": args
        }
        self.last_requests.append(request)
        
        # Keep only last 100 requests
        if len(self.last_requests) > 100:
            self.last_requests = self.last_requests[-100:]
        
        self.logger.info(f"Request: {req_type}:{name} - Args: {args}")