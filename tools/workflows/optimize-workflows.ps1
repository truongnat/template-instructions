# Workflow Optimization Automation Script
# This script automates the remaining consolidation and reorganization tasks

Write-Host "🚀 Starting Workflow Optimization Automation..." -ForegroundColor Green

# Phase 2: Continue with remaining merges

## Merge auto.md content into orchestrator.md
Write-Host "`n📝 Merging auto.md → orchestrator.md..." -ForegroundColor Yellow
if (Test-Path ".agent\workflows\auto.md") {
    $autoContent = Get-Content ".agent\workflows\auto.md" -Raw
    $orchContent = Get-Content ".agent\workflows\orchestrator.md" -Raw
    
    # Append unique content from auto.md
    Add-Content ".agent\workflows\orchestrator.md" "`n`n---`n`n## Automation Modes (from auto.md)`n`n"
    Add-Content ".agent\workflows\orchestrator.md" $autoContent
    
    Write-Host "✓ auto.md merged into orchestrator.md" -ForegroundColor Green
}

## Merge auto-learning-workflow.md into brain.md
Write-Host "`n📝 Merging auto-learning-workflow.md → brain.md..." -ForegroundColor Yellow
if (Test-Path ".agent\workflows\auto-learning-workflow.md") {
    $learningContent = Get-Content ".agent\workflows\auto-learning-workflow.md" -Raw
    $brainContent = Get-Content ".agent\workflows\brain.md" -Raw
    
    Add-Content ".agent\workflows\brain.md" "`n`n---`n`n## Automated Learning System`n`n"
    Add-Content ".agent\workflows\brain.md" $learningContent
    
    Write-Host "✓ auto-learning-workflow.md merged into brain.md" -ForegroundColor Green
}

## Merge cleanup files into housekeeping.md
Write-Host "`n📝 Merging cleanup.md → housekeeping.md..." -ForegroundColor Yellow
if (Test-Path ".agent\workflows\cleanup.md") {
    $cleanupContent = Get-Content ".agent\workflows\cleanup.md" -Raw  
    Add-Content ".agent\workflows\housekeeping.md" "`n`n---`n`n## Additional Cleanup Procedures`n`n"
    Add-Content ".agent\workflows\housekeeping.md" $cleanupContent
    Write-Host "✓ cleanup.md merged into housekeeping.md" -ForegroundColor Green
}

if (Test-Path ".agent\workflows\cleanup-quick-reference.md") {
    $quickRefContent = Get-Content ".agent\workflows\cleanup-quick-reference.md" -Raw
    # Add quick reference to top of housekeeping
    $hkContent = Get-Content ".agent\workflows\housekeeping.md" -Raw
    $newHkContent = "---`nQuick Reference:`n" + $quickRefContent + "`n---`n`n" + $hkContent
    Set-Content ".agent\workflows\housekeeping.md" $newHkContent
    Write-Host "✓ cleanup-quick-reference.md added to housekeeping.md header" -ForegroundColor Green
}

## Merge documentation-updates.md into release.md
Write-Host "`n📝 Merging documentation-updates.md → release.md..." -ForegroundColor Yellow
if (Test-Path ".agent\workflows\documentation-updates.md") {
    $docsContent = Get-Content ".agent\workflows\documentation-updates.md" -Raw
    Add-Content ".agent\workflows\release.md" "`n`n---`n`n## Documentation Update Procedures`n`n"
    Add-Content ".agent\workflows\release.md" $docsContent
    Write-Host "✓ documentation-updates.md merged into release.md" -ForegroundColor Green
}

# Phase 3: Reorganization

Write-Host "`n`n🏗️  PHASE 3: Creating New Directory Structure..." -ForegroundColor Cyan

## Create new directory structure
Write-Host "`nCreating workflow hierarchy..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path ".agent\workflows\core" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent\workflows\process" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent\workflows\support" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent\workflows\utilities" -Force | Out-Null
Write-Host "✓ Created core/, process/, support/, utilities/" -ForegroundColor Green

## Move core role workflows
Write-Host "`nMoving core role workflows..." -ForegroundColor Yellow
$coreRoles = @("pm.md", "ba.md", "sa.md", "uiux.md", "dev.md", "devops.md", "tester.md", "seca.md")
foreach ($role in $coreRoles) {
    if (Test-Path ".agent\workflows\$role") {
        Move-Item ".agent\workflows\$role" ".agent\workflows\core\" -Force
        Write-Host "  ✓ Moved $role → core/" -ForegroundColor Green
    }
}

## Move process workflows
Write-Host "`nMoving process workflows..." -ForegroundColor Yellow
$processWorkflows = @("orchestrator.md", "cycle.md", "explore.md", "emergency.md", "sprint.md")
foreach ($workflow in $processWorkflows) {
    if (Test-Path ".agent\workflows\$workflow") {
        Move-Item ".agent\workflows\$workflow" ".agent\workflows\process\" -Force
        Write-Host "  ✓ Moved $workflow → process/" -ForegroundColor Green
    }
}

## Move support workflows
Write-Host "`nMoving support workflows..." -ForegroundColor Yellow
$supportWorkflows = @("compound.md", "brain.md", "route.md", "release.md", "housekeeping.md")
foreach ($workflow in $supportWorkflows) {
    if (Test-Path ".agent\workflows\$workflow") {
        Move-Item ".agent\workflows\$workflow" ".agent\workflows\support\" -Force
        Write-Host "  ✓ Moved $workflow → support/" -ForegroundColor Green
    }
}

