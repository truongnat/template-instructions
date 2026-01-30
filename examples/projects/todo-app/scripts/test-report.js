#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * Test Report Generator
 * Combines backend and frontend test coverage into a unified report
 */

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function readCoverageSummary(coveragePath) {
  try {
    const summaryPath = path.join(coveragePath, 'coverage-summary.json');
    if (!fs.existsSync(summaryPath)) {
      return null;
    }
    return JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
  } catch (error) {
    console.error(`Error reading coverage from ${coveragePath}:`, error.message);
    return null;
  }
}

function getColorForPercentage(percentage) {
  if (percentage >= 80) return COLORS.green;
  if (percentage >= 70) return COLORS.yellow;
  return COLORS.red;
}

function formatPercentage(value) {
  const percentage = value.pct || 0;
  const color = getColorForPercentage(percentage);
  return `${color}${percentage.toFixed(2)}%${COLORS.reset}`;
}

function printCoverageTable(title, coverage) {
  if (!coverage || !coverage.total) {
    console.log(`\n${COLORS.yellow}No coverage data available for ${title}${COLORS.reset}`);
    return;
  }

  const { total } = coverage;
  
  console.log(`\n${COLORS.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLORS.reset}`);
  console.log(`${COLORS.blue}${title}${COLORS.reset}`);
  console.log(`${COLORS.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLORS.reset}`);
  
  console.log(`\n  Metric          Coverage    Covered/Total`);
  console.log(`  ────────────────────────────────────────────────────────`);
  console.log(`  Statements      ${formatPercentage(total.statements)}     ${total.statements.covered}/${total.statements.total}`);
  console.log(`  Branches        ${formatPercentage(total.branches)}     ${total.branches.covered}/${total.branches.total}`);
  console.log(`  Functions       ${formatPercentage(total.functions)}     ${total.functions.covered}/${total.functions.total}`);
  console.log(`  Lines           ${formatPercentage(total.lines)}     ${total.lines.covered}/${total.lines.total}`);
}

function calculateOverallScore(backendCoverage, frontendCoverage) {
  const scores = [];
  
  if (backendCoverage?.total) {
    const { total } = backendCoverage;
    const avg = (
      total.statements.pct +
      total.branches.pct +
      total.functions.pct +
      total.lines.pct
    ) / 4;
    scores.push(avg);
  }
  
  if (frontendCoverage?.total) {
    const { total } = frontendCoverage;
    const avg = (
      total.statements.pct +
      total.branches.pct +
      total.functions.pct +
      total.lines.pct
    ) / 4;
    scores.push(avg);
  }
  
  return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
}

function generateReport() {
  console.log(`\n${COLORS.cyan}╔════════════════════════════════════════════════════════════╗${COLORS.reset}`);
  console.log(`${COLORS.cyan}║${COLORS.reset}           ${COLORS.blue}📊 TODO APP TEST COVERAGE REPORT${COLORS.reset}           ${COLORS.cyan}║${COLORS.reset}`);
  console.log(`${COLORS.cyan}╚════════════════════════════════════════════════════════════╝${COLORS.reset}`);
  
  const backendCoverage = readCoverageSummary(path.join(__dirname, '../backend/coverage'));
  const frontendCoverage = readCoverageSummary(path.join(__dirname, '../frontend/coverage'));
  
  printCoverageTable('🔧 Backend Coverage (Jest)', backendCoverage);
  printCoverageTable('⚛️  Frontend Coverage (Vitest)', frontendCoverage);
  
  const overallScore = calculateOverallScore(backendCoverage, frontendCoverage);
  const scoreColor = getColorForPercentage(overallScore);
  
  console.log(`\n${COLORS.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLORS.reset}`);
  console.log(`${COLORS.blue}Overall Test Score:${COLORS.reset} ${scoreColor}${overallScore.toFixed(2)}%${COLORS.reset}`);
  console.log(`${COLORS.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLORS.reset}\n`);
  
  // Recommendations
  if (overallScore < 70) {
    console.log(`${COLORS.red}⚠️  Coverage is below threshold (70%). Consider adding more tests.${COLORS.reset}`);
  } else if (overallScore < 80) {
    console.log(`${COLORS.yellow}⚡ Good coverage! Aim for 80%+ for excellent quality.${COLORS.reset}`);
  } else {
    console.log(`${COLORS.green}✅ Excellent test coverage! Keep up the good work.${COLORS.reset}`);
  }
  
  console.log(`\n${COLORS.cyan}📁 Detailed Reports:${COLORS.reset}`);
  console.log(`   Backend:  todo-app/backend/coverage/index.html`);
  console.log(`   Frontend: todo-app/frontend/coverage/index.html\n`);
}

generateReport();
