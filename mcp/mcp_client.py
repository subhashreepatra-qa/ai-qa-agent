import asyncio
from contextlib import AsyncExitStack
import os
from typing import Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params=StdioServerParameters(
            command= self._command,
            args=self._args,
            env=self._env
        )
        stdio_transport= await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio,_write=stdio_transport
        self._session= await self._exit_stack.enter_async_context(
             ClientSession(_stdio,_write)
        )
        await self._session.initialize()
    def session(self):
        if self._session is None:
            raise RuntimeError("Session is none")
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result= await self._session.list_tools()
        return result.tools
    async def call_tools(self, 
                         tool_name:str,
                         tool_input:dict) ->types.CallToolResult | None:
        if(tool_name is None):
            raise ValueError("Tool Name should ne non empty")
        if(tool_input is None):
            raise ValueError("Tool input should be non empty")
        return await self._session.call_tool(tool_name, tool_input)
    async def cleanup(self):
        await self._exit_stack.aclose()

    async def __aenter__(self):
        await self.connect()
        return self
    async def __aexit__(self, exc_type, exc, tb):
        await self.cleanup()
async def main(): 
    print("Starting...")
    try:
        async with MCPClient(command="uv",
                             args=["run", "mcp/mcp_server.py"],
                             env={**os.environ, "ANTHROPIC_API_KEY":os.environ.get("ANTHROPIC_API_KEY", "")}) as _client:
            print("Connected..!")
            user_story = input("Enter user story:")
            result=await _client.call_tools(
                tool_name="generate_test_scenario",
                tool_input={"user_story": user_story}
            )
            print(result.content[0].text)
    except Exception as e:
        print(f"Error:  {e}")    

if __name__ == "__main__":asyncio.run(main())  

     
            


