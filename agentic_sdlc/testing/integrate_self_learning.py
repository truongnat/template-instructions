"""
Self-Learning Integration - Feed test results to the learning system
Extracts patterns from workflow test results to improve future execution.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


def integrate_with_self_learning():
    """Feed test results to self-learning system."""
    
    print(f"\n{'='*60}")
    print("  SELF-LEARNING INTEGRATION")
    print(f"{'='*60}\n")
    
    # Load test results
    results_file = project_root / "test-results" / "scores" / "comprehensive-test-results.json"
    
    if not results_file.exists():
        print("❌ Test results not found")
        return 1
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Extract patterns
    print("📊 Analyzing test patterns...")
    
    patterns = extract_patterns(results)
    
    # Save learnings to knowledge base
    learnings_dir = project_root / "docs" / "knowledge-base" / "learnings"
    learnings_dir.mkdir(parents=True, exist_ok=True)
    
    learnings_file = learnings_dir / f"workflow-test-learnings-{datetime.now().strftime('%Y-%m-%d')}.json"
    
    with open(learnings_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "workflow-testing",
            "patterns": patterns,
            "recommendations": generate_recommendations(patterns)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Learnings saved to: {learnings_file}")
    
    # Generate learning report
    report = generate_learning_report(patterns)
    
    report_file = project_root / "docs" / "reports" / "learnings" / f"workflow-test-analysis-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Analysis report saved to: {report_file}")
    print("\n✅ Self-learning integration complete!")
    
    return 0


def extract_patterns(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract patterns from test results."""
    
    patterns = {
        "success_patterns": [],
        "failure_patterns": [],
        "improvement_areas": [],
        "high_performers": [],
        "low_performers": [],
        "category_performance": {}
    }
    
    # Categorize workflows
    categories = {
        'Intelligence': ['score', 'monitor', 'observe', 'ab', 'deep-search'],
        'Process': ['commit', 'cycle', 'orchestrator', 'planning', 'debug', 'emergency', 'explore', 'review', 'sprint', 'refactor'],
        'Support': ['docs', 'release', 'housekeeping', 'onboarding', 'worktree', 'brain'],
        'Utility': ['metrics', 'validate'],
        'Advanced': ['autogen']
    }
    
    # Analyze each result
    for result in results:
        workflow = result['workflow']
        status = result['status']
        compliance = result['compliance_score']
        quality = result['quality_score']
        
        # Find category
        category = "Unknown"
        for cat, workflows in categories.items():
            if workflow in workflows:
                category = cat
                break
        
        # Track category performance
        if category not in patterns['category_performance']:
            patterns['category_performance'][category] = {
                'total': 0,
                'passed': 0,
                'compliance_sum': 0,
                'quality_sum': 0
            }
        
        patterns['category_performance'][category]['total'] += 1
        patterns['category_performance'][category]['compliance_sum'] += compliance
        patterns['category_performance'][category]['quality_sum'] += quality
        
        if status == 'PASS':
            patterns['category_performance'][category]['passed'] += 1
        
        # Track high/low performers
        if compliance >= 90 and quality >= 8:
            patterns['high_performers'].append({
                'workflow': workflow,
                'compliance': compliance,
                'quality': quality,
                'pattern': 'High compliance + High quality'
            })
        elif compliance < 80 or quality < 7:
            patterns['low_performers'].append({
                'workflow': workflow,
                'compliance': compliance,
                'quality': quality,
                'pattern': 'Below target metrics'
            })
        
        # Extract success patterns
        if status == 'PASS':
            patterns['success_patterns'].append({
                'workflow': workflow,
                'key_factors': [
                    f"Compliance: {compliance}%",
                    f"Quality: {quality}/10"
                ]
            })
        else:
            patterns['failure_patterns'].append({
                'workflow': workflow,
                'issues': result.get('note', 'Script execution issues'),
                'compliance': compliance,
                'quality': quality
            })
    
    # Calculate category averages
    for cat, data in patterns['category_performance'].items():
        if data['total'] > 0:
            data['avg_compliance'] = data['compliance_sum'] / data['total']
            data['avg_quality'] = data['quality_sum'] / data['total']
            data['pass_rate'] = (data['passed'] / data['total']) * 100
    
    # Identify improvement areas
    for cat, data in patterns['category_performance'].items():
        if data.get('avg_compliance', 100) < 85:
            patterns['improvement_areas'].append({
                'category': cat,
                'metric': 'compliance',
                'current': data['avg_compliance'],
                'target': 85
            })
        if data.get('avg_quality', 10) < 7.5:
            patterns['improvement_areas'].append({
                'category': cat,
                'metric': 'quality',
                'current': data['avg_quality'],
                'target': 7.5
            })
    
    return patterns


