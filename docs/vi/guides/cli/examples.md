# CLI Examples

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp các ví dụ thực tế về cách sử dụng Agentic SDLC CLI trong các tình huống phổ biến. Mỗi example bao gồm context, commands, và giải thích chi tiết.

## Getting Started Examples

### Example 1: Khởi Tạo Project Mới

**Scenario:** Bạn muốn bắt đầu một project mới với Agentic SDLC.

```bash
# Tạo project directory
agentic init my-ai-project

# Di chuyển vào project
cd my-ai-project

# Xem cấu trúc được tạo
ls -la

# Output:
# .agentic/
# config.yaml
# logs/
# .gitignore
# README.md
```text

**Giải thích:**
- `agentic init` tạo cấu trúc project chuẩn
- Tự động tạo config file với default settings
- Khởi tạo git repository (trừ khi dùng `--no-git`)

### Example 2: Cấu Hình API Keys

**Scenario:** Cấu hình OpenAI API key để sử dụng GPT-4.

```bash
# Set OpenAI API key
agentic config set openai.api_key sk-proj-xxxxxxxxxxxxx

# Verify configuration
agentic config get openai.api_key

# Output: sk-proj-****** (masked for security)

# Set default model
agentic config set model.default_model gpt-4

# Xem tất cả config
agentic config show
```text

**Best Practice:**
```bash
# Sử dụng environment variable cho security
export OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Hoặc set global config
agentic config set openai.api_key $OPENAI_API_KEY --global
```text

### Example 3: Tạo Agent Đầu Tiên

**Scenario:** Tạo một developer agent để viết code.

```bash
# Tạo developer agent
agentic agent create python-dev \
  --role "Python Developer" \
  --model gpt-4 \
  --system-prompt "You are an expert Python developer specializing in clean, maintainable code."

# Verify agent được tạo
agentic agent list

# Output:
# ┌──────────────┬─────────────┬──────────────────┬────────┬────────┐
# │ ID           │ Name        │ Role             │ Model  │ Status │
# ├──────────────┼─────────────┼──────────────────┼────────┼────────┤
# │ agent-001    │ python-dev  │ Python Developer │ gpt-4  │ active │
# └──────────────┴─────────────┴──────────────────┴────────┴────────┘

# Xem chi tiết agent
agentic agent status python-dev
```text

## Development Workflow Examples

### Example 4: Automated Code Review

**Scenario:** Review code changes trước khi commit.

```bash
# Review một file cụ thể
agentic run code-review --file src/api/users.py

# Review với output report
agentic run code-review \
  --file src/api/users.py \
  --output review-report.json

# Review multiple files
agentic run code-review \
  --file "src/**/*.py" \
  --output reviews/

# Review với specific agent
agentic run code-review \
  --file src/api/users.py \
  --agent senior-reviewer
```text

**Integration với Git:**
```bash
# Review staged changes
git diff --name-only --cached | while read file; do
  if [[ $file == *.py ]]; then
    agentic run code-review --file "$file"
  fi
done

# Hoặc tạo git hook
# .git/hooks/pre-commit
#!/bin/bash
agentic run code-review --file "$(git diff --name-only --cached)"
```text

### Example 5: Test Generation

**Scenario:** Tự động generate unit tests cho code mới.

```bash
# Generate tests cho một file
agentic run test-generation \
  --file src/utils/helpers.py \
  --output tests/test_helpers.py

# Generate với coverage target
agentic run test-generation \
  --file src/api/users.py \
  --coverage 90 \
  --output tests/api/test_users.py

# Generate tests cho toàn bộ module
agentic run test-generation \
  --file "src/api/*.py" \
  --output tests/api/
```text

**Chạy generated tests:**
```bash
# Run tests
pytest tests/test_helpers.py

# Run với coverage
pytest --cov=src tests/
```text

### Example 6: Documentation Generation

**Scenario:** Tự động generate documentation từ code.

```bash
# Generate API documentation
agentic run doc-generator \
  --file src/api/ \
  --output docs/api/ \
  --format markdown

# Generate với specific style
agentic run doc-generator \
  --file src/ \
  --output docs/ \
  --style google \
  --include-examples

# Generate README
agentic run readme-generator \
  --project-dir . \
  --output README.md
```text

