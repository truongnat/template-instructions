#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Test for Judge/Scorer feature
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_sdlc.intelligence.judge import Judge

def test_scorer():
    print("🧪 Running Standalone Scorer Test...")
    
    # Use a temporary scores file
    test_scores_file = Path("test_scores.json")
    if test_scores_file.exists():
        test_scores_file.unlink()
        
    judge = Judge(scores_file=test_scores_file)

    # 1. Test Code Scoring
    print("  - Testing code scoring...")
    temp_code = Path("temp_test_code.py")
    temp_code.write_text("""
import os
import sys

def hello_world():
    \"\"\"A docstring\"\"\"
    print("Hello World")

if __name__ == "__main__":
    hello_world()
""", encoding='utf-8')
    
    res_code = judge.score_code(str(temp_code))
    print(f"    Code Score: {res_code.final_score}/10 (Passed: {res_code.passed})")
    assert res_code.final_score > 5
    assert res_code.file_type == "code"
    
    # Test low quality code
    low_code = Path("low_quality.py")
    low_code.write_text("pass", encoding='utf-8')
    res_low = judge.score_code(str(low_code))
    print(f"    Low Code Score: {res_low.final_score}/10 (Passed: {res_low.passed})")
    assert res_low.final_score < 7 # Structure will be low

    # 2. Test Report Scoring
    print("  - Testing report scoring...")
    temp_report = Path("temp_test_report.md")
    temp_report.write_text("""
# Project Report
## Problem
We need a scorer.
## Solution
Implement a Judge class.
## Results
It works well.
## Next Steps
Optimize weights.
#tag1 #tag2
[Source](http://example.com)
""", encoding='utf-8')
    
    res_report = judge.score_report(str(temp_report))
    print(f"    Report Score: {res_report.final_score}/10 (Passed: {res_report.passed})")
    assert res_report.final_score > 7
    assert res_report.file_type == "report"

    # 3. Test A/B Test Scoring
    print("  - Testing A/B test scoring...")
    ab_result = {
        "test_id": "test-123",
        "confidence": 0.85,
        "option_a": {"votes": 10},
        "option_b": {"votes": 5},
        "kb_insights": ["Insight 1"],
        "memgraph_related": ["Node 1"]
    }
    res_ab = judge.score_ab_test(ab_result)
    print(f"    AB Test Score: {res_ab.final_score}/10 (Passed: {res_ab.passed})")
    assert res_ab.final_score > 8

    # 4. Verify Persistence
    print("  - Testing persistence...")
    assert test_scores_file.exists()
    with open(test_scores_file, 'r') as f:
        data = json.load(f)
        assert data["totalReviews"] >= 3
        print(f"    Total reviews persisted: {data['totalReviews']}")

    # Cleanup
    for p in [temp_code, low_code, temp_report, test_scores_file]:
        if p.exists():
            p.unlink()

    print("\n✅ All scorer tests passed!")

if __name__ == "__main__":
    test_scorer()