def generate_recommendations(patterns: Dict[str, Any]) -> List[str]:
    """Generate recommendations from patterns."""
    
    recommendations = []
    
    # High performer recommendations
    if patterns['high_performers']:
        recommendations.append(
            f"✅ {len(patterns['high_performers'])} workflows are high performers - use as reference for others"
        )
    
    # Low performer recommendations
    for item in patterns['low_performers']:
        recommendations.append(
            f"❗ Fix /{item['workflow']}: compliance={item['compliance']}%, quality={item['quality']}/10"
        )
    
    # Category-level recommendations
    for area in patterns['improvement_areas']:
        recommendations.append(
            f"📈 Improve {area['category']} {area['metric']}: {area['current']:.1f} → {area['target']}"
        )
    
    # General recommendations
    if len(patterns['failure_patterns']) == 0:
        recommendations.append("🎉 All workflows passing - consider expanding test coverage")
    else:
        recommendations.append(f"⚠️ {len(patterns['failure_patterns'])} workflows need attention")
    
    return recommendations


def generate_learning_report(patterns: Dict[str, Any]) -> str:
    """Generate markdown learning report."""
    
    report = f"""# Workflow Test Analysis & Learnings

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Pattern Analysis

### Category Performance

| Category | Total | Passed | Pass Rate | Avg Compliance | Avg Quality |
|----------|-------|--------|-----------|----------------|-------------|
"""
    
    for cat, data in patterns['category_performance'].items():
        report += f"| {cat} | {data['total']} | {data['passed']} | {data.get('pass_rate', 0):.1f}% | {data.get('avg_compliance', 0):.1f}% | {data.get('avg_quality', 0):.1f}/10 |\n"
    
    report += "\n### 🌟 High Performers\n\n"
    
    if patterns['high_performers']:
        for item in patterns['high_performers']:
            report += f"- **/{item['workflow']}**: Compliance {item['compliance']}%, Quality {item['quality']}/10\n"
    else:
        report += "No high performers identified.\n"
    
    report += "\n### ⚠️ Low Performers\n\n"
    
    if patterns['low_performers']:
        for item in patterns['low_performers']:
            report += f"- **/{item['workflow']}**: Compliance {item['compliance']}%, Quality {item['quality']}/10\n"
    else:
        report += "No low performers identified.\n"
    
    report += "\n### 📈 Improvement Areas\n\n"
    
    if patterns['improvement_areas']:
        for area in patterns['improvement_areas']:
            report += f"- **{area['category']} {area['metric']}**: {area['current']:.1f} → {area['target']}\n"
    else:
        report += "All metrics meet targets.\n"
    
    report += "\n## 💡 Recommendations\n\n"
    
    recommendations = generate_recommendations(patterns)
    for rec in recommendations:
        report += f"- {rec}\n"
    
    report += "\n## 🔄 Self-Learning Actions\n\n"
    report += "1. ✅ Patterns extracted and stored in knowledge base\n"
    report += "2. ✅ High performers identified for reference\n"
    report += "3. ✅ Low performers flagged for improvement\n"
    report += "4. ✅ Recommendations generated for team review\n"
    
    report += "\n## 📁 Artifacts\n\n"
    report += "- Learnings JSON: `docs/knowledge-base/learnings/workflow-test-learnings-*.json`\n"
    report += "- Compliance Reports: `test-results/reports/compliance/*.md`\n"
    report += "- Test Results: `test-results/scores/comprehensive-test-results.json`\n"
    
    return report


def main():
    """Main entry point."""
    return integrate_with_self_learning()


if __name__ == '__main__':
    sys.exit(main())