### Example 7: Bug Fixing

**Scenario:** Tự động phát hiện và fix bugs.

```bash
# Analyze code for bugs
agentic run bug-detector \
  --file src/api/users.py \
  --output bug-report.json

# Auto-fix simple bugs
agentic run bug-fixer \
  --file src/api/users.py \
  --auto-fix \
  --backup

# Fix với human review
agentic run bug-fixer \
  --file src/api/users.py \
  --interactive
```text

## CI/CD Integration Examples

### Example 8: GitHub Actions Integration

**Scenario:** Tích hợp Agentic SDLC vào GitHub Actions workflow.

```yaml
# .github/workflows/agentic-review.yml
name: Agentic Code Review

on:
  pull_request:
    branches: [main]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Agentic SDLC
        run: pip install agentic-sdlc[cli]
      
      - name: Configure API Key
        run: |
          agentic config set openai.api_key ${{ secrets.OPENAI_API_KEY }}
      
      - name: Run Code Review
        run: |
          agentic run code-review \
            --file "$(git diff --name-only origin/main)" \
            --output-format json > review.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: review-results
          path: review.json
```text

**Commands để test locally:**
```bash
# Simulate CI environment
export OPENAI_API_KEY=sk-...

# Run review như CI
agentic run code-review \
  --file "$(git diff --name-only main)" \
  --output-format json
```text

### Example 9: GitLab CI Integration

**Scenario:** Sử dụng Agentic SDLC trong GitLab CI pipeline.

```yaml
# .gitlab-ci.yml
stages:
  - review
  - test
  - deploy

code_review:
  stage: review
  image: python:3.10
  before_script:
    - pip install agentic-sdlc[cli]
    - agentic config set openai.api_key $OPENAI_API_KEY
  script:
    - agentic run code-review --file "src/**/*.py" --output review.json
  artifacts:
    paths:
      - review.json
    expire_in: 1 week

automated_tests:
  stage: test
  image: python:3.10
  before_script:
    - pip install agentic-sdlc[cli]
    - agentic config set openai.api_key $OPENAI_API_KEY
  script:
    - agentic run test-generation --file "src/**/*.py" --output tests/
    - pytest tests/
```text

### Example 10: Pre-commit Hooks

**Scenario:** Validate code trước khi commit.

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running Agentic SDLC pre-commit checks..."

# Get staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep ".py$")

if [ -z "$STAGED_FILES" ]; then
  echo "No Python files to check"
  exit 0
fi

# Run code review
echo "Reviewing code..."
for file in $STAGED_FILES; do
  agentic run code-review --file "$file" || exit 1
done

# Run linting
echo "Running linter..."
agentic run lint-check --file "$STAGED_FILES" || exit 1

echo "All checks passed!"
exit 0
```text

**Make hook executable:**
```bash
chmod +x .git/hooks/pre-commit
```text

## Multi-Agent Workflow Examples

### Example 11: Complete Feature Development

**Scenario:** Sử dụng multiple agents để develop một feature hoàn chỉnh.

```bash
# Step 1: Requirements analysis
agentic run requirements-analysis \
  --agent business-analyst \
  --input feature-request.md \
  --output requirements.md

# Step 2: Architecture design
agentic run architecture-design \
  --agent software-architect \
  --input requirements.md \
  --output architecture.md

# Step 3: Implementation
agentic run implementation \
  --agent senior-developer \
  --input architecture.md \
  --output src/new-feature/

# Step 4: Test generation
agentic run test-generation \
  --agent test-engineer \
  --file src/new-feature/ \
  --output tests/new-feature/

# Step 5: Code review
agentic run code-review \
  --agent code-reviewer \
  --file src/new-feature/ \
  --output review-report.json

# Step 6: Documentation
agentic run doc-generation \
  --agent technical-writer \
  --file src/new-feature/ \
  --output docs/new-feature.md
```text

**Automated workflow:**
```bash
# Chạy toàn bộ workflow với một command
agentic run feature-development-workflow \
  --params feature-params.json \
  --output feature-output/
```text

### Example 12: Code Refactoring

**Scenario:** Refactor legacy code với multiple agents.

```bash
# Step 1: Code analysis
agentic run code-analysis \
  --agent code-analyzer \
  --file legacy/old-module.py \
  --output analysis-report.json

