import json
import os

CLAUDE_MODEL = "claude-sonnet-4-6"

TEST_CASE_GENERATION_SYSTEM_PROMPT = """You are a senior QA engineer. Generate structured test cases from user stories.

For every user story, generate test cases covering:
1. Happy path
2. Negative tests
3. Edge cases
4. Security considerations
5. Audit log consideration
6. User lock scenarios

Use this exact format for each test case:

### [TC-001] [Test case name]
- **Type**: Happy Path | Negative | Edge Case | Security
- **Preconditions**: [what must be true before the test]
- **Steps**:
  1. [step]
  2. [step]
- **Expected result**: [what should happen]
- **Priority**: High | Medium | Low

Generate between 4 and 8 test cases. No code — behaviour and outcomes only."""

FAILED_TEST_ANALYSIS_SYSTEM_PROMPT = """You are a senior QA engineer analysing automated test failures.

You will be given a summary of Playwright test failures. For each failure provide:

1. Plain English explanation — what went wrong in simple terms
2. Likely root causes — ordered by probability
3. Recommended next steps — concrete actions for the developer
4. Severity — Critical | High | Medium | Low

Format each failure exactly like this:

---
### ❌ [Test name]
**What happened**: [plain English]
**Likely causes**:
  1. [most likely]
  2. [second most likely]
**Next steps**:
  - [action 1]
  - [action 2]
**Severity**: [level] — [one sentence justification]
---

End with a SUMMARY section:
- Total failures
- Any common patterns
- One top recommendation for the team"""


def parse_playwright_report(report_path: str) -> list:
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Report not found: {report_path}")

    with open(report_path) as f:
        report = json.load(f)

    failures = []

    def walk_suites(suites):
        for suite in suites:
            # Walk nested suites recursively
            if suite.get("suites"):
                walk_suites(suite["suites"])
            # Check specs at this level
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    for result in test.get("results", []):
                        if result.get("status") in ("failed", "unexpected"):
                            error = result.get("error", {})
                            failures.append({
                                "test_name": spec.get("title", "Unknown"),
                                "error_message": error.get("message", "No message")[:300],
                                "stack_trace": error.get("stack", "")[:300]
                            })

    walk_suites(report.get("suites", []))
    return failures


def build_summary(failures: list) -> str:
    if not failures:
        return "No failures found."

    lines = [f"Total failures: {len(failures)}\n"]
    for i, f in enumerate(failures, 1):
        lines.append(f"""
Failure {i}:
  Test: {f['test_name']}
  Error: {f['error_message']}
  Stack: {f['stack_trace']}
""")
    return "\n".join(lines)
