# Contributing to MCP Shell

Thank you for your interest in contributing to MCP Shell! This guide will help you get started.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/mcp-shell.git
   cd mcp-shell
   ```
3. **Set up development environment**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
4. **Run tests** to ensure everything works:
   ```bash
   python -m pytest tests/
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Git
- Node.js 16+ (for DXT building)

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest pytest-cov ruff mypy

# Install DXT toolchain
npm install -g @anthropic-ai/dxt
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific tests
python -m pytest tests/unit/connectors/shell/
python -m pytest tests/integration/

# Run linting
ruff check src/
mypy src/
```

### Writing Tests
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies appropriately

## 📁 Project Structure

```
mcp-shell/
├── src/
│   ├── connectors/         # Connector implementations
│   │   ├── shell/         # Shell command connector
│   │   ├── applescript/   # AppleScript connector (macOS)
│   │   └── chrome/        # Chrome automation connector
│   ├── core/              # Core framework
│   │   ├── base_connector.py  # Base connector class
│   │   ├── config.py      # Configuration management
│   │   └── registry.py    # Connector registry
│   └── templates/         # Prompt templates
├── config/                # Configuration files
├── tests/                 # Test suite
└── dxt-package/          # DXT package build
```

## 🔌 Adding New Connectors

### Connector Template
```python
from src.core.base_connector import BaseConnector
from src.core.models import ToolResult

class MyConnector(BaseConnector):
    """My custom connector for XYZ functionality."""
    
    def get_available_tools(self) -> list:
        return [
            {
                "name": "my_tool",
                "description": "Does something useful",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "Parameter description"}
                    },
                    "required": ["param"]
                }
            }
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: dict) -> ToolResult:
        if tool_name == "my_tool":
            return await self._my_tool_implementation(arguments)
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _my_tool_implementation(self, args: dict) -> ToolResult:
        # Implement your tool logic here
        return ToolResult(
            content=f"Result for {args['param']}",
            is_error=False
        )
```

### Connector Registration
Add your connector to `src/core/registry.py`:
```python
from src.connectors.my_connector import MyConnector

# Register the connector
CONNECTORS = {
    "my_connector": MyConnector,
    # ... other connectors
}
```

## 📝 Code Style

### Python Style Guide
- Follow PEP 8
- Use `ruff` for linting and formatting
- Use type hints throughout
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Quality Tools
```bash
# Linting
ruff check src/

# Type checking
mypy src/

# Formatting
ruff format src/
```

### Commit Message Format
Use conventional commits:
- `feat: add new connector for XYZ`
- `fix: resolve issue with shell escaping`
- `docs: update installation instructions`
- `test: add unit tests for chrome connector`
- `refactor: simplify config loading logic`

## 🔒 Security Guidelines

### Security Best Practices
- **Input validation**: Always validate and sanitize user inputs
- **Command injection prevention**: Use proper shell escaping
- **File access controls**: Limit file operations to safe directories
- **Error handling**: Don't expose sensitive information in error messages
- **Permissions**: Request minimal necessary permissions

### Security Review Checklist
- [ ] User inputs are properly validated
- [ ] Shell commands are properly escaped
- [ ] File paths are validated and constrained
- [ ] Error messages don't leak sensitive data
- [ ] No hardcoded credentials or secrets

## 📚 Documentation

### Documentation Standards
- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Include usage examples in connector documentation
- Update CHANGELOG.md for all changes

### Documentation Format
```python
def my_function(param: str) -> str:
    """Brief description of the function.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of the return value
        
    Raises:
        ValueError: When param is invalid
        
    Example:
        >>> result = my_function("test")
        >>> print(result)
        "test result"
    """
```

## 🚀 Release Process

### Version Bumping
1. Update version in `pyproject.toml`
2. Update `VERSION` file
3. Update `CHANGELOG.md`
4. Create git tag: `git tag -a v1.3.2 -m "Release v1.3.2"`

### DXT Package Building
```bash
cd dxt-package
dxt pack
# Test the generated .dxt file
```

## 🆘 Getting Help

- **Questions**: Open a [Discussion](https://github.com/bobmatnyc/mcp-shell/discussions)
- **Bug Reports**: Open an [Issue](https://github.com/bobmatnyc/mcp-shell/issues)
- **Feature Requests**: Open an [Issue](https://github.com/bobmatnyc/mcp-shell/issues) with the "enhancement" label

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes with tests
4. **Run** the test suite and ensure it passes
5. **Update** documentation as needed
6. **Submit** a pull request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

### PR Review Criteria
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (unless versioned appropriately)
- [ ] Security considerations addressed

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to MCP Shell! 🎉