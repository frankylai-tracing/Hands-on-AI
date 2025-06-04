import asyncio
import os
import shutil
import subprocess
import time
from typing import Any
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from dotenv import load_dotenv
import agentops


set_tracing_disabled(disabled=True)

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


# Load environment variables
load_dotenv()
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))

WORKING_MODEL = str(os.getenv("WORKING_MODEL", ""))
PPINFRA_BASE_URL = str(os.getenv("PPINFRA_BASE_URL", ""))
PPINFRA_API_KEY = str(os.getenv("PPINFRA_API_KEY", ""))
AGENTS_API_KEY = str(os.getenv("AGENTS_API_KEY", ""))

VLLM_BASE_URL = str(os.getenv("VLLM_BASE_URL", ""))
VLLM_API_KEY = str(os.getenv("VLLM_API_KEY", ""))
VLLM_MODEL_2_5 = str(os.getenv("VLLM_MODEL_2_5", ""))
VLLM_MODEL_3 = str(os.getenv("VLLM_MODEL_3", ""))

agentops.init(api_key=AGENTS_API_KEY)

# =================================ppinfra model================================
external_client = AsyncOpenAI(
    api_key=PPINFRA_API_KEY,
    base_url=PPINFRA_BASE_URL,
)
external_model = OpenAIChatCompletionsModel(
    model=WORKING_MODEL, openai_client=external_client
)
# =================================ppinfra model================================

# =================================vllm model===================================
# external_client = AsyncOpenAI(
#     api_key=VLLM_API_KEY,
#     base_url=VLLM_BASE_URL,
# )
# external_model = OpenAIChatCompletionsModel(
#     model=VLLM_MODEL_3, openai_client=external_client
# )

# =================================vllm model===================================


async def run(mcp_server: MCPServer):

    agent = Agent(
        name="Assistant",
        instructions="Use the appropriate tools to answer the questions.",
        model=external_model,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")

    question_list = [
        "你现在可使用的工具有哪些？",
        "数据库中的表格有哪些？",
        "第一个表格的 schemas 是什么？",
        "products 表格里有多少个产品？",
        "products 有多少个产品类型？",
        "数据库中有多少个用户？",
    ]

    for item in question_list:
        print(f"\nQuery: {item}")
        try:
            result = await Runner.run(starting_agent=agent, input=item)
            print("\n" + result.final_output)
            print("\n\n")
        except Exception as e:
            print(f"\nError: {str(e)}")

    # while True:
    #     try:
    #         query = input("\nQuery: ").strip()
    #         if query.lower() == "quit":
    #             break
    #         result = await Runner.run(starting_agent=agent, input=query)
    #         print("\n" + result.final_output)
    #     except Exception as e:
    #         print(f"\nError: {str(e)}")


async def main():
    server_url = f"http://127.0.0.1:{MCP_PORT}/sse"
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
        server_file = os.path.join(this_dir, "server.py")

        print(f"Starting SSE server at http://127.0.0.1:{MCP_PORT}/sse ...")

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
