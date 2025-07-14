"""
Chrome Extension Connector for MCP Gateway
Enables Claude Desktop to control Chrome web pages through WebSocket communication
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import uuid

from core.base_connector import BaseConnector
from core.models import (
    ToolContent, ToolDefinition, ToolResult,
    PromptDefinition, PromptResult
)
from core.resource_models import ResourceDefinition, ResourceResult

logger = logging.getLogger(__name__)


@dataclass
class PendingCommand:
    """Represents a command waiting for response from Chrome extension"""
    command_id: str
    command_type: str
    data: Dict[str, Any]
    timestamp: datetime
    future: asyncio.Future


class ChromeExtensionConnector(BaseConnector):
    """Connector that enables Chrome extension control from Claude Desktop"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # WebSocket server configuration
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8200)
        self.websocket_path = config.get('websocket_path', '/chrome-extension')
        
        # Connection management
        self.connected_extensions: Set[websockets.WebSocketServerProtocol] = set()
        self.pending_commands: Dict[str, PendingCommand] = {}
        self.server = None
        
        # Statistics
        self.commands_sent = 0
        self.commands_completed = 0
        self.extensions_connected = 0
        
        # Server task will be created in initialize()
        self.server_task = None
    
    async def initialize(self) -> None:
        """Initialize the connector and start WebSocket server"""
        await super().initialize()
        
        # Start WebSocket server with proper error handling
        self.server_task = asyncio.create_task(self._start_websocket_server_with_error_handling())
        logger.info("Chrome extension connector initialization complete")
    
    async def _start_websocket_server_with_error_handling(self):
        """Wrapper to handle WebSocket server startup errors properly"""
        try:
            await self.start_websocket_server()
        except Exception as e:
            logger.error(f"❌ Critical error in WebSocket server task: {e}")
            logger.exception("Full error traceback:")
    
    async def start_websocket_server(self):
        """Start WebSocket server for Chrome extension connections"""
        try:
            logger.info(f"Starting Chrome extension WebSocket server on {self.host}:{self.port}")
            logger.info(f"Using websockets version: {websockets.__version__}")
            logger.info("About to call websockets.serve()...")
            
            # Connection handler with proper signature for websockets 15.0.1
            # The newer websockets library expects only ServerConnection parameter
            async def connection_handler(websocket):
                logger.info(f"WebSocket connection established")
                await self.handle_extension_connection(websocket)
            
            self.server = await websockets.serve(
                connection_handler,
                self.host,
                self.port
            )
            
            logger.info("websockets.serve() completed successfully!")
            logger.info(f"✅ Chrome extension WebSocket server successfully started on ws://{self.host}:{self.port}{self.websocket_path}")
            logger.info(f"WebSocket server object: {self.server}")
            
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"❌ Port {self.port} is already in use. Please check if another service is running on this port.")
            else:
                logger.error(f"❌ OS error starting WebSocket server: {e}")
            logger.exception("Full OS error traceback:")
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
            logger.exception("Full WebSocket server error traceback:")
    
    async def handle_extension_connection(self, websocket):
        """Handle incoming Chrome extension WebSocket connections"""
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔌 Chrome extension connected from {client_info}")
        
        self.connected_extensions.add(websocket)
        self.extensions_connected += 1
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_extension_message(websocket, data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON from extension: {e}")
                except Exception as e:
                    logger.error(f"❌ Error handling extension message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Chrome extension disconnected: {client_info}")
        except Exception as e:
            logger.error(f"❌ Extension connection error: {e}")
        finally:
            self.connected_extensions.discard(websocket)
    
    async def handle_extension_message(self, websocket, data):
        """Handle messages from Chrome extension"""
        message_type = data.get('type')
        
        if message_type == 'chrome_extension_connected':
            logger.info("✅ Chrome extension initialized and ready")
            await self.send_to_extension(websocket, {
                'type': 'connection_acknowledged',
                'data': {
                    'server_time': datetime.now().isoformat(),
                    'connector_name': self.name
                }
            })
            
        elif message_type == 'command_response':
            await self.handle_command_response(data)
            
        elif message_type in ['page_ready', 'tab_activated', 'tab_updated', 'dom_updated']:
            logger.debug(f"📄 Page event: {message_type}")
            # These are informational events from the extension
            
        else:
            logger.warning(f"⚠️ Unknown message type from extension: {message_type}")
    
    async def handle_command_response(self, data):
        """Handle command response from Chrome extension"""
        command_id = data.get('commandId')
        
        if command_id and command_id in self.pending_commands:
            pending_command = self.pending_commands.pop(command_id)
            
            if data.get('success'):
                pending_command.future.set_result(data.get('data'))
                self.commands_completed += 1
                logger.debug(f"✅ Command {command_id} completed successfully")
            else:
                error_msg = data.get('error', 'Unknown error')
                pending_command.future.set_exception(Exception(error_msg))
                logger.error(f"❌ Command {command_id} failed: {error_msg}")
        else:
            logger.warning(f"⚠️ Received response for unknown command: {command_id}")
    
    async def send_to_extension(self, websocket, message):
        """Send message to specific Chrome extension"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"❌ Failed to send message to extension: {e}")
    
    async def broadcast_to_extensions(self, message):
        """Send message to all connected Chrome extensions"""
        if not self.connected_extensions:
            raise Exception("No Chrome extensions connected")
        
        # Send to the first connected extension (could be enhanced to target specific ones)
        extension = next(iter(self.connected_extensions))
        await self.send_to_extension(extension, message)
    
    async def send_command_to_chrome(self, command_type: str, data: Dict[str, Any], timeout: int = 30) -> Any:
        """Send command to Chrome extension and wait for response"""
        if not self.connected_extensions:
            raise Exception("No Chrome extensions connected. Please install and activate the EVA Chrome Controller extension.")
        
        command_id = str(uuid.uuid4())
        
        # Create pending command
        future = asyncio.Future()
        pending_command = PendingCommand(
            command_id=command_id,
            command_type=command_type,
            data=data,
            timestamp=datetime.now(),
            future=future
        )
        
        self.pending_commands[command_id] = pending_command
        self.commands_sent += 1
        
        # Send command to extension
        message = {
            'type': command_type,
            'commandId': command_id,
            'data': data
        }
        
        try:
            await self.broadcast_to_extensions(message)
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            self.pending_commands.pop(command_id, None)
            raise Exception(f"Command {command_type} timed out after {timeout} seconds")
        except Exception as e:
            self.pending_commands.pop(command_id, None)
            raise e
    
    def get_tools(self) -> List[ToolDefinition]:
        """Define available Chrome control tools"""
        return [
            ToolDefinition(
                name="chrome_click",
                description="Click an element on the current Chrome page using CSS selector",
                input_schema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to click (e.g., 'button.submit', '#login-btn', 'a[href*=\"example\"]')"
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["selector"]
                }
            ),
            
            ToolDefinition(
                name="chrome_extract_text",
                description="Extract text content from an element on the current Chrome page",
                input_schema={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to extract text from"
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["selector"]
                }
            ),
            
            ToolDefinition(
                name="chrome_fill_form",
                description="Fill form fields on the current Chrome page",
                input_schema={
                    "type": "object",
                    "properties": {
                        "form_data": {
                            "type": "object",
                            "description": "Object with CSS selectors as keys and values to fill",
                            "additionalProperties": {"type": "string"}
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["form_data"]
                }
            ),
            
            ToolDefinition(
                name="chrome_scroll",
                description="Scroll the current Chrome page",
                input_schema={
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": ["up", "down", "left", "right", "top", "bottom"],
                            "description": "Direction to scroll"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Scroll amount in pixels (default: 500)",
                            "default": 500
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["direction"]
                }
            ),
            
            ToolDefinition(
                name="chrome_navigate",
                description="Navigate to a URL in Chrome",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to"
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["url"]
                }
            ),
            
            ToolDefinition(
                name="chrome_inject_script",
                description="Execute custom JavaScript on the current Chrome page",
                input_schema={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute"
                        },
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    },
                    "required": ["script"]
                }
            ),
            
            ToolDefinition(
                name="chrome_get_page_info",
                description="Get information about the current Chrome page",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tab_id": {
                            "type": "integer",
                            "description": "Optional tab ID. If not provided, uses the active tab"
                        }
                    }
                }
            ),
            
            ToolDefinition(
                name="chrome_create_tab",
                description="Create a new Chrome tab and navigate to a URL",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to open in the new tab"
                        },
                        "active": {
                            "type": "boolean",
                            "description": "Whether to make the new tab active (default: true)",
                            "default": True
                        }
                    },
                    "required": ["url"]
                }
            ),
            
            ToolDefinition(
                name="chrome_extension_status",
                description="Get status of Chrome extension connection and statistics",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a Chrome control tool"""
        try:
            if tool_name == "chrome_extension_status":
                return await self._get_extension_status()
            
            elif tool_name == "chrome_click":
                result = await self.send_command_to_chrome("chrome_click", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Clicked element: {arguments['selector']}")],
                    is_error=False
                )
            
            elif tool_name == "chrome_extract_text":
                result = await self.send_command_to_chrome("chrome_extract_text", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"Extracted text: {result['text']}")],
                    is_error=False
                )
            
            elif tool_name == "chrome_fill_form":
                result = await self.send_command_to_chrome("chrome_fill_form", arguments)
                filled_count = len(result.get('filled', []))
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Filled {filled_count} form fields")],
                    is_error=False
                )
            
            elif tool_name == "chrome_scroll":
                result = await self.send_command_to_chrome("chrome_scroll", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Scrolled {arguments['direction']} by {result.get('amount', 0)} pixels")],
                    is_error=False
                )
            
            elif tool_name == "chrome_navigate":
                result = await self.send_command_to_chrome("chrome_navigate", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Navigated to: {arguments['url']}")],
                    is_error=False
                )
            
            elif tool_name == "chrome_inject_script":
                result = await self.send_command_to_chrome("chrome_inject_script", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Script executed. Result: {json.dumps(result, indent=2)}")],
                    is_error=False
                )
            
            elif tool_name == "chrome_get_page_info":
                result = await self.send_command_to_chrome("chrome_get_page_info", arguments)
                page_info = result.get('page', {})
                tab_info = result.get('tab', {})
                
                info_text = f"""📄 Page Information:
Title: {page_info.get('title', 'Unknown')}
URL: {page_info.get('url', 'Unknown')}
Domain: {page_info.get('domain', 'Unknown')}
Viewport: {page_info.get('viewportWidth', 0)}x{page_info.get('viewportHeight', 0)}
Scroll Position: ({page_info.get('scrollX', 0)}, {page_info.get('scrollY', 0)})
Tab ID: {tab_info.get('id', 'Unknown')}"""
                
                return ToolResult(
                    content=[ToolContent(type="text", text=info_text)],
                    is_error=False
                )
            
            elif tool_name == "chrome_create_tab":
                result = await self.send_command_to_chrome("chrome_create_tab", arguments)
                return ToolResult(
                    content=[ToolContent(type="text", text=f"✅ Created new tab (ID: {result['tabId']}) with URL: {result['url']}")],
                    is_error=False
                )
            
            else:
                return ToolResult(
                    content=[ToolContent(type="text", text=f"❌ Unknown tool: {tool_name}")],
                    is_error=True
                )
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return ToolResult(
                content=[ToolContent(type="text", text=f"❌ Error: {str(e)}")],
                is_error=True
            )
    
    async def _get_extension_status(self) -> ToolResult:
        """Get Chrome extension connection status"""
        status = {
            "connected_extensions": len(self.connected_extensions),
            "commands_sent": self.commands_sent,
            "commands_completed": self.commands_completed,
            "pending_commands": len(self.pending_commands),
            "extensions_connected_total": self.extensions_connected,
            "websocket_server": f"ws://{self.host}:{self.port}{self.websocket_path}"
        }
        
        status_text = f"""🤖 Chrome Extension Status:
Connected Extensions: {status['connected_extensions']}
Commands Sent: {status['commands_sent']}
Commands Completed: {status['commands_completed']}
Pending Commands: {status['pending_commands']}
Total Extensions Connected: {status['extensions_connected_total']}
WebSocket Server: {status['websocket_server']}

Status: {"🟢 Ready" if status['connected_extensions'] > 0 else "🔴 No extensions connected"}"""
        
        return ToolResult(
            content=[ToolContent(type="text", text=status_text)],
            is_error=False
        )
    
    def get_resources(self) -> List[ResourceDefinition]:
        """Define available resources"""
        return [
            ResourceDefinition(
                uri="chrome://status",
                name="Chrome Extension Status",
                description="Real-time status of Chrome extension connections and commands",
                mime_type="application/json"
            )
        ]
    
    async def read_resource(self, uri: str) -> ResourceResult:
        """Read a resource"""
        if uri == "chrome://status":
            status = {
                "connected_extensions": len(self.connected_extensions),
                "commands_sent": self.commands_sent,
                "commands_completed": self.commands_completed,
                "pending_commands": list(self.pending_commands.keys()),
                "server_info": {
                    "host": self.host,
                    "port": self.port,
                    "path": self.websocket_path
                }
            }
            
            return ResourceResult(
                contents=[ToolContent(type="text", text=json.dumps(status, indent=2))]
            )
        
        return ResourceResult(
            contents=[ToolContent(type="text", text="Resource not found")],
            is_error=True
        )
    
    def get_prompts(self) -> List[PromptDefinition]:
        """Define available prompts"""
        return [
            PromptDefinition(
                name="chrome_automation_help",
                description="Get help with Chrome page automation using the extension",
                arguments=[]
            )
        ]
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> PromptResult:
        """Get a prompt"""
        if name == "chrome_automation_help":
            help_text = """🤖 Chrome Extension Automation Help

The EVA Chrome Controller extension enables Claude Desktop to control Chrome web pages. Here's how to use it:

## Available Commands:
- chrome_click(selector) - Click elements using CSS selectors
- chrome_extract_text(selector) - Extract text from page elements  
- chrome_fill_form(form_data) - Fill form fields automatically
- chrome_scroll(direction, amount?) - Scroll the page in any direction
- chrome_navigate(url) - Navigate to a new URL
- chrome_inject_script(script) - Execute custom JavaScript
- chrome_get_page_info() - Get detailed page information
- chrome_create_tab(url) - Open new tabs
- chrome_extension_status() - Check connection status

## CSS Selector Examples:
- #login-button (by ID)
- .submit-btn (by class)
- button[type="submit"] (by attribute)
- form input[name="email"] (nested selectors)
- a[href*="example.com"] (partial match)

## Example Usage:
1. chrome_get_page_info() - See what page you're on
2. chrome_click("#login-button") - Click a login button
3. chrome_fill_form({"#email": "user@example.com", "#password": "secret"}) - Fill login form
4. chrome_extract_text("h1") - Get the page title

Make sure the Chrome extension is installed and active!"""
            
            return PromptResult(
                description="Chrome automation help and examples",
                messages=[ToolContent(type="text", text=help_text)]
            )
        
        return PromptResult(
            description="Prompt not found",
            messages=[ToolContent(type="text", text="Prompt not found")],
            is_error=True
        )