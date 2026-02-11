# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Agentic SDLC Kit.

## 🔍 Quick Diagnostics

### Run System Diagnostics

```bash
# Run comprehensive diagnostics
asdlc diagnose

# Check system health
asdlc brain health

# Verify configuration
asdlc config validate

# Check connectivity
asdlc brain status
```

### View Logs

```bash
# View recent logs
asdlc logs --tail 50

# View logs with specific level
asdlc logs --level ERROR

# Follow logs in real-time
asdlc logs --follow

# View logs for specific component
asdlc logs --component brain
asdlc logs --component workflow
```

## 🚨 Common Issues

### Installation Issues

#### Issue: Command not found after installation

**Symptoms:**
```bash
$ asdlc --version
bash: asdlc: command not found
```

**Solutions:**

1. **Verify installation:**
```bash
pip list | grep agentic-sdlc
```

2. **Check virtual environment:**
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. **Add to PATH:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
```

4. **Reinstall package:**
```bash
pip uninstall agentic-sdlc
pip install agentic-sdlc
```

#### Issue: Permission denied errors

**Symptoms:**
```bash
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use virtual environment (recommended):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install agentic-sdlc
```

2. **Install with --user flag:**
```bash
pip install --user agentic-sdlc
```

3. **Fix permissions:**
```bash
sudo chown -R $USER:$USER ~/.local
```

#### Issue: SSL certificate errors

**Symptoms:**
```bash
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**

1. **Update certificates:**
```bash
pip install --upgrade certifi
```

2. **Use trusted host:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org agentic-sdlc
```

3. **Update pip:**
```bash
pip install --upgrade pip
```

#### Issue: Dependency conflicts

**Symptoms:**
```bash
ERROR: Cannot install agentic-sdlc because these package versions have conflicting dependencies
```

**Solutions:**

1. **Use fresh virtual environment:**
```bash
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install agentic-sdlc
```

2. **Install specific version:**
```bash
pip install agentic-sdlc==2.5.0
```

3. **Check Python version:**
```bash
python --version  # Should be 3.9+
```

### Configuration Issues

#### Issue: Configuration file not found

**Symptoms:**
```bash
ERROR: Configuration file 'agentic.yaml' not found
```

**Solutions:**

1. **Initialize project:**
```bash
asdlc init
```

2. **Create configuration manually:**
```bash
cp agentic.yaml.template agentic.yaml
```

3. **Check current directory:**
```bash
pwd
ls -la agentic.yaml
```

#### Issue: Invalid configuration syntax

**Symptoms:**
```bash
ERROR: Invalid YAML syntax in agentic.yaml
```

**Solutions:**

1. **Validate YAML syntax:**
```bash
# Use online validator or
python -c "import yaml; yaml.safe_load(open('agentic.yaml'))"
```

2. **Check indentation:**
```yaml
# Correct (2 spaces)
core:
  llm_provider: "openai"

# Incorrect (tabs or mixed)
core:
	llm_provider: "openai"
```

3. **Reset to defaults:**
```bash
asdlc config reset
```

#### Issue: Environment variables not loading

**Symptoms:**
```bash
ERROR: OPENAI_API_KEY not found
```

**Solutions:**

1. **Check .env file exists:**
```bash
ls -la .env
```

2. **Verify variable is set:**
```bash
echo $OPENAI_API_KEY
```

3. **Source .env manually:**
```bash
export $(cat .env | xargs)
```

4. **Check .env format:**
```bash
# Correct
OPENAI_API_KEY=sk-xxx

# Incorrect (no spaces around =)
OPENAI_API_KEY = sk-xxx
```

### Runtime Issues

#### Issue: API key errors

**Symptoms:**
```bash
ERROR: Invalid API key provided
ERROR: Incorrect API key provided
```

**Solutions:**

1. **Verify API key:**
```bash
echo $OPENAI_API_KEY
# Should start with sk-
```

2. **Check key validity:**
```bash
# Test OpenAI key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. **Regenerate key:**
- Go to provider dashboard
- Generate new API key
- Update .env file

4. **Check key permissions:**
- Ensure key has required permissions
- Check usage limits and quotas

#### Issue: Connection timeout

**Symptoms:**
```bash
ERROR: Connection timeout after 30 seconds
ERROR: Failed to connect to API
```

**Solutions:**

1. **Check internet connectivity:**
```bash
ping api.openai.com
```

2. **Increase timeout:**
```yaml
# agentic.yaml
core:
  request_timeout: 300  # Increase to 5 minutes
```

3. **Check proxy settings:**
```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

4. **Use local LLM:**
```bash
# Switch to Ollama
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
```

#### Issue: Rate limit exceeded

**Symptoms:**
```bash
ERROR: Rate limit exceeded
ERROR: Too many requests
```

**Solutions:**

1. **Wait and retry:**
```bash
# Automatic retry with backoff
asdlc config set core.max_retries 5
asdlc config set core.retry_delay 10
```

2. **Reduce concurrency:**
```yaml
# agentic.yaml
core:
  max_concurrent_agents: 2  # Reduce from 5
