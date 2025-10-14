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

mcp_params = MCPServerSseParams(url=f"http://localhost:{os.environ.get("MCP_PORT", 8000)}/sse")

async def defineMCPServerandRunAgent():
    async with MCPServerSse(
        name="SSE Python Server",
        params=mcp_params,
        client_session_timeout_seconds=10,
        max_retry_attempts=3,
        cache_tools_list=True,
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE MCP Agent Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")            
            tools = await server.list_tools()
            print("\n Available tools:")
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            await runAgent(server) 


if __name__ == "__main__":
    async def main():
        server = await defineMCPServerandRunAgent()
    asyncio.run(main())