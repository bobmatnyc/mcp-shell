# MCP Desktop Gateway Deployment
# Deploys as global NPM package

.PHONY: deploy-desktop-gateway clean-desktop-gateway status-desktop-gateway

# Configuration
SERVICE_NAME = mcp-desktop-gateway
PACKAGE_NAME = @bobmatnyc/mcp-desktop-gateway
MONOREPO_ROOT = $(shell cd ../.. && pwd)
SERVICE_ROOT = $(MONOREPO_ROOT)/services/mcp-desktop-gateway
BUILD_DIR = $(SERVICE_ROOT)/dist

# Colors
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

deploy-desktop-gateway: ## Deploy desktop gateway as NPM package
	@echo "$(BLUE)🖥️  Deploying Desktop Gateway$(NC)"
	@echo "================================="
	@echo "📦 Building NPM package..."
	@$(SERVICE_ROOT)/build-npm-package.sh
	@echo "📦 Creating package tarball..."
	@cd $(BUILD_DIR) && npm pack
	@TARBALL=$$(cd $(BUILD_DIR) && ls -t *.tgz | head -1); \
	echo "🔄 Installing package globally..."; \
	npm install -g --force "$(BUILD_DIR)/$$TARBALL"
	@echo "🧪 Verifying installation..."
	@if mcp-desktop-gateway --help >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Package verification passed$(NC)"; \
	else \
		echo "$(RED)❌ Package verification failed$(NC)"; \
		exit 1; \
	fi
	@echo "🧹 Cleaning up build artifacts..."
	@rm -rf $(BUILD_DIR)
	@echo "$(GREEN)✅ Desktop Gateway deployed successfully$(NC)"

status-desktop-gateway: ## Check desktop gateway deployment status
	@echo "$(BLUE)📊 Desktop Gateway Status$(NC)"
	@echo "================================"
	@if command -v mcp-desktop-gateway >/dev/null 2>&1; then \
		echo "$(GREEN)✅ mcp-desktop-gateway$(NC)"; \
		echo "     📍 $$(which mcp-desktop-gateway)"; \
		echo "     🏷️  Version: $$(mcp-desktop-gateway --version 2>/dev/null || echo 'Unknown')"; \
	else \
		echo "$(RED)❌ mcp-desktop-gateway (Not installed)$(NC)"; \
	fi

clean-desktop-gateway: ## Remove desktop gateway deployment
	@echo "$(YELLOW)🗑️  Removing Desktop Gateway$(NC)"
	@npm uninstall -g $(PACKAGE_NAME) 2>/dev/null || echo "Package not globally installed"
	@rm -rf $(BUILD_DIR)
	@echo "$(GREEN)✅ Desktop Gateway removed$(NC)"

help-desktop-gateway: ## Show desktop gateway commands
	@echo "$(BLUE)🖥️  Desktop Gateway Commands$(NC)"
	@echo "==================================="
	@echo ""
	@echo "make deploy-desktop-gateway    Deploy as NPM package"
	@echo "make status-desktop-gateway    Check deployment status"
	@echo "make clean-desktop-gateway     Remove deployment"
	@echo ""
	@echo "Configuration:"
	@echo '  "mcp-desktop-gateway": {'
	@echo '    "command": "mcp-desktop-gateway",'
	@echo '    "args": [],'
	@echo '    "env": {'
	@echo '      "MCP_DEV_MODE": "true",'
	@echo '      "PYTHONUNBUFFERED": "1"'
	@echo '    }'
	@echo '  }'