```

3. **Upgrade API plan:**
- Check provider dashboard
- Upgrade to higher tier

4. **Use different model:**
```yaml
# Use faster/cheaper model
core:
  default_model: "gpt-3.5-turbo"
```

#### Issue: Out of memory errors

**Symptoms:**
```bash
ERROR: Out of memory
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Reduce batch size:**
```yaml
workflows:
  defaults:
    max_parallel_agents: 2  # Reduce parallelism
```

2. **Clear cache:**
```bash
asdlc brain clear-cache
rm -rf .cache/
```

3. **Increase system memory:**
```bash
# Check current usage
free -h

# Close other applications
```

4. **Use smaller model:**
```yaml
core:
  default_model: "gpt-3.5-turbo"  # Smaller than gpt-4
```

### Brain Issues

#### Issue: Brain not learning

**Symptoms:**
```bash
WARNING: Brain learning disabled
INFO: No patterns learned
```

**Solutions:**

1. **Enable brain:**
```yaml
# agentic.yaml
brain:
  enabled: true
  auto_learn: true
```

2. **Check brain status:**
```bash
asdlc brain status
```

3. **Initialize brain state:**
```bash
asdlc brain init-state --sprint 1
```

4. **Verify learning rate:**
```yaml
brain:
  learning_rate: 0.1  # Should be > 0
```

#### Issue: Brain state corrupted

**Symptoms:**
```bash
ERROR: Failed to load brain state
ERROR: Invalid brain state format
```

**Solutions:**

1. **Reset brain state:**
```bash
asdlc brain reset
```

2. **Restore from backup:**
```bash
cp states/brain_state.db.backup states/brain_state.db
```

3. **Reinitialize:**
```bash
rm states/brain_state.db
asdlc brain init-state --sprint 1
```

#### Issue: Brain health check failing

**Symptoms:**
```bash
ERROR: Brain health check failed
WARNING: Brain component unhealthy
```

**Solutions:**

1. **Run diagnostics:**
```bash
asdlc brain health --verbose
```

2. **Check dependencies:**
```bash
# Verify database connectivity
asdlc brain status

# Check file permissions
ls -la states/
```

3. **Restart brain:**
```bash
asdlc brain restart
```

### Workflow Issues

#### Issue: Workflow execution fails

**Symptoms:**
```bash
ERROR: Workflow execution failed
ERROR: Agent execution timeout
```

**Solutions:**

1. **Check workflow configuration:**
```bash
asdlc config validate .agent/workflows/cycle.yaml
```

2. **Increase timeout:**
```yaml
# .agent/workflows/cycle.yaml
config:
  timeout: 3600  # Increase timeout
```

3. **Check agent availability:**
```bash
asdlc agent list
asdlc agent info PM
```

4. **View workflow logs:**
```bash
asdlc logs --component workflow --tail 100
```

#### Issue: Agent not responding

**Symptoms:**
```bash
ERROR: Agent PM not responding
WARNING: Agent timeout after 300 seconds
```

**Solutions:**

1. **Check agent status:**
```bash
asdlc agent status PM
```

2. **Restart agent:**
```bash
asdlc agent restart PM
```

3. **Increase agent timeout:**
```yaml
# .agent/agents/pm.yaml
llm:
  timeout: 600  # Increase timeout
```

4. **Check LLM connectivity:**
```bash
asdlc brain status
```

#### Issue: Workflow stuck in progress

**Symptoms:**
```bash
INFO: Workflow status: IN_PROGRESS (for hours)
```

**Solutions:**

1. **Check workflow status:**
```bash
asdlc workflow status <workflow-id>
```

2. **Cancel workflow:**
```bash
asdlc workflow cancel <workflow-id>
```

3. **Check for deadlocks:**
```bash
asdlc logs --component workflow --grep "deadlock"
```

4. **Restart workflow:**
```bash
asdlc workflow restart <workflow-id>
```

### Integration Issues

#### Issue: GitHub integration not working

**Symptoms:**
```bash
ERROR: Failed to connect to GitHub
ERROR: Invalid GitHub token
```

**Solutions:**

1. **Verify token:**
```bash
echo $GITHUB_TOKEN
```

2. **Test token:**
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

3. **Check token permissions:**
- Go to GitHub Settings → Developer settings → Personal access tokens
- Ensure token has required scopes (repo, workflow)

4. **Regenerate token:**
```bash
# Generate new token and update .env
GITHUB_TOKEN=ghp_new_token_here
```

#### Issue: Neo4j connection failed

**Symptoms:**
```bash
ERROR: Failed to connect to Neo4j
ERROR: Authentication failed
```

