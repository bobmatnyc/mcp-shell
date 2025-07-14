"""
Meta Prompt Templates
Optimized templates for prompt training and LangChain integration
"""

from typing import Dict, Any


class MetaPromptTemplates:
    """Templates for prompt training and meta-prompt operations"""
    
    # Prompt management operations compressed
    OPERATIONS = {
        "create": "Create new prompt version",
        "deploy": "Deploy version as active",
        "rollback": "Rollback to previous version", 
        "export": "Export prompts for use",
        "import": "Import external prompt",
        "metrics": "Update performance metrics"
    }
    
    # Version states compressed
    STATES = {
        "active": "Currently deployed",
        "experimental": "Testing phase",
        "retired": "No longer used"
    }
    
    # Metrics tracked compressed
    METRICS = {
        "rating": "Average user rating",
        "success_rate": "Task completion rate",
        "error_rate": "Error frequency", 
        "usage_count": "Total usage"
    }
    
    # Training parameters compressed
    TRAINING = {
        "model": "Target LLM model",
        "temperature": "Response creativity",
        "max_tokens": "Response length limit",
        "training_data": "Examples used",
        "evaluation": "Success criteria"
    }
    
    @classmethod
    def get_prompt_help(cls) -> str:
        """Get compressed prompt training help"""
        return f"""Prompt Management System:
Operations: {', '.join(cls.OPERATIONS.keys())}
States: {', '.join(cls.STATES.keys())}
Metrics: {', '.join(cls.METRICS.keys())}

Version Control: Automated versioning, rollback support
Training: LangChain integration, performance tracking
Export: Ready-to-use prompt files"""
    
    @classmethod
    def get_training_config(cls, prompt_type: str) -> Dict[str, Any]:
        """Get optimized training configuration"""
        base_config = {
            "temperature": 0.1,
            "max_tokens": 1000,
            "evaluation_metrics": list(cls.METRICS.keys())
        }
        
        # Type-specific optimizations
        if prompt_type == "system":
            base_config.update({
                "temperature": 0.0,  # More deterministic for system prompts
                "max_tokens": 500   # Shorter for system guidance
            })
        elif prompt_type == "automation":
            base_config.update({
                "temperature": 0.2,  # Slightly creative for automation
                "max_tokens": 800   # Medium length for instructions
            })
            
        return base_config
    
    @classmethod
    def format_version_info(cls, version_data: Dict[str, Any]) -> str:
        """Format version information efficiently"""
        return f"""Version {version_data['version']} ({version_data.get('state', 'unknown')})
Created: {version_data.get('created_at', 'unknown')}
Rating: {version_data.get('avg_rating', 0):.1f}
Success: {version_data.get('success_rate', 0):.1%}
Usage: {version_data.get('usage_count', 0)}"""
    
    @classmethod
    def get_langchain_integration(cls) -> str:
        """Get LangChain integration guidance"""
        return """LangChain Integration:
• Auto-training: Feedback-driven prompt optimization
• Version control: Seamless prompt evolution
• Performance tracking: Success/error metrics
• Export format: LangChain-compatible templates
• Evaluation: Automated quality assessment"""