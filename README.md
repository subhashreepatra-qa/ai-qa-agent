# AI-Powered QA Agent

A portfolio project demonstrating agentic AI testing using the Anthropic Claude API and Playwright.

Built to explore how AI can be embedded into a real QA workflow — from test generation to failure analysis to self-healing selectors.

---

## What It Does

| Agent | Input | Output |
|---|---|---|
| **Agent 1 — Test Generator** | User story (plain English) | Structured test cases |
| **Agent 2 — Failure Analyser** | Playwright JSON report | Plain English failure analysis |
| **Agent 3 — Self Healer** | Broken selector + page HTML | Resilient alternative selectors |

---

## Why I Built This

Traditional test automation has three pain points this project addresses:

- **Test authoring is slow** — QA engineers write every test case from scratch
- **Failure messages are cryptic** — stack traces aren't readable by developers or stakeholders
- **Selectors are brittle** — UI changes break tests silently

Each agent tackles one of these problems using Claude as the intelligence layer.

---
```
## Project Structure
ai-qa-agent/
├── agents/
│   ├── test_generator.py      # Agent 1 — generates test cases from user stories
│   ├── failure_analyser.py    # Agent 2 — analyses Playwright failures
│   └── self_healer.py         # Agent 3 — suggests resilient selectors
├── tests/
│   └── todo.spec.ts           # Playwright test suite (TypeScript)
├── package.json
└── requirements.txt

```

---

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key — get one at console.anthropic.com

### Install

```bash
# Python dependencies
pip3 install anthropic

# Node dependencies
npm install

# Playwright browsers
npx playwright install chromium
```

### Set your API key

```bash
export ANTHROPIC_API_KEY=your_key_here
```

---

## Usage

### Agent 1 — Generate test cases

```bash
python3 agents/test_generator.py \
  --story "As a user I want to log in with my email and password"
```

### Agent 2 — Analyse failures

```bash
npx playwright test --reporter=json > playwright-report/results.json
python3 agents/failure_analyser.py --report playwright-report/results.json
```

### Agent 3 — Self-healing selectors

```bash
python3 agents/self_healer.py \
  --selector "#add-todo-button" \
  --html page_snapshot.html
```

---

## Example Output

### Agent 1 — Test Generator

**Input:** `"As a user I want to log in with my email and password"`

**Output:**
# Test Cases: User Login with Email and Password

---

### [TC-001] Successful login with valid credentials
- **Type**: Happy Path
- **Preconditions**: User has a registered and active account; user is on the login page
- **Steps**:
  1. Enter a valid registered email address into the email field
  2. Enter the correct password for that account into the password field
  3. Click the "Log In" button
- **Expected result**: User is authenticated, redirected to their account dashboard, and a valid session is established
- **Priority**: High

---

### [TC-002] Login fails with incorrect password
- **Type**: Negative
- **Preconditions**: User has a registered and active account; user is on the login page
- **Steps**:
  1. Enter a valid registered email address into the email field
  2. Enter an incorrect password into the password field
  3. Click the "Log In" button
- **Expected result**: Login is rejected, a generic error message is displayed (e.g. "Invalid email or password"), and the user remains on the login page
- **Priority**: High

---

### [TC-003] Login fails with an unregistered email address
- **Type**: Negative
- **Preconditions**: User is on the login page
- **Steps**:
  1. Enter an email address that does not exist in the system
  2. Enter any password into the password field
  3. Click the "Log In" button
- **Expected result**: Login is rejected and the same generic error message is displayed as for an incorrect password, giving no indication of whether the email exists
- **Priority**: High

---

### [TC-004] Login fails when one or both fields are left empty
- **Type**: Edge Case
- **Preconditions**: User is on the login page
- **Steps**:
  1. Leave the email field empty and the password field empty
  2. Click the "Log In" button
  3. Repeat with only the email field filled in, then only the password field filled in
- **Expected result**: Form submission is blocked each time; clear inline validation messages prompt the user to complete all required fields
- **Priority**: High

---

### [TC-005] Account is locked after repeated failed login attempts
- **Type**: Edge Case
- **Preconditions**: User has a registered and active account; user is on the login page
- **Steps**:
  1. Enter the correct email address and an incorrect password
  2. Click the "Log In" button
  3. Repeat steps 1–2 until the maximum allowed failed attempts are reached (e.g. 5 times)
