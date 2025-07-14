"""
Desktop Automation Templates
Optimized templates for AppleScript and system automation
"""

from typing import Dict, Any


class AutomationTemplates:
    """Templates for desktop automation operations"""
    
    # Common tool descriptions compressed
    TOOL_DESC = {
        "script": "Execute AppleScript code",
        "notification": "Display system notification", 
        "apps": "Get running applications",
        "control": "Control app (activate/quit/hide)",
        "clipboard_get": "Get clipboard contents",
        "clipboard_set": "Set clipboard contents"
    }
    
    # Standard parameters compressed
    PARAMS = {
        "script": {
            "script": {"type": "string", "description": "AppleScript code"},
            "timeout": {"type": "number", "description": "Timeout seconds (max 60)"}
        },
        "notification": {
            "title": {"type": "string", "description": "Title"},
            "message": {"type": "string", "description": "Message"},
            "sound": {"type": "string", "description": "Sound (optional)"}
        },
        "control": {
            "app_name": {"type": "string", "description": "App name"},
            "action": {"type": "string", "enum": ["activate", "quit", "hide"], "description": "Action"}
        },
        "text": {
            "text": {"type": "string", "description": "Text content"}
        }
    }
    
    # Security messages compressed
    SECURITY = {
        "warning": "Script contains sensitive operations. Proceeding with caution.",
        "timeout": "Script timed out",
        "dangerous": "Dangerous command blocked"
    }
    
    # Success messages compressed  
    SUCCESS = {
        "executed": "AppleScript executed successfully",
        "app_controlled": "Successfully {action}d {app}",
        "clipboard_set": "Copied to clipboard",
        "no_output": "No output"
    }
    
    # Error messages compressed
    ERRORS = {
        "no_script": "No script provided",
        "no_app": "app_name and action required", 
        "invalid_action": "Unknown action",
        "no_text": "text required",
        "macos_only": "AppleScript only available on macOS",
        "platform_error": "Platform not supported",
        "execution_error": "Error executing AppleScript"
    }
    
    # App connector guides compressed
    APP_GUIDES = {
        "contacts": """CONTACTS (10 tools): Contact management
• Search: contacts_search(query, limit)
• Create: contacts_create_contact(first_name, ...)
• Update/Delete: contacts_update/delete_contact(name)
• Groups: contacts_get_groups, contacts_create_group
• Export: contacts_export_vcard(name, path)""",
        
        "messages": """MESSAGES (10 tools): Text messaging
• Send: messages_send(recipient, message)
• Conversations: messages_get_conversations(limit)
• Search: messages_search(query, limit)
• Files: messages_send_file(recipient, path)""",
        
        "finder": """FINDER (10 tools): File operations
• Navigate: finder_open_folder(path)
• Select: finder_get/select_items(paths)
• Manage: finder_move_to_trash, finder_create_folder
• Info: finder_get_info(path)""",
        
        "terminal": """TERMINAL (10 tools): Command automation
• Execute: terminal_execute_command(command, timeout)
• Tabs: terminal_new_tab(command, title)
• Output: terminal_get_output(lines)"""
    }
    
    @classmethod
    def get_tool_definition(cls, tool_type: str, name: str, params_key: str) -> Dict[str, Any]:
        """Get optimized tool definition"""
        return {
            "name": name,
            "description": cls.TOOL_DESC[tool_type],
            "input_schema": {
                "type": "object",
                "properties": cls.PARAMS[params_key],
                "required": list(cls.PARAMS[params_key].keys()) if params_key != "notification" else ["title", "message"]
            }
        }
    
    @classmethod
    def format_result(cls, success: bool, message_key: str, **kwargs) -> str:
        """Format standardized result message"""
        if success:
            return cls.SUCCESS[message_key].format(**kwargs)
        else:
            return cls.ERRORS[message_key]
    
    @classmethod
    def get_app_guide(cls, app: str) -> str:
        """Get compressed app-specific guide"""
        if app == "all":
            return "\n\n".join(cls.APP_GUIDES.values())
        return cls.APP_GUIDES.get(app, f"Unknown app: {app}")
    
    @classmethod
    def get_automation_help(cls) -> str:
        """Get compressed automation help"""
        return f"""AppleScript Tools:
{cls.TOOL_DESC['script']} - run_applescript
{cls.TOOL_DESC['notification']} - system_notification  
{cls.TOOL_DESC['apps']} - get_running_apps
{cls.TOOL_DESC['control']} - control_app
{cls.TOOL_DESC['clipboard_get']} - get_clipboard
{cls.TOOL_DESC['clipboard_set']} - set_clipboard

App Connectors: 40+ tools across Contacts, Messages, Finder, Terminal
Use 'app_connectors_guide' for details.

Safety: Timeout protection, dangerous operation detection, macOS only"""