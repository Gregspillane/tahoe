"""
Regression tests to prevent parameter reference bugs in the reconciliation pipeline.
This test specifically prevents the recurrence of 'original_google' parameter errors
that were fixed during the Google Speech → OpenAI migration.
"""

import pytest
import ast
import os
from pathlib import Path


class ParameterConsistencyChecker:
    """Checks for consistent parameter naming throughout the codebase."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reconciliation_dir = project_root / "reconciliation"
        
    def scan_for_deprecated_parameters(self) -> list:
        """Scan reconciliation code for deprecated Google Speech parameter references."""
        deprecated_patterns = [
            "original_google",
            "google_text", 
            "google_segment",
            "google_speech",
            "google_result",
            "google_confidence"
        ]
        
        violations = []
        
        for py_file in self.reconciliation_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                content = f.read()
                
            for pattern in deprecated_patterns:
                if pattern in content:
                    # Count occurrences and get line numbers
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if pattern in line and not line.strip().startswith('#'):
                            violations.append({
                                'file': str(py_file),
                                'line': line_num,
                                'pattern': pattern,
                                'content': line.strip()
                            })
                            
        return violations
    
    def check_openai_parameter_consistency(self) -> list:
        """Ensure OpenAI parameters are used consistently."""
        expected_patterns = [
            "original_openai",
            "openai_text",
            "openai_segment", 
            "openai_result",
            "openai_confidence"
        ]
        
        missing_patterns = []
        
        # Check gemini_client.py specifically
        gemini_file = self.reconciliation_dir / "gemini_client.py"
        if gemini_file.exists():
            with open(gemini_file, 'r') as f:
                content = f.read()
                
            # original_openai should appear in ReconciliationDecision usage
            if "original_openai" not in content:
                missing_patterns.append({
                    'file': str(gemini_file),
                    'missing_pattern': 'original_openai',
                    'issue': 'ReconciliationDecision should use original_openai parameter'
                })
                
        return missing_patterns


def test_no_deprecated_google_speech_parameters():
    """Test that no deprecated Google Speech parameters remain in reconciliation code."""
    project_root = Path(__file__).parent.parent.parent
    checker = ParameterConsistencyChecker(project_root)
    
    violations = checker.scan_for_deprecated_parameters()
    
    if violations:
        error_msg = "Found deprecated Google Speech parameter references:\n"
        for violation in violations:
            error_msg += f"  {violation['file']}:{violation['line']} - '{violation['pattern']}' in: {violation['content']}\n"
        error_msg += "\nThese should be updated to use OpenAI parameter names (e.g., original_google → original_openai)"
        
        pytest.fail(error_msg)


def test_openai_parameter_consistency():
    """Test that OpenAI parameters are used consistently throughout reconciliation code."""
    project_root = Path(__file__).parent.parent.parent
    checker = ParameterConsistencyChecker(project_root)
    
    missing_patterns = checker.check_openai_parameter_consistency()
    
    if missing_patterns:
        error_msg = "OpenAI parameter consistency issues found:\n"
        for issue in missing_patterns:
            error_msg += f"  {issue['file']} - {issue['issue']}\n"
        
        pytest.fail(error_msg)


def test_reconciliation_decision_dataclass():
    """Test that ReconciliationDecision dataclass has correct OpenAI field."""
    project_root = Path(__file__).parent.parent.parent
    gemini_file = project_root / "reconciliation" / "gemini_client.py"
    
    with open(gemini_file, 'r') as f:
        content = f.read()
    
    # Parse the AST to check the ReconciliationDecision dataclass
    tree = ast.parse(content)
    
    reconciliation_decision_found = False
    has_original_openai = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ReconciliationDecision":
            reconciliation_decision_found = True
            
            # Check if it has original_openai field
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if item.target.id == "original_openai":
                        has_original_openai = True
    
    assert reconciliation_decision_found, "ReconciliationDecision dataclass not found"
    assert has_original_openai, "ReconciliationDecision should have original_openai field, not original_google"


def test_method_signatures_use_openai_params():
    """Test that method signatures use OpenAI parameter names consistently."""
    project_root = Path(__file__).parent.parent.parent
    gemini_file = project_root / "reconciliation" / "gemini_client.py"
    
    with open(gemini_file, 'r') as f:
        content = f.read()
    
    # Check specific method signatures
    required_signatures = [
        "def _build_reconciliation_prompt",
        "def _parse_gemini_response"
    ]
    
    for signature in required_signatures:
        if signature in content:
            # Find the method definition
            start_idx = content.find(signature)
            # Find the end of the method signature - look for closing parenthesis then colon
            # This handles multiline method signatures correctly
            paren_count = 0
            method_end = start_idx
            for i, char in enumerate(content[start_idx:], start_idx):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        # Find the colon after this closing parenthesis
                        method_end = content.find(':', i)
                        break
            method_signature = content[start_idx:method_end]
            
            assert "original_google" not in method_signature, f"{signature} still references original_google parameter"
            
            # For _parse_gemini_response, ensure it has original_openai
            if "_parse_gemini_response" in signature:
                assert "original_openai" in method_signature, f"{signature} should have original_openai parameter"


if __name__ == "__main__":
    # Allow running this test directly for debugging
    pytest.main([__file__, "-v"])