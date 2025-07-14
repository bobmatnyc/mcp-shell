"""
Desktop Automation Templates
Template system for optimizing MCP Desktop Gateway prompt efficiency
"""

from .base_templates import BaseTemplates
from .automation_templates import AutomationTemplates
from .browser_templates import BrowserTemplates  
from .shell_templates import ShellTemplates
from .meta_templates import MetaPromptTemplates

__all__ = [
    "BaseTemplates",
    "AutomationTemplates",
    "BrowserTemplates", 
    "ShellTemplates",
    "MetaPromptTemplates"
]