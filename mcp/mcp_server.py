import anthropic
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp import types
from pydantic import Field

# Initialize MCP Server
mcp=FastMCP("qa-agent")

SYSTEM_PROMPT = """You are a senior QA engineer. Generate structured test cases from user stories.

For every user story, generate test cases covering:
1. Happy path
2. Negative tests
3. Edge cases
4. Security considerations
5. Audit Log Consideration
5. User lock Scenarios

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

#Tool - Claude can call this directly
@mcp.tool(name="generate_test_scenario",
          description="Generate Structured Test cases from the User Story using Claude")

def generate_test_scenario(
    user_story: str=Field(description="Generate Structured Test cases from the User Story using Claude")

) -> str:
    client=anthropic.Anthropic()
    response=client.messages.create(
       model="claude-sonnet-4-6",
       max_tokens=1500,
       system=SYSTEM_PROMPT,
       messages=[
           {"role": "user", "content": f"Generate test cases for this user story:\n\n{user_story}"}
        ]
    )

    return response.content[0].text

# Prompt — user triggers this from the CLI
@mcp.prompt(
    name="generate_test_case_prompt",
    description="Generate Structured test cases from User Story"
)
def generate_test_case_prompt(
 user_story:str=Field(description="The User Story to generate the test cases for")   
)->list:
    return [          
            base.UserMessage(content=f"""Generate Structured Test cases from the following User Story.
            Use the generate_test_scenario tool to do this.
            <user_story>
            {user_story}
            </user_story>

            After Generating the User Story display them in full.""")
        
    ]
if __name__== "__main__":
    mcp.run()

