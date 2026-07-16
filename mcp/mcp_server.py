import os
import sys

import anthropic
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp import types
from pydantic import Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.qa_utils import (
    CLAUDE_MODEL,
    FAILED_TEST_ANALYSIS_SYSTEM_PROMPT,
    TEST_CASE_GENERATION_SYSTEM_PROMPT,
    build_summary,
    parse_playwright_report,
)

# Initialize MCP Server
mcp=FastMCP("qa-agent")

#Tool - Claude can call this directly
@mcp.tool(name="generate_test_scenario",
          description="Generate Structured Test cases from the User Story using Claude")

def generate_test_scenario(
    user_story: str=Field(description="Generate Structured Test cases from the User Story using Claude")

) -> str:
    client=anthropic.Anthropic()
    response=client.messages.create(
       model=CLAUDE_MODEL,
       max_tokens=1500,
       system=TEST_CASE_GENERATION_SYSTEM_PROMPT,
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
@mcp.tool(name="analyze_test_failure",
          description="Analyze failed test cases and provide insights"
          )
def analyze_test_failure(report_path: str=Field(description="The Playwright Json file to analyze the failed test cases for")) -> str:
    failures = parse_playwright_report(report_path)

    if not failures:
        return "✅ No failures — all tests passed!"

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

@mcp.prompt(
    name="analyze_test_failure_prompt",
    description="Analyze failed test cases and provide insights"
)
def analyze_test_failure_prompt(
 report_path:str=Field(description="The Playwright Json file to analyze the failed test cases for")   
)->list:
    return [          
            base.UserMessage(content=f"""Analyze failed test cases and provide insights for the Playwright Json file.
            Use the analyze_test_failure tool to do this.
            <report_path>
            {report_path}
            </report_path>

            After Analyzing the report display the insights in full.""")
        
    ]

if __name__== "__main__":
    mcp.run()