- **Expected result**: The account is temporarily locked, the user is informed of the lockout and advised to retry later or reset their password, and further login attempts are blocked for the lockout period
- **Priority**: High

---

### [TC-006] Password field value is masked during input
- **Type**: Security
- **Preconditions**: User is on the login page
- **Steps**:
  1. Click into the password field
  2. Type any characters into the password field
- **Expected result**: All entered characters are masked (e.g. displayed as dots or asterisks) and the plain-text value is never visible in the UI
- **Priority**: High

---

### [TC-007] Login form is protected against brute-force attacks
- **Type**: Security
- **Preconditions**: User is on the login page
- **Steps**:
  1. Submit the login form repeatedly with different password values in rapid succession, simulating an automated brute-force attempt
- **Expected result**: The system detects the pattern and responds with rate limiting (e.g. increasing delays, CAPTCHA challenge, or temporary IP block), preventing unlimited automated attempts
- **Priority**: High

---

### [TC-008] Credentials are not exposed in the browser URL or history
- **Type**: Security
- **Preconditions**: User is on the login page
- **Steps**:
  1. Enter a valid email and password
  2. Click the "Log In" button
  3. Inspect the browser address bar and browser history after submission
- **Expected result**: The email and password do not appear in the URL as query parameters at any point; the form submits via POST or equivalent secure method
- **Priority**: High

---
> **Note**: Agent 1 generates human-readable test descriptions that a QA engineer 
> reviews and implements in Playwright. This is intentional — AI-generated test 
> artifacts should always have a human review step before execution. The login 
> example above would be implemented as a Playwright spec against a real login page. 
> The todo.spec.ts suite shows the same pattern applied to the TodoMVC app.

### Agent 2 — Failure Analyser

**Input:** Playwright JSON report with 1 failing test

**Output:**
📋 Reading report: playwright-report/results.json
❌ Found 3 failure(s). Sending to Claude...

────────────────────────────────────────────────────────────
---
### ❌ TC-001 | can create a new todo item (Run 1)
**What happened**: After attempting to create a new todo item with the text "Buy Coffee", the test could not find that text anywhere on the page within 5 seconds. The item either wasn't created, wasn't displayed, or the text doesn't match what's actually rendered.
**Likely causes**:
  1. The form submission is broken — e.g. the Enter key press or submit button click is not being triggered correctly, so the item is never added
  2. The todo item is saved but rendered with different text (e.g. trimmed, cased differently, or truncated — "buy coffee" vs "Buy Coffee")
  3. The input field interaction is failing silently — the text may not be typed into the correct element, leaving the field empty on submit
  4. A UI re-render or navigation after submission is wiping the list before the assertion runs
**Next steps**:
  - Add a screenshot or video capture at the point of failure to see the actual state of the page after the action
  - Check the test's input/submit steps — verify `fill()` targets the correct locator and that the form submission step (Enter key or button click) is actually firing
  - Inspect the DOM after submission in a headed run (`--headed`) to confirm whether the item appears at all
  - Verify the exact text rendered in the UI matches `'Buy Coffee'` (check for case sensitivity, whitespace, or special characters)
  - Check browser console/network logs for any errors during item creation (e.g. a failed API call)
**Severity**: High — Core functionality (creating a todo item) is completely non-functional across all runs, blocking validation of the primary user journey.

---
### ❌ TC-001 | can create a new todo item (Run 2)
**What happened**: Identical failure to Run 1 — "Buy Coffee" was not visible after the create action. See above.
**Likely causes**:
  1. Same root cause as Run 1 — this is a consistent, deterministic failure, not a flake
  2. No environment variability is masking the issue; the failure reproduces 100% of the time
**Next steps**:
  - Treat this as a confirmed bug, not a flaky test — no retry strategy will fix it
  - Prioritise root cause investigation as described in Run 1 above
**Severity**: High — Consistent reproduction confirms a real defect, not transient infrastructure noise.

---
### ❌ TC-001 | can create a new todo item (Run 3)
**What happened**: Identical failure to Runs 1 and 2 — "Buy Coffee" was not visible after the create action. See above.
**Likely causes**:
  1. Same root cause as Runs 1 and 2 — 3/3 failure rate confirms a deterministic defect
  2. Possibly a recent code change broke the todo creation feature or changed the rendered output
