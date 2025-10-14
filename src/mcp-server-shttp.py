import requests
import os
from fastmcp import FastMCP

# Create server
mcp = FastMCP(name="custom-mcp-server")

@mcp.tool()
def Multiply(a: int, b: int) -> int:
    """
    Multiply two numbers
    """
    return (a * b) 

@mcp.tool()
def Get_Current_Weather(city: str) -> str:
    """
    Get the current weather in a city
    """
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("MCP_HOST", "127.0.0.1"),
        port=os.environ.get("MCP_PORT", 8000),
    )