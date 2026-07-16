import os
import sys
import argparse

import anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.qa_utils import CLAUDE_MODEL, TEST_CASE_GENERATION_SYSTEM_PROMPT


def generate_test_cases(user_story: str) -> str:
    client = anthropic.Anthropic()

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=TEST_CASE_GENERATION_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Generate test cases for this user story:\n\n{user_story}"}
        ]
    )

    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Generate test cases from a user story using Claude")
    parser.add_argument("--story", required=True, help="The user story")
    parser.add_argument("--output", default=None, help="Optional file to save output")
    args = parser.parse_args()

    print(f"\n🤖 Sending to Claude...\n")
    result = generate_test_cases(args.story)
    print(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"\n✅ Saved to {args.output}")


if __name__ == "__main__":
    main()