**Solutions:**

1. **Check Neo4j is running:**
```bash
docker ps | grep neo4j
# or
systemctl status neo4j
```

2. **Verify credentials:**
```bash
echo $NEO4J_URI
echo $NEO4J_USER
echo $NEO4J_PASSWORD
```

3. **Test connection:**
```bash
cypher-shell -a $NEO4J_URI -u $NEO4J_USER -p $NEO4J_PASSWORD
```

4. **Start Neo4j:**
```bash
docker-compose up -d neo4j
# or
systemctl start neo4j
```

### Docker Issues

#### Issue: Docker container won't start

**Symptoms:**
```bash
ERROR: Container exited with code 1
```

**Solutions:**

1. **Check logs:**
```bash
docker-compose logs agentic-sdlc
```

2. **Verify environment variables:**
```bash
docker-compose config
```

3. **Check port conflicts:**
```bash
lsof -i :8000
```

4. **Rebuild container:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Issue: Volume mount issues

**Symptoms:**
```bash
ERROR: Permission denied accessing /workspace
```

**Solutions:**

1. **Fix permissions:**
```bash
sudo chown -R $USER:$USER ./data ./logs
```

2. **Check volume mounts:**
```yaml
# docker-compose.yml
volumes:
  - ./:/workspace:rw  # Ensure read-write
```

3. **Use named volumes:**
```yaml
volumes:
  - data:/app/data
  - logs:/app/logs
```

## 🔧 Advanced Troubleshooting

### Enable Debug Logging

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Or in agentic.yaml
monitoring:
  log_level: DEBUG
```

### Collect Diagnostic Information

```bash
# Generate diagnostic report
asdlc diagnose --output diagnostic-report.txt

# Include:
# - System information
# - Configuration
# - Recent logs
# - Health checks
# - Version information
```

### Performance Issues

**Slow response times:**

1. **Enable caching:**
```yaml
storage:
  cache_enabled: true
  cache_ttl: 3600
```

2. **Use local LLM:**
```bash
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
```

3. **Reduce model size:**
```yaml
core:
  default_model: "gpt-3.5-turbo"
```

4. **Increase parallelism:**
```yaml
workflows:
  defaults:
    max_parallel_agents: 5
```

### Database Issues

**Database corruption:**

```bash
# Backup current state
cp states/brain_state.db states/brain_state.db.backup

# Reset database
rm states/brain_state.db
asdlc brain init-state

# Restore if needed
cp states/brain_state.db.backup states/brain_state.db
```

**Database locked:**

```bash
# Check for locks
lsof states/brain_state.db

# Kill locking process
kill -9 <PID>

# Restart
asdlc brain restart
```

## 📊 Monitoring and Alerts

### Set Up Monitoring

```yaml
# agentic.yaml
monitoring:
  enabled: true
  metrics_enabled: true
  health_check_interval: 60
  alert_on_failure: true
  
  alerts:
    - type: "error_rate"
      threshold: 0.1
      action: "notify"
    
    - type: "response_time"
      threshold: 5000
      action: "log"
```

### View Metrics

```bash
# View system metrics
asdlc metrics show

# View specific metric
asdlc metrics show --metric response_time

# Export metrics
asdlc metrics export --format json
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this guide** for common issues
2. **Run diagnostics:** `asdlc diagnose`
3. **Check logs:** `asdlc logs --tail 100`
4. **Search GitHub issues:** [github.com/truongnat/agentic-sdlc/issues](https://github.com/truongnat/agentic-sdlc/issues)

### Reporting Issues

When reporting issues, include:

1. **System information:**
```bash
asdlc --version
python --version
uname -a
```

2. **Configuration:**
```bash
asdlc config show
```

3. **Logs:**
```bash
asdlc logs --tail 100 > logs.txt
```

4. **Steps to reproduce:**
- What you did
- What you expected
- What actually happened

5. **Diagnostic report:**
```bash
asdlc diagnose --output diagnostic.txt
```

### Community Support

- **GitHub Issues:** [github.com/truongnat/agentic-sdlc/issues](https://github.com/truongnat/agentic-sdlc/issues)
- **Discussions:** [github.com/truongnat/agentic-sdlc/discussions](https://github.com/truongnat/agentic-sdlc/discussions)
- **Documentation:** [docs/](.)

## 📚 Additional Resources

- **[Getting Started Guide](GETTING_STARTED.md)** - Quick start tutorial
- **[Installation Guide](INSTALLATION.md)** - Setup instructions
- **[Configuration Guide](CONFIGURATION.md)** - Configuration reference
- **[Architecture Overview](ARCHITECTURE.md)** - System architecture

---

**Still having issues?** Open an issue on [GitHub](https://github.com/truongnat/agentic-sdlc/issues) with your diagnostic report.