## Move utility workflows
Write-Host "`nMoving utility workflows..." -ForegroundColor Yellow
$utilityWorkflows = @("validate.md", "metrics.md")
foreach ($workflow in $utilityWorkflows) {
    if (Test-Path ".agent\workflows\$workflow") {
        Move-Item ".agent\workflows\$workflow" ".agent\workflows\utilities\" -Force
        Write-Host "  ✓ Moved $workflow → utilities/" -ForegroundColor Green
    }
}

# Archive deleted workflows
Write-Host "`n`n🗄️  Archiving consolidated/deleted workflows..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path ".agent\archive\workflows-consolidated-20260103" -Force | Out-Null

$toArchive = @(
    "po.md", "qa.md", "reporter.md", "stakeholder.md",
    "auto.md", "auto-learning-workflow.md",
    "cleanup.md", "cleanup-quick-reference.md",  
    "documentation-updates.md", "research.md", "kb-search.md",
    "git-kb-integration.md", "kb-hooks-setup.md"
)

foreach ($file in $toArchive) {
    if (Test-Path ".agent\workflows\$file") {
        Move-Item ".agent\workflows\$file" ".agent\archive\workflows-consolidated-20260103\" -Force
        Write-Host "  ✓ Archived $file" -ForegroundColor DarkYellow
    }
}

# Create archive README
@"
# Archived Workflows (2026-01-03)

These workflows were consolidated or deleted during optimization.

## Merged into Other Workflows:
- po.md → pm.md (Product Owner duties now in PM)
- qa.md → tester.md (QA duties now in Tester Phase 1)
- reporter.md → pm.md (Reporter duties now in PM)
- stakeholder.md → pm.md (Stakeholder liaison now in PM)
- auto.md → orchestrator.md (Automation in Orchestrator)
- auto-learning-workflow.md → brain.md (Auto-learning in Brain)
- cleanup.md → housekeeping.md (Cleanup in Housekeeping)
- cleanup-quick-reference.md → housekeeping.md (Quick ref in header)
- documentation-updates.md → release.md (Docs updates in Release)

## Deleted (functionality moved elsewhere):
- research.md → embedded in all role workflows (MANDATORY research step)
- kb-search.md → trivial wrapper, examples in compound.md

## Moved to Setup:
- git-kb-integration.md → docs/setup/ (setup guide)
- kb-hooks-setup.md → docs/setup/ (setup guide)

See: docs/analysis/Workflows-Deep-Analysis-2026-01-03.md
"@ | Set-Content ".agent\archive\workflows-consolidated-20260103\README.md"

# Move setup guides
Write-Host "`n`n📚 Moving setup guides to docs/setup/..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "docs\setup" -Force | Out-Null

if (Test-Path ".agent\archive\workflows-consolidated-20260103\git-kb-integration.md") {
    Move-Item ".agent\archive\workflows-consolidated-20260103\git-kb-integration.md" "docs\setup\" -Force
    Write-Host "  ✓ Moved git-kb-integration.md → docs/setup/" -ForegroundColor Green
}

if (Test-Path ".agent\archive\workflows-consolidated-20260103\kb-hooks-setup.md") {
    Move-Item ".agent\archive\workflows-consolidated-20260103\kb-hooks-setup.md" "docs\setup\" -Force
    Write-Host "  ✓ Moved kb-hooks-setup.md → docs/setup/" -ForegroundColor Green
}

# Count results
Write-Host "`n`n📊 RESULTS:" -ForegroundColor Magenta
Write-Host "─────────────────────────────────────" -ForegroundColor DarkGray

$coreCount = (Get-ChildItem ".agent\workflows\core\*.md" -ErrorAction SilentlyContinue).Count
$processCount = (Get-ChildItem ".agent\workflows\process\*.md" -ErrorAction SilentlyContinue).Count
$supportCount = (Get-ChildItem ".agent\workflows\support\*.md" -ErrorAction SilentlyContinue).Count
$utilityCount = (Get-ChildItem ".agent\workflows\utilities\*.md" -ErrorAction SilentlyContinue).Count
$totalNew = $coreCount + $processCount + $supportCount + $utilityCount  
$archived = (Get-ChildItem ".agent\archive\workflows-consolidated-20260103\*.md" -ErrorAction SilentlyContinue).Count

Write-Host "Core Roles:      $coreCount workflows" -ForegroundColor Green
Write-Host "Processes:       $processCount workflows" -ForegroundColor Green
Write-Host "Support:         $supportCount workflows" -ForegroundColor Green
Write-Host "Utilities:       $utilityCount workflows" -ForegroundColor Green
Write-Host "─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "TOTAL:           $totalNew workflows" -ForegroundColor Cyan
Write-Host "Archived:        $archived files" -ForegroundColor DarkYellow
Write-Host "Reduction:       $(33 - $totalNew) workflows ($(([math]::Round((33 - $totalNew) / 33 * 100)))%)" -ForegroundColor Magenta

Write-Host "`n✅ Workflow optimization automation complete!" -ForegroundColor Green
Write-Host "`n📁 New structure:" -ForegroundColor Cyan
Write-Host ".agent/workflows/" -ForegroundColor White
Write-Host "  ├── core/        ($coreCount files)" -ForegroundColor Gray
Write-Host "  ├── process/     ($processCount files)" -ForegroundColor Gray
Write-Host "  ├── support/     ($supportCount files)" -ForegroundColor Gray
Write-Host "  └── utilities/   ($utilityCount files)" -ForegroundColor Gray

Write-Host "`n🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Create INDEX.md files for each directory"
Write-Host "2. Create DECISION-TREE.md"
Write-Host "3. Create main README.md"
Write-Host "4. Update references in global.md"
Write-Host "5. Run validation"