# Step 2: Refactoring plan
agentic run refactoring-plan \
  --agent software-architect \
  --input analysis-report.json \
  --output refactoring-plan.md

# Step 3: Execute refactoring
agentic run refactor \
  --agent senior-developer \
  --input refactoring-plan.md \
  --file legacy/old-module.py \
  --output src/new-module.py

# Step 4: Verify refactoring
agentic run refactoring-verification \
  --agent test-engineer \
  --old-file legacy/old-module.py \
  --new-file src/new-module.py \
  --output verification-report.json
```text

## Advanced Examples

### Example 13: Custom Workflow với Parameters

**Scenario:** Chạy custom workflow với complex parameters.

```bash
# Create parameters file
cat > workflow-params.json << EOF
{
  "input_files": ["src/api/users.py", "src/api/auth.py"],
  "output_dir": "output/",
  "options": {
    "strict_mode": true,
    "coverage_threshold": 85,
    "max_iterations": 15
  },
  "agents": {
    "reviewer": "senior-reviewer",
    "tester": "test-engineer"
  }
}
EOF

# Run workflow với parameters
agentic run custom-workflow --params workflow-params.json

# Hoặc inline parameters
agentic run custom-workflow \
  --input-files "src/api/*.py" \
  --output-dir output/ \
  --strict-mode true \
  --coverage-threshold 85
```text

### Example 14: Parallel Execution

**Scenario:** Chạy multiple tasks song song.

```bash
# Run multiple workflows in parallel
agentic run code-review --file src/api/ --async &
agentic run test-generation --file src/api/ --async &
agentic run doc-generation --file src/api/ --async &

# Wait for all to complete
wait

echo "All tasks completed!"
```text

**Using GNU Parallel:**
```bash
# Install parallel
# brew install parallel  # macOS
# apt-get install parallel  # Ubuntu

# Review multiple files in parallel
find src/ -name "*.py" | parallel -j 4 agentic run code-review --file {}

# Process with progress
find src/ -name "*.py" | parallel --progress agentic run code-review --file {}
```text

### Example 15: Watch Mode for Development

**Scenario:** Auto-run workflow khi files thay đổi.

```bash
# Watch mode - rerun on file changes
agentic run test-suite --watch

# Watch specific files
agentic run code-review --file src/api/users.py --watch

# Watch với custom interval
agentic run lint-check --file "src/**/*.py" --watch --interval 5
```text

**Using external tools:**
```bash
# Using watchexec
watchexec -e py "agentic run code-review --file src/"

# Using entr
find src/ -name "*.py" | entr agentic run test-suite
```text

### Example 16: Debugging và Troubleshooting

**Scenario:** Debug workflow execution issues.

```bash
# Enable verbose logging
agentic --verbose run problematic-workflow

# Enable debug log level
agentic --log-level DEBUG run problematic-workflow

# Dry run để test
agentic run workflow --dry-run

# Save detailed logs
agentic --verbose --log-level DEBUG run workflow 2>&1 | tee debug.log

# Check agent status
agentic agent status my-agent --show-history --show-metrics
```text

### Example 17: Batch Processing

**Scenario:** Process nhiều files hoặc tasks.

```bash
# Process all Python files
for file in src/**/*.py; do
  echo "Processing $file..."
  agentic run code-review --file "$file" --output "reviews/$(basename $file).json"
done

# Process với error handling
for file in src/**/*.py; do
  if ! agentic run code-review --file "$file"; then
    echo "Failed: $file" >> failed-files.txt
  fi
done

# Process với progress tracking
total=$(find src/ -name "*.py" | wc -l)
current=0

find src/ -name "*.py" | while read file; do
  current=$((current + 1))
  echo "[$current/$total] Processing $file..."
  agentic run code-review --file "$file"
done
```text

## Integration Examples

### Example 18: Slack Integration

**Scenario:** Send workflow results đến Slack.

```bash
# Run workflow và send results
agentic run code-review --file src/api/users.py --output review.json

# Send to Slack
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"Code review completed\", \"attachments\": [$(cat review.json)]}"
```text

**Automated script:**
```bash
#!/bin/bash
# review-and-notify.sh

# Run review
agentic run code-review --file "$1" --output-format json > review.json

