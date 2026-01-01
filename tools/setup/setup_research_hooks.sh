#!/bin/bash
# Setup Research Agent Hooks
# This script configures automated research hooks for Kiro IDE

set -e

echo "============================================================"
echo "🔧 Setting Up Research Agent Hooks"
echo "============================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .kiro directory exists
if [ ! -d ".kiro" ]; then
    echo -e "${YELLOW}⚠️  .kiro directory not found. Creating...${NC}"
    mkdir -p .kiro/hooks
fi

# Check if hooks directory exists
if [ ! -d ".kiro/hooks" ]; then
    echo -e "${YELLOW}⚠️  .kiro/hooks directory not found. Creating...${NC}"
    mkdir -p .kiro/hooks
fi

# Copy hook configuration
echo "📋 Installing hook configuration..."
if [ -f ".kiro/hooks/auto-research-hook.json" ]; then
    echo -e "${GREEN}✓ Hook configuration already exists${NC}"
else
    echo -e "${RED}✗ Hook configuration not found${NC}"
    echo "Please ensure auto-research-hook.json is in .kiro/hooks/"
    exit 1
fi

# Make research scripts executable
echo "🔐 Making research scripts executable..."
chmod +x tools/research/research_agent.py 2>/dev/null || echo -e "${YELLOW}⚠️  tools/research/research_agent.py not found${NC}"
chmod +x tools/research/research_mcp.py 2>/dev/null || echo -e "${YELLOW}⚠️  tools/research/research_mcp.py not found${NC}"

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
python3 -c "import neo4j" 2>/dev/null && echo -e "${GREEN}✓ neo4j installed${NC}" || echo -e "${YELLOW}⚠️  neo4j not installed (optional)${NC}"
python3 -c "import requests" 2>/dev/null && echo -e "${GREEN}✓ requests installed${NC}" || echo -e "${YELLOW}⚠️  requests not installed (optional)${NC}"

# Create research reports directory
echo "📁 Creating research reports directory..."
mkdir -p docs/research-reports
echo -e "${GREEN}✓ Created docs/research-reports/${NC}"

# Test research agent
echo "🧪 Testing research agent..."
if python3 tools/research/research_agent.py --task "test" --type general > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Research agent working${NC}"
else
    echo -e "${YELLOW}⚠️  Research agent test failed (may need dependencies)${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✓ Research Agent Hooks Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "📚 Available Hooks:"
echo "  • Research Before Planning (@PM)"
echo "  • Research Before Development (@DEV)"
echo "  • Research Before Bug Fix (@TESTER)"
echo "  • Research Before Architecture (@SA)"
echo "  • Research On Demand (/research)"
echo ""
echo "🎯 Usage:"
echo "  1. Hooks trigger automatically when you mention roles"
echo "  2. Or use: /research <task description>"
echo "  3. View reports in: docs/research-reports/"
echo ""
echo "⚙️  Configuration:"
echo "  • Edit: .kiro/hooks/auto-research-hook.json"
echo "  • Enable/disable individual hooks"
echo "  • Adjust trigger patterns"
echo ""
echo "🔧 Next Steps:"
echo "  1. Restart Kiro IDE to load hooks"
echo "  2. Try: /research Build authentication system"
echo "  3. Check: docs/research-reports/ for results"
echo ""
