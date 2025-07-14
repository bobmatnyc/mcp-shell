"""
Base Templates for Cross-Connector Deduplication
Common patterns and utilities shared across all desktop connectors
"""

from typing import Dict, Any


class BaseTemplates:
    """Base templates for common connector patterns"""
    
    # Common error messages
    COMMON_ERRORS = {
        "unknown_tool": "Unknown tool",
        "unknown_prompt": "Unknown prompt", 
        "missing_params": "Missing required parameters",
        "execution_error": "Execution error",
        "not_found": "Not found",
        "timeout": "Operation timed out",
        "platform_error": "Platform not supported"
    }
    
    # Common success messages
    COMMON_SUCCESS = {
        "completed": "Operation completed successfully",
        "created": "Created successfully",
        "updated": "Updated successfully",
        "deleted": "Deleted successfully"
    }
    
    # Common parameter types
    COMMON_PARAMS = {
        "timeout": {"type": "number", "description": "Timeout seconds"},
        "verbose": {"type": "boolean", "description": "Verbose output"},
        "force": {"type": "boolean", "description": "Force operation"},
        "confirm": {"type": "boolean", "description": "Confirm action"}
    }
    
    # Standard tool result format
    @classmethod
    def create_tool_result(cls, success: bool, message: str, 
                          error_type: str = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized tool result"""
        result = {
            "success": success,
            "message": message
        }
        
        if not success and error_type:
            result["error_type"] = error_type
            
        if data:
            result.update(data)
            
        return result
    
    # Standard resource format
    @classmethod
    def create_resource_definition(cls, uri: str, name: str, 
                                 description: str, mime_type: str = "application/json") -> Dict[str, Any]:
        """Create standardized resource definition"""
        return {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type
        }
    
    # Standard prompt format
    @classmethod
    def create_prompt_definition(cls, name: str, description: str, 
                               arguments: list = None) -> Dict[str, Any]:
        """Create standardized prompt definition"""
        return {
            "name": name,
            "description": description,
            "arguments": arguments or []
        }
    
    # Common help patterns
    @classmethod
    def get_help_template(cls) -> str:
        """Get standardized help template"""
        return """Tools: {tools}
Resources: {resources}
Prompts: {prompts}

Usage: Use tool names with required parameters
Safety: {safety_features}"""
    
    # Standard error handling
    @classmethod
    def handle_error(cls, error: Exception, context: str = "") -> Dict[str, Any]:
        """Standardized error handling"""
        return cls.create_tool_result(
            success=False,
            message=f"{cls.COMMON_ERRORS['execution_error']}: {str(error)}",
            error_type="execution_error",
            data={"context": context} if context else None
        )
    
    # Common validation
    @classmethod
    def validate_required_params(cls, params: Dict[str, Any], 
                                required: list) -> tuple[bool, str]:
        """Validate required parameters"""
        missing = [param for param in required if not params.get(param)]
        if missing:
            return False, f"{cls.COMMON_ERRORS['missing_params']}: {', '.join(missing)}"
        return True, ""
    
    # Platform detection
    @classmethod
    def is_platform_supported(cls, platform: str, supported: list) -> tuple[bool, str]:
        """Check platform support"""
        if platform not in supported:
            return False, cls.COMMON_ERRORS["platform_error"]
        return True, ""