# Check if passed
if jq -e '.status == "passed"' review.json > /dev/null; then
  message="✅ Code review passed for $1"
else
  message="❌ Code review failed for $1"
fi

# Send to Slack
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"$message\"}"
```text

### Example 19: Jira Integration

**Scenario:** Create Jira tickets từ workflow results.

```bash
# Run bug detection
agentic run bug-detector --file src/ --output-format json > bugs.json

# Create Jira tickets for each bug
jq -c '.bugs[]' bugs.json | while read bug; do
  title=$(echo $bug | jq -r '.title')
  description=$(echo $bug | jq -r '.description')
  
  # Create Jira ticket
  curl -X POST $JIRA_API_URL/issue \
    -H "Authorization: Bearer $JIRA_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"fields\": {
        \"project\": {\"key\": \"PROJ\"},
        \"summary\": \"$title\",
        \"description\": \"$description\",
        \"issuetype\": {\"name\": \"Bug\"}
      }
    }"
done
```text

### Example 20: Docker Integration

**Scenario:** Chạy Agentic SDLC trong Docker container.

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install Agentic SDLC
RUN pip install agentic-sdlc[cli]

# Copy config
COPY config.yaml /app/config.yaml

# Set working directory
WORKDIR /app

# Entry point
ENTRYPOINT ["agentic"]
```text

**Build và run:**
```bash
# Build image
docker build -t agentic-cli .

# Run workflow
docker run -v $(pwd):/app agentic-cli run code-review --file src/

# Run với environment variables
docker run \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd):/app \
  agentic-cli run workflow
```text

## Scripting Examples

### Example 21: Complete CI/CD Script

```bash
#!/bin/bash
# ci-cd-pipeline.sh

set -e  # Exit on error

echo "🚀 Starting CI/CD Pipeline..."

# Step 1: Code Review
echo "📝 Running code review..."
agentic run code-review --file "src/**/*.py" --output review.json

# Step 2: Run Tests
echo "🧪 Running tests..."
agentic run test-suite --coverage 80

# Step 3: Security Scan
echo "🔒 Running security scan..."
agentic run security-scan --file "src/**/*.py" --output security-report.json

# Step 4: Build
echo "🔨 Building application..."
agentic run build --output dist/

# Step 5: Deploy
echo "🚢 Deploying to production..."
agentic run deploy --env production --confirm

echo "✅ Pipeline completed successfully!"
```text

### Example 22: Daily Report Generator

```bash
#!/bin/bash
# daily-report.sh

DATE=$(date +%Y-%m-%d)
REPORT_FILE="reports/daily-report-$DATE.md"

echo "# Daily Development Report - $DATE" > $REPORT_FILE
echo "" >> $REPORT_FILE

# Code quality metrics
echo "## Code Quality" >> $REPORT_FILE
agentic run code-quality-check --file src/ --format markdown >> $REPORT_FILE

# Test coverage
echo "## Test Coverage" >> $REPORT_FILE
agentic run coverage-report --format markdown >> $REPORT_FILE

# Security issues
echo "## Security Issues" >> $REPORT_FILE
agentic run security-scan --file src/ --format markdown >> $REPORT_FILE

# Send report
mail -s "Daily Report - $DATE" team@example.com < $REPORT_FILE
```

## Tài Liệu Liên Quan

- [CLI Overview](overview.md) - Giới thiệu về CLI
- [Command Reference](commands.md) - Chi tiết về commands
- [Configuration Guide](../../getting-started/configuration.md) - Hướng dẫn cấu hình
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [Agents](../agents/overview.md) - Quản lý agents

## Tóm Tắt

Các examples trong tài liệu này minh họa:

- **Getting Started**: Khởi tạo projects, cấu hình, tạo agents
- **Development Workflows**: Code review, testing, documentation, bug fixing
- **CI/CD Integration**: GitHub Actions, GitLab CI, pre-commit hooks
- **Multi-Agent Workflows**: Feature development, refactoring
- **Advanced Usage**: Custom workflows, parallel execution, debugging
- **Integrations**: Slack, Jira, Docker
- **Scripting**: Automation scripts, daily reports

Sử dụng các examples này làm starting point và customize theo nhu cầu của bạn. Kết hợp multiple commands để tạo powerful automation workflows.
