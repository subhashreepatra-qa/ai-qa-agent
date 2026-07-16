import argparse
import os
import sys

import anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.qa_utils import (
    CLAUDE_MODEL,
    FAILED_TEST_ANALYSIS_SYSTEM_PROMPT,
    build_summary,
    parse_playwright_report,
)


def analyse(report_path: str) -> str:
    print(f"\n📋 Reading report: {report_path}")
    failures = parse_playwright_report(report_path)

    if not failures:
        return "✅ No failures — all tests passed!"

    print(f"❌ Found {len(failures)} failure(s). Sending to Claude...\n")
    print("─" * 60)

    client = anthropic.Anthropic()
    summary = build_summary(failures)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=FAILED_TEST_ANALYSIS_SYSTEM_PROMPT,
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
