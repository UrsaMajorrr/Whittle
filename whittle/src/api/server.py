import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("whittle")

BASE_URL = "http://localhost:8000"
USER_AGENT = "Whittle/1.0"

@mcp.tool()
def choose_software(prompt: str) -> str:
    return "I'm a software that can choose the best CFD for the user's prompt"

@mcp.tool()
def run_simulation(prompt: str) -> str:
    return "I'm a software that can run a simulation"


if __name__ == "__main__":
    mcp.run(transport="stdio")



