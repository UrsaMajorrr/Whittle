import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class WhittleServer:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_path: str):
        server_parameters = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_parameters))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print([tool.name for tool in tools])

    async def process_query(self, query: str):
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
            ,
        } for tool in response.tools]

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=messages,
            tools=available_tools,
            system="You are a helpful AI assistant that uses tools to help users with CFD simulations."
        )

        final_text = []

        assistant_message = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"\nTool Result: {result.content}\n")

                assistant_message.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content
                    }]
                })

                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    messages=messages,
                    tools=available_tools,
                    system="You are a helpful AI assistant that uses tools to help users with CFD simulations."
                )

                final_text.append(response.content[0].text)

        return "".join(final_text)
    

    async def chat_loop(self):
        print("MCP client started")
        print("Type your query or 'exit' to quit")

        while True:
            try:
                query = input("> ").strip()

                if query.lower() == "exit":
                    print("Exiting...")
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"Error: {str(e)}")


    async def cleanup(self):
        await self.exit_stack.aclose()

    
async def main():
    if len(sys.argv) != 2:
        print("Usage: python stdio_server.py <path_to_mcp_server>")
        sys.exit(1)

    client = WhittleServer()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())