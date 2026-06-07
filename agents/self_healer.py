import anthropic
import argparse
import os

SYSTEM_PROMPT = """You are a QA automation engineer specialising in Playwright test maintenance.

A test has broken because a CSS selector no longer matches any element.
You will be given the broken selector and the page HTML.

Suggest alternative selectors that are resilient to UI changes.
Always prefer in this order:
1. data-testid attributes
2. aria-label or role
3. visible text content
4. CSS classes (last resort)

Output format:

## Self-Healing Suggestions for: `[broken selector]`

**Why it likely broke**:
[explanation based on the HTML]

**Suggested alternatives** (best first):

1. `[selector]`
   - Type: data-testid | aria | role | text | CSS
   - Resilience: High | Medium | Low
   - Reason: [why this is a good choice]

2. `[selector]`
   - Type: ...
   - Resilience: ...
   - Reason: ...

(up to 4 suggestions)

**Playwright code snippet**:
```typescript
// Replace your broken locator with:
await page.locator('[best selector]').click();
```

**Prevention tip**: [one sentence on writing more resilient selectors]"""


def load_html(html_path: str) -> str:
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    with open(html_path) as f:
        html = f.read()

    # Truncate to avoid token limits — Claude only needs relevant section
    max_chars = 8000
    if len(html) > max_chars:
        print(f"⚠️  HTML truncated to {max_chars} chars")
        html = html[:max_chars] + "\n... [truncated]"

    return html


def suggest_alternatives(broken_selector: str, html: str) -> str:
    print(f"\n🔍 Broken selector: {broken_selector}")
    print("🤖 Asking Claude to suggest alternatives...\n")
    print("─" * 60)

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""The following selector has broken:

Broken selector: {broken_selector}

Page HTML:
```html
{html}
```

Suggest resilient alternative selectors."""
            }
        ]
    )

    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(
        description="Suggest self-healing selector alternatives using Claude"
    )
    parser.add_argument("--selector", required=True, help="The broken selector")
    parser.add_argument("--html", required=True, help="Path to HTML snapshot file")
    parser.add_argument("--output", default=None, help="Optional file to save suggestions")
    args = parser.parse_args()

    html = load_html(args.html)
    result = suggest_alternatives(args.selector, html)

    print(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"\n✅ Saved to {args.output}")


if __name__ == "__main__":
    main()
