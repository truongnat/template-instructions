#!/usr/bin/env node
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import fs from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(__dirname, '..');

// Command mappings: command -> python script path
const commands = {
    // Brain & Core
    'brain': 'tools/brain/brain_cli.py',
    'learn': 'tools/neo4j/learning_engine.py',
    'research': 'tools/research/research_agent.py',

    // Layer 2: Intelligence
    'score': 'tools/layer2/scorer/input_scorer.py',
    'score-input': 'tools/layer2/scorer/input_scorer.py',
    'score-output': 'tools/layer2/scorer/output_scorer.py',
    'route': 'tools/layer2/router/workflow_router.py',
    'route-workflow': 'tools/layer2/router/workflow_router.py',
    'route-agent': 'tools/layer2/router/agent_router.py',
    'rules': 'tools/layer2/router/rules_engine.py',
    'monitor': 'tools/layer2/monitor/observer.py',
    'observe': 'tools/layer2/monitor/observer.py',
    'check-rules': 'tools/layer2/monitor/rule_checker.py',
    'audit': 'tools/layer2/monitor/audit_logger.py',

    // Layer 3: Infrastructure
    'release': 'tools/release/release.py',

    'agent': 'tools/run.py',
    'validate': 'tools/validation/validate.py',
    'health': 'tools/validation/health-check.py',
    'setup': 'tools/setup/init.py',


    // MCP
    'mcp': 'mcp/protocol.py',

    // Run arbitrary scripts
    'run': null // Special: run <path>
};

// Command aliases
const aliases = {
    'l2': 'layer2',
    'wf': 'workflow',
    's': 'score',
    'r': 'route',
    'm': 'monitor',
    'b': 'brain'
};

const args = process.argv.slice(2);
let command = args[0];

// Resolve alias
if (aliases[command]) {
    command = aliases[command];
}

function printUsage() {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                    AGENTIC SDLC CLI                           ║
║            3-Layer Brain Architecture Control                 ║
╚═══════════════════════════════════════════════════════════════╝

Usage: agentic-sdlc <command> [args]

╭─────────────────────────────────────────────────────────────────╮
│ LAYER 1: CORE                                                   │
├─────────────────────────────────────────────────────────────────┤
│  brain       Brain system management & state control            │
│  learn       Self-learning engine (Neo4j integration)           │
│  research    Research agent for deep investigation              │
╰─────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────╮
│ LAYER 2: INTELLIGENCE                                           │
├─────────────────────────────────────────────────────────────────┤
│  score         Score input/output quality                       │
│  score-input   Score input request quality                      │
│  score-output  Score output/response quality                    │
│  route         Route to appropriate workflow                    │
│  route-agent   Route to appropriate AI agent/role               │
│  rules         Evaluate routing rules                           │
│  monitor       Monitor system & detect violations               │
│  observe       Alias for monitor                                │
│  check-rules   Validate rule compliance                         │
│  audit         View audit logs                                  │
╰─────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────╮
│ LAYER 3: INFRASTRUCTURE                                         │
├─────────────────────────────────────────────────────────────────┤
│  release     Manage releases & version bumping                  │
│  workflow    Run workflows (cycle, orchestrator, debug, etc.)   │

│  validate    Validate system configuration                      │
│  health      Check system health                                │
│  setup       Initialize project                                 │

│  mcp         MCP (Model Context Protocol) management            │
│  run         Run arbitrary Python script                        │
╰─────────────────────────────────────────────────────────────────╯

Examples:
  agentic-sdlc brain status              # Check brain status
  agentic-sdlc score --score "Add login" # Score input quality
  agentic-sdlc route --route "fix bug"   # Get workflow recommendation
  agentic-sdlc monitor --status          # Check monitor status
  agentic-sdlc release --preview         # Preview release changes
  agentic-sdlc workflow cycle            # Run cycle workflow
  agentic-sdlc run tools/brain/judge.py  # Run any Python script

Aliases: l2=layer2, wf=workflow, s=score, r=route, m=monitor, b=brain
`);
}

if (!command || command === '--help' || command === '-h') {
    printUsage();
    process.exit(command ? 0 : 1);
}

let scriptPath = commands[command];
let scriptArgs = args.slice(1);

// Special handling for layer2 namespace
if (command === 'layer2') {
    const sub = args[1];
    if (!sub) {
        console.log(`
Layer 2 (Intelligence) Commands:
  scorer         Input/output quality scoring
  ab_test        A/B testing engine
  self_learning  Pattern recognition & improvement
  artifact_gen   Artifact generation
  router         Workflow & agent routing
  proxy          Model cost optimization
  task_manager   Kanban-style task management
  monitor        Compliance monitoring
  performance    Flow optimization

Usage: agentic-sdlc layer2 <component> [args]
Example: agentic-sdlc layer2 scorer --score "your text"
`);
        process.exit(0);
    }
    scriptPath = `tools/layer2/${sub}/__init__.py`;
    scriptArgs = args.slice(2);
}

// Special handling for workflows
if (command === 'workflow') {
    const sub = args[1];
    if (sub) {
        scriptPath = `tools/workflows/${sub}.py`;
        scriptArgs = args.slice(2);
    } else {
        console.error("Please specify a workflow (e.g., cycle, housekeeping)");
        console.log("Available: cycle, orchestrator, debug, refactor, review, release, emergency, housekeeping");
        process.exit(1);
    }
}

// Special handling for 'run' command
if (command === 'run') {
    if (args.length < 2) {
        console.error("Usage: agentic-sdlc run <script_path> [args]");
        process.exit(1);
    }
    scriptPath = args[1];
    scriptArgs = args.slice(2);
}

if (!scriptPath) {
    console.error(`Unknown command: ${command}`);
    console.log("Run 'agentic-sdlc --help' for usage information.");
    process.exit(1);
}

const fullPath = join(rootDir, scriptPath);

if (!fs.existsSync(fullPath)) {
    console.error(`Script not found: ${scriptPath}`);
    console.log(`Full path: ${fullPath}`);
    process.exit(1);
}

const pythonProcess = spawn('python', [fullPath, ...scriptArgs], {
    stdio: 'inherit',
    cwd: rootDir // Execute from project root
});

pythonProcess.on('exit', (code) => {
    process.exit(code ?? 0);
});

pythonProcess.on('error', (err) => {
    console.error('Failed to start python process:', err);
    process.exit(1);
});
