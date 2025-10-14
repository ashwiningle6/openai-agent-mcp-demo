import asyncio
from agents import Agent, Runner, gen_trace_id, trace, set_default_openai_key
from agents.mcp import MCPServer, MCPServerSseParams, MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv
import os 

# Load variables from .env file
load_dotenv()
set_default_openai_key(os.environ.get("OPENAI_API_KEY", ""))

async def runAgent(mcp_server: MCPServer):
    agent = Agent(
        name="Tool based Assistant",
        instructions="Use available tools to answer user queries.",
        model="gpt-4o-mini",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(temperature=0.95, top_p=0.95, tool_choice="required"),
    )

    # Use the `add` tool to add two numbers
    num1, num2 = input("\nEnter 2 numbers (e.g., 12, 15): ").split(",")
    message = f"Multiply these numbers: {num1} and {num2}."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Final Output: {result.final_output}\n")

    # Run the `get_weather` tool
    place_input = input("Enter a place you want to check temperature for: ")
    message = f"What's the weather in {place_input}?"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Final Output: {result.final_output}")

mcp_params = MCPServerSseParams(url="http://localhost:8000/sse")

async def defineMCPServerandRunAgent():
    async with MCPServerSse(
        name="SSE Python Server",
        params=mcp_params,
    ) as server:
        
        with trace(workflow_name="mcpClient"):

            tools = await server.list_tools()
            # Print the description of each available tool
            print("\n Available tools:")
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            await runAgent(server) 


if __name__ == "__main__":
    
    async def main():
        server = await defineMCPServerandRunAgent()

    asyncio.run(main())