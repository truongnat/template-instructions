"""
Generate Individual Workflow Compliance Reports
Creates detailed compliance reports for each of the 24 workflows.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))


def generate_individual_reports():
    """Generate individual compliance reports for each workflow."""
    
    # Load comprehensive test results
    results_file = project_root / "test-results" / "scores" / "comprehensive-test-results.json"
    
    if not results_file.exists():
        print("❌ Comprehensive test results not found. Run tests first.")
        return 1
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Create compliance reports directory
    compliance_dir = project_root / "test-results" / "reports" / "compliance"
    compliance_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("  GENERATING INDIVIDUAL COMPLIANCE REPORTS")
    print(f"{'='*60}\n")
    
    # Group results by workflow
    workflows = {}
    for result in results:
        workflow = result['workflow']
        if workflow not in workflows:
            workflows[workflow] = []
        workflows[workflow].append(result)
    
    # Generate report for each workflow
    for workflow_name, workflow_results in workflows.items():
        report = generate_workflow_report(workflow_name, workflow_results)
        
        # Save report
        report_file = compliance_dir / f"{workflow_name}-compliance.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Generated: {workflow_name}-compliance.md")
    
    print(f"\n✅ Generated {len(workflows)} individual compliance reports")
    print(f"📁 Location: {compliance_dir}")
    
    return 0


def generate_workflow_report(workflow_name, results):
    """Generate compliance report for a single workflow."""
    
    # Calculate aggregate scores
    avg_compliance = sum(r['compliance_score'] for r in results) / len(results)
    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    
    all_passed = all(r['status'] == 'PASS' for r in results)
    any_partial = any(r['status'] == 'PARTIAL' for r in results)
    any_failed = any(r['status'] == 'FAIL' for r in results)
    
    if all_passed:
        overall_status = "✅ PASS"
    elif any_failed:
        overall_status = "❌ FAIL"
    else:
        overall_status = "⚠️ PARTIAL"
    
    # Generate report
    report = f"""# Workflow Compliance Report: /{workflow_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Status**: {overall_status}  
**Test Cases**: {len(results)}

## 📊 Summary

- **Average Compliance**: {avg_compliance:.1f}%
- **Average Quality**: {avg_quality:.1f}/10
- **Tests Passed**: {sum(1 for r in results if r['status'] == 'PASS')}/{len(results)}
- **Tests Partial**: {sum(1 for r in results if r['status'] == 'PARTIAL')}/{len(results)}
- **Tests Failed**: {sum(1 for r in results if r['status'] == 'FAIL')}/{len(results)}

## 🧪 Test Cases

"""
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result['status'] == "PASS" else "⚠️" if result['status'] == "PARTIAL" else "❌"
        
        report += f"""### {i}. {result['test_case']} {status_icon}

**Description**: {result['description']}  
**Status**: {result['status']}  
**Compliance Score**: {result['compliance_score']}%  
**Quality Score**: {result['quality_score']}/10  
**Timestamp**: {result['timestamp']}

"""
        
        if 'note' in result:
            report += f"**Note**: {result['note']}\n\n"
        
        if 'details' in result and result['details']:
            report += "**Details**:\n"
            for key, value in result['details'].items():
                report += f"- {key}: {value}\n"
            report += "\n"
        
        if 'output' in result:
            report += f"**Output**: {result['output'][:200]}...\n\n"
    
    # Recommendations
    report += "## 💡 Recommendations\n\n"
    
    if any_partial or any_failed:
        report += "### Issues to Address\n\n"
        for result in results:
            if result['status'] in ['PARTIAL', 'FAIL']:
                report += f"- **{result['test_case']}**: "
                if 'note' in result:
                    report += f"{result['note']}\n"
                else:
                    report += f"Improve compliance (current: {result['compliance_score']}%) and quality (current: {result['quality_score']}/10)\n"
    
    if avg_compliance < 85:
        report += f"\n- Increase compliance score from {avg_compliance:.1f}% to >= 85%\n"
    
    if avg_quality < 7.5:
        report += f"- Improve quality score from {avg_quality:.1f}/10 to >= 7.5/10\n"
    
    if all_passed and avg_compliance >= 85 and avg_quality >= 7.5:
        report += "✅ All tests passed with excellent scores. No improvements needed.\n"
    
    # Next Steps
    report += "\n## 🚀 Next Steps\n\n"
    
    if any_partial or any_failed:
        report += "1. Fix identified issues in PARTIAL/FAIL test cases\n"
        report += "2. Re-run tests to verify improvements\n"
        report += "3. Update workflow definition if needed\n"
    else:
        report += "1. ✅ Workflow is production-ready\n"
        report += "2. Consider end-to-end testing with full AI agent execution\n"
        report += "3. Monitor workflow performance in production\n"
    
    return report


def main():
    """Main entry point."""
    return generate_individual_reports()


if __name__ == '__main__':
    sys.exit(main())
