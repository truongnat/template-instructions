#!/bin/bash
# Ví Dụ 8: CLI Usage (Sử Dụng CLI)
#
# Setup Instructions:
# 1. Cài đặt: pip install agentic-sdlc[cli]
# 2. Cấu hình API keys
# 3. Chạy: bash 08-cli-usage.sh
#
# Dependencies:
# - agentic-sdlc[cli]>=3.0.0
#
# Expected Output:
# - Project được khởi tạo
# - Configuration được set
# - Workflow được chạy
# - Agents được quản lý

echo "======================================================================"
echo "VÍ DỤ: SỬ DỤNG CLI AGENTIC SDLC"
echo "======================================================================"

# 1. Khởi tạo project mới
echo ""
echo "✓ Khởi tạo project mới..."
agentic init my-project --template basic

# 2. Xem cấu hình hiện tại
echo ""
echo "✓ Xem cấu hình..."
agentic config show

# 3. Set configuration
echo ""
echo "✓ Set configuration..."
agentic config set project_name "my-awesome-project"
agentic config set log_level "DEBUG"

# 4. Get specific config value
echo ""
echo "✓ Get config value..."
agentic config get project_name

# 5. List available agents
echo ""
echo "✓ List agents..."
agentic agent list

# 6. Create new agent
echo ""
echo "✓ Create agent..."
agentic agent create \
  --name "my-developer" \
  --role "developer" \
  --model "gpt-4" \
  --description "My custom developer agent"

# 7. Check agent status
echo ""
echo "✓ Check agent status..."
agentic agent status my-developer

# 8. Run workflow
echo ""
echo "✓ Run workflow..."
agentic run workflow.yaml --verbose

# 9. Run with specific agent
echo ""
echo "✓ Run with specific agent..."
agentic run task.yaml --agent my-developer

# 10. Export configuration
echo ""
echo "✓ Export configuration..."
agentic config export --output config-backup.yaml

# 11. Validate configuration
echo ""
echo "✓ Validate configuration..."
agentic config validate

# 12. Show version
echo ""
echo "✓ Show version..."
agentic --version

# 13. Show help
echo ""
echo "✓ Show help..."
agentic --help

echo ""
echo "======================================================================"
echo "✓ Tất cả ví dụ CLI đã hoàn thành!"
echo "======================================================================"
