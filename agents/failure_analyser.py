import anthropic
import argparse
import json
import os

SYSTEM_PROMPT = """You are a senior QA engineer analysing automated test failures.

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


def parse_report(report_path: str) -> list:
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


def build_summary(failures: list) -> list:
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


def analyse(report_path: str) -> str:
    print(f"\n📋 Reading report: {report_path}")
    failures = parse_report(report_path)

    if not failures:
        return "✅ No failures — all tests passed!"

    print(f"❌ Found {len(failures)} failure(s). Sending to Claude...\n")
    print("─" * 60)

    client = anthropic.Anthropic()
    summary = build_summary(failures)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Analyse these failures:\n\n{summary}"}
        ]
    )

    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Analyse Playwright failures using Claude")
    parser.add_argument("--report", required=True, help="Path to Playwright JSON report")
    parser.add_argument("--output", default=None, help="Optional file to save analysis")
    args = parser.parse_args()

    result = analyse(args.report)
    print(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"\n✅ Saved to {args.output}")


if __name__ == "__main__":
    main()