**Next steps**:
  - Check recent commits/PRs that touched the todo input component, form submission logic, or the list rendering
  - Run the test in isolation with `--debug` mode to step through each action interactively
  - If this test was previously passing, use `git bisect` to identify the breaking commit
**Severity**: High — Third consecutive failure of the same test confirms this is a reliable signal of a broken feature.

---

## 📊 SUMMARY

| | |
|---|---|
| **Total failures** | 3 |
| **Unique tests affected** | 1 (TC-001) |
| **Failure rate** | 100% (3/3 runs) |

**Common pattern**: All three failures are identical — same test, same locator (`getByText('Buy Coffee')`), same timeout, same error. This is a **deterministic failure**, not flakiness. The todo creation feature is definitively broken in this environment.

**Top recommendation**: Do not add retries or increase timeouts — this will not help. The team should immediately inspect the todo creation flow end-to-end (input → submit → render), compare against recent code changes, and run the test in headed/debug mode to observe exactly where the flow breaks down. A 5-second timeout is already generous for a UI interaction; the item simply isn't appearing at all.

---

### Agent 3 — Self Healer

**Input:** Broken selector `#add-todo-button`

**Output:**
## Self-Healing Suggestions for: `#add-todo-button`

**Why it likely broke**:
The element with `id="add-todo-button"` does not exist in the current HTML. The TodoMVC app uses a text input (`<input class="new-todo">`) to add todos — typically by pressing **Enter** after typing, rather than clicking a dedicated button. There is no button element present in the DOM at all.

---

**Suggested alternatives** (best first):

1. `input.new-todo`
   - Type: CSS (class)
   - Resilience: Medium
   - Reason: The `.new-todo` class is a well-established TodoMVC convention and unlikely to change; this is the actual element used to add todos in this app.

2. `input[placeholder="What needs to be done?"]`
   - Type: CSS (attribute/text)
   - Resilience: Medium
   - Reason: The placeholder text is visible and semantically meaningful, making it a stable hook tied to UX intent rather than implementation details.

3. `header.header input`
   - Type: CSS (structural)
   - Resilience: Low
   - Reason: Scopes the input to the header context, reducing ambiguity if more inputs are added, but relies on structural nesting.

4. `section.todoapp input`
   - Type: CSS (structural)
   - Resilience: Low
   - Reason: Broader fallback scoped to the main app section; useful if the header class changes.

---

**Playwright code snippet**:
```typescript
// Replace your broken locator with:
// Type into the input and press Enter to add a todo (no button exists)
const todoInput = page.locator('input[placeholder="What needs to be done?"]');
await todoInput.fill('My new todo');
await todoInput.press('Enter');
```

> ⚠️ **Note**: If your test was calling `.click()` on a button, the interaction model has changed — this app submits todos via the **Enter key** on the input field, not a button click. Update your test logic accordingly.

---

**Prevention tip**: Prefer `data-testid` attributes (e.g., `data-testid="add-todo-input"`) added explicitly for testing, so selectors remain stable even when IDs, classes, or element types are refactored.


---

## Key Design Decisions

### System prompts as guardrails
Each agent uses a carefully designed system prompt that constrains Claude's output to a consistent, parseable format. This is critical in a production context — you never want AI-generated test artifacts going into a pipeline without human review.

### Recursive suite parsing
Playwright's JSON report nests suites inside suites. The failure analyser walks the structure recursively to catch failures at any depth — a naive flat parser misses them.

### HTML truncation in the self-healer
Page HTML can be very large. The self-healer truncates to 8,000 characters before sending to Claude, keeping API costs low and responses focused.

---

## What I Learned

- Prompt engineering for consistent, structured output is harder than it looks — small wording changes produce very different results
- Claude's analysis of failure patterns (distinguishing flakiness from deterministic bugs) adds genuine value beyond what a stack trace shows
- The self-healing pattern works best when you give Claude both the broken selector AND the full page context — without the HTML it can only guess

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Claude API (claude-sonnet-4-6) | Test generation, failure analysis, self-healing |
| Playwright + TypeScript | Test execution |
| Python 3.9 | Agent scripts |

---

*Built as a portfolio project to demonstrate AI-native quality engineering practices.*
