#!/usr/bin/env pwsh
# File Naming Standardization Script
# Renames files to follow project conventions:
# - Documentation: UPPERCASE-WITH-HYPHENS.md
# - Code: lowercase_with_underscores.py/js
# - Config: lowercase-with-hyphens.json

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "File Naming Standardization" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$renamedCount = 0
$errorCount = 0

function Rename-CaseSensitive {
    param(
        [string]$OldPath,
        [string]$NewName
    )
    
    if (-not (Test-Path $OldPath)) {
        Write-Host "  ⚠️  File not found: $OldPath" -ForegroundColor Yellow
        return $false
    }
    
    $dir = Split-Path $OldPath -Parent
    $oldName = Split-Path $OldPath -Leaf
    $tempName = "$NewName.tmp"
    $tempPath = Join-Path $dir $tempName
    $finalPath = Join-Path $dir $NewName
    
    if ($oldName -eq $NewName) {
        Write-Host "  ✓ Already correct: $OldPath" -ForegroundColor Gray
        return $true
    }
    
    try {
        # Step 1: Rename to temp
        Rename-Item -Path $OldPath -NewName $tempName -Force -ErrorAction Stop
        
        # Step 2: Rename to final
        Rename-Item -Path $tempPath -NewName $NewName -Force -ErrorAction Stop
        
        Write-Host "  ✓ Renamed: $oldName → $NewName" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  ✗ Error: $oldName - $($_.Exception.Message)" -ForegroundColor Red
        
        # Cleanup temp file if exists
        if (Test-Path $tempPath) {
            Rename-Item -Path $tempPath -NewName $oldName -Force -ErrorAction SilentlyContinue
        }
        
        return $false
    }
}

Write-Host "Phase 1: Deleting backup files..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".agent/rules/global.md.bak") {
    Remove-Item ".agent/rules/global.md.bak" -Force
    Write-Host "  ✓ Deleted: global.md.bak" -ForegroundColor Green
}

Write-Host ""
Write-Host "Phase 2: Renaming .agent/ files..." -ForegroundColor Yellow
Write-Host ""

# .agent/
if (Rename-CaseSensitive ".agent/usage.md" "USAGE.md") { $renamedCount++ } else { $errorCount++ }

# .agent/ide-integration/
if (Rename-CaseSensitive ".agent/ide-integration/aider-commands.md" "AIDER-COMMANDS.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/ide-integration/cursor-rules.md" "CURSOR-RULES.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/ide-integration/github-copilot-instructions.md" "GITHUB-COPILOT-INSTRUCTIONS.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/ide-integration/windsurf-cascade.md" "WINDSURF-CASCADE.md") { $renamedCount++ } else { $errorCount++ }


# .agent/rules/
if (Rename-CaseSensitive ".agent/rules/artifacts.md" "ARTIFACTS.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/rules/auto-learning.md" "AUTO-LEARNING.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/rules/git-workflow.md" "GIT-WORKFLOW.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive ".agent/rules/global.md" "GLOBAL.md") { $renamedCount++ } else { $errorCount++ }

Write-Host ""
Write-Host "Phase 3: Renaming .github/ files..." -ForegroundColor Yellow
Write-Host ""

if (Rename-CaseSensitive ".github/copilot-instructions.md" "COPILOT-INSTRUCTIONS.md") { $renamedCount++ } else { $errorCount++ }

Write-Host ""
Write-Host "Phase 4: Renaming docs/ files..." -ForegroundColor Yellow
Write-Host ""

# docs/architecture/
if (Rename-CaseSensitive "docs/architecture/brain.md" "BRAIN.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive "docs/architecture/neo4j-learning-queries.md" "NEO4J-LEARNING-QUERIES.md") { $renamedCount++ } else { $errorCount++ }

# docs/reports/
if (Rename-CaseSensitive "docs/reports/comparison-leann-neo4j.md" "COMPARISON-LEANN-NEO4J.md") { $renamedCount++ } else { $errorCount++ }

# docs/setup/
if (Rename-CaseSensitive "docs/setup/github-management.md" "GITHUB-MANAGEMENT.md") { $renamedCount++ } else { $errorCount++ }

# docs/sprints/
if (Rename-CaseSensitive "docs/sprints/sprint-github-issues.md" "SPRINT-GITHUB-ISSUES.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive "docs/sprints/sprint-leann-integration.md" "SPRINT-LEANN-INTEGRATION.md") { $renamedCount++ } else { $errorCount++ }
if (Rename-CaseSensitive "docs/sprints/sprint-neo4j-brain.md" "SPRINT-NEO4J-BRAIN.md") { $renamedCount++ } else { $errorCount++ }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Standardization Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Files renamed: $renamedCount" -ForegroundColor Green
Write-Host "✗ Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review renamed files" -ForegroundColor White
Write-Host "2. Update any references in code/docs" -ForegroundColor White
Write-Host "3. Test all scripts still work" -ForegroundColor White
Write-Host "4. Commit changes" -ForegroundColor White
Write-Host ""
