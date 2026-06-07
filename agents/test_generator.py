import anthropic
import argparse

SYSTEM_PROMPT = """You are a senior QA engineer. Generate structured test cases from user stories.

For every user story, generate test cases covering:
1. Happy path
2. Negative tests
3. Edge cases
4. Security considerations

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


def generate_test_cases(user_story: str) -> str:
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
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
