"""
Custom Bandit Plugin: Kovel Privilege Leak Detection

Checks for patterns that could leak privileged attorney-client
communications in CounselConduit.

B901: Detects logging of session transcript content
B902: Detects unprotected export of privileged data
B903: Detects missing Kovel attestation checks
"""

import ast
import bandit
from bandit.core import issue as b_issue
from bandit.core import test_properties as test_props


@test_props.checks("Call")
@test_props.test_id("B901")
def kovel_transcript_leak(context):
    """B901: Detect logging of privileged transcript content."""
    call_name = context.call_function_name_qual
    log_functions = [
        "logging.info",
        "logging.debug",
        "logging.warning",
        "logger.info",
        "logger.debug",
        "logger.warning",
        "print",
    ]
    if call_name in log_functions:
        for arg in context.call_args:
            if isinstance(arg, str) and any(kw in arg.lower() for kw in ["transcript", "session_data", "privileged", "kovel"]):
                return b_issue.Issue(
                    severity=b_issue.HIGH,
                    confidence=b_issue.MEDIUM,
                    cwe=b_issue.Cwe.INFORMATION_EXPOSURE,
                    text="Possible logging of privileged Kovel session data. Privileged communications must never appear in logs.",
                    lineno=context.node.lineno,
                )


@test_props.checks("Call")
@test_props.test_id("B902")
def kovel_unprotected_export(context):
    """B902: Detect export of data without privilege check."""
    export_functions = [
        "json.dumps",
        "json.dump",
        "csv.writer",
        "to_json",
        "to_csv",
        "to_dict",
    ]
    call_name = context.call_function_name_qual
    if call_name in export_functions:
        # Check if there's a privilege_check in the same scope
        parent = context.node
        while hasattr(parent, "parent"):
            parent = parent.parent
            if isinstance(parent, ast.FunctionDef):
                func_source = ast.dump(parent)
                if "privilege_check" not in func_source and "kovel_attestation" not in func_source:
                    return b_issue.Issue(
                        severity=b_issue.MEDIUM,
                        confidence=b_issue.LOW,
                        cwe=b_issue.Cwe.INFORMATION_EXPOSURE,
                        text="Data export without privilege_check() or kovel_attestation(). "
                        "All exports in CounselConduit must verify privilege status.",
                        lineno=context.node.lineno,
                    )
                break
