from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings

import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import set_tracing_disabled
import agentops

from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

WORKING_MODEL = str(os.getenv("WORKING_MODEL", "qwen/qwen2.5-32b-instruct"))

PPINFRA_BASE_URL = str(
    os.getenv("PPINFRA_BASE_URL", "https://api.ppinfra.com/v3/openai")
)

PPINFRA_API_KEY = str(os.getenv("PPINFRA_API_KEY", ""))

AGENTS_API_KEY = str(os.getenv("AGENTS_API_KEY", ""))

agentops.init(api_key=AGENTS_API_KEY)

set_tracing_disabled(disabled=True)


external_client = AsyncOpenAI(
    api_key=PPINFRA_API_KEY,
    base_url=PPINFRA_BASE_URL,
)
external_model = OpenAIChatCompletionsModel(
    model=WORKING_MODEL, openai_client=external_client
)


async def run(mcp_server: MCPServer):

    agent = Agent(
        name="Assistant",
        instructions="Use the appropriate tools to answer the questions. if the question does not require tools, answer directly.",
        model=external_model,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break
            result = await Runner.run(starting_agent=agent, input=query)
            print("\n" + result.final_output)
        except Exception as e:
            print(f"\nError: {str(e)}")


async def main():
    server_url = f"http://127.0.0.1:8223/sse"
    print(f"\n服务器地址:{ server_url}\n")
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": server_url,
        },
    ) as server:

        await run(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # We'll run the SSE server in a subprocess. Usually this would be a remote server, but for this
    # demo, we'll run it locally at http://localhost:8000/sse
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "mcp_server.py")

        print(f"Starting SSE server at http://127.0.0.1:{8223}/sse ...")

        # Run `uv run server.py` to start the SSE server
        process = subprocess.Popen(["uv", "run", server_file])
        # Give it 3 seconds to start
        time.sleep(3)

        print("SSE server started. Running example...\n\n")
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
