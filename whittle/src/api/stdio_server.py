import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
from whittle.src.application.llm_agent_interactor import ClaudeLLMAgent, LLMAgent
from whittle.src.infra.registry import ModelRegistry

load_dotenv()
llm_model = None

class WhittleServer:
    def __init__(self, llm_model: LLMAgent):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm_model = llm_model

    async def connect_to_server(self, server_path: str):
        server_parameters = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_parameters))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        try:
            await self.session.initialize()
            # Initialize the server with our model type
            model_type = "claude" if isinstance(self.llm_model, ClaudeLLMAgent) else "gpt"
            await self.session.call_tool("init_server", {"model_type": model_type})
        except Exception as e:
            print(f"Failed to connect to server: {str(e)}")
            await self.cleanup()
            sys.exit(1)

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
        } for tool in response.tools]

        response = self.llm_model.return_response_with_tools(query, available_tools)

        final_text = []

        assistant_message = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"\nTool Result: {result.content[0].text}\n")

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

                response = self.llm_model.return_response_with_tools(query, available_tools)
                if hasattr(response, 'content'):
                    for content in response.content:
                        if content.type == "text":
                            final_text.append(content.text)
                else:
                    final_text.append(str(response))

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

    model_registry = ModelRegistry(system_prompt="You are a helpful assistant that can help with CFD simulations.")
    desired_model = input("Please select a model: ")
    llm_model = model_registry.get_model(desired_model)

    client = WhittleServer(llm_model)
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())