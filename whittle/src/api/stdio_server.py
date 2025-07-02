import asyncio
import sys
import os
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from pathlib import Path

# Add the project root to the Python path so we can import whittle modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv
from whittle.src.application.llm_agent_interactor import ClaudeLLMAgent, OpenAILLMAgent
from whittle.src.infra.registry import ModelRegistry

load_dotenv()

class WhittleServer:
    def __init__(self, llm_model):
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

        if self.session:
            response = await self.session.list_tools()
            tools = response.tools
            print([tool.name for tool in tools])

    async def process_query(self, query: str):
        if not self.session:
            return "Error: No active session"
            
        messages: List[Dict[str, Any]] = [
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
        if hasattr(response, 'content'):
            for content in response.content:
                if content.type == "text":
                    final_text.append(content.text)
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_args = content.input

                    result = await self.session.call_tool(tool_name, tool_args)
                    
                    # Handle different content types safely
                    tool_result_text = "Tool executed successfully"
                    if hasattr(result, 'content') and result.content:
                        try:
                            # Convert the first content item to string
                            first_content = result.content[0]
                            # The linter is wrong here - this actually works in practice
                            tool_result_text = first_content.text  # type: ignore
                        except (AttributeError, IndexError):
                            # Fallback if the above doesn't work
                            tool_result_text = result.content[0].text  # type: ignore
                    else:
                        tool_result_text = result.content[0].text  # type: ignore
                        
                    final_text.append(f"\n{tool_result_text}\n")

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

    # Use the ModelRegistry to create the model instance
    model_registry = ModelRegistry(system_prompt="""You are an agent in a multi-tool system for CFD workflows. You MUST pick only ONE tool per user request.

Here's when to use each tool:
- create_cfd_case_without_generating_mesh → user says: "set up a new case", "start a simulation", "initialize files", "create case structure"
- foam_block_mesh_generation → user says: "generate mesh", "run blockMesh", "mesh the domain", "create mesh", "generate a mesh"
- foam_snappy_hex_mesh_generation → user says: "complex mesh", "STL mesh", "snappyHexMesh", "generate complex mesh"
- run_openfoam_simulation → user says: "run the simulation", "solve it", "start solving", "execute simulation"
- edit_file → user says: "change this file", "modify", "update text", "edit"
- help_tool_selection → use this if you're unsure which tool to pick

CRITICAL RULE: If the user asks to "generate a mesh" or "create a mesh", use foam_block_mesh_generation, NOT create_cfd_case_without_generating_mesh!

MESH GENERATION RULES:
- When generating blockMeshDict files, ALWAYS use simple single-block meshes with uniform grading (simpleGrading 1 1 1)
- Avoid complex multi-block structures that cause point merge failures
- Use symmetryPlane boundaries only for faces that are truly planar
- Keep mesh resolution moderate (e.g., 50-100 cells in each direction) for reliability
- Always test mesh topology before adding complex features

Never confuse CFD software like OpenFOAM with LLM model types like GPT or Claude.

Always return only one tool call.""")
    
    print(f"Available models: {model_registry.get_models()}")
    desired_model = input("Please select a model: ").lower()
    
    try:
        llm_model = model_registry.get_model(desired_model)
    except ValueError as e:
        print(f"Error: {e}")
        print("Using Claude as default.")
        llm_model = model_registry.get_model("claude")

    client = WhittleServer(llm_model)
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())