from pydantic import BaseModel, Field
from typing import Optional, List, Any
from dotenv import load_dotenv
import agentops
import os

import time
import asyncio

import shutil
import subprocess

from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


from PROMPT import TEXT2SQL_AGENT_SYSTEM_INSTRUCTIONS

from agents import Agent, Runner
from agents import set_tracing_disabled

from llm_service import external_model


set_tracing_disabled(disabled=True)

load_dotenv()

MCP_PORT = int(os.getenv("MCP_PORT", "8322"))
AGENTS_API_KEY = str(os.getenv("AGENTS_API_KEY", ""))

agentops.init(api_key=AGENTS_API_KEY)


class SQLQueryResult(BaseModel):
    """SQL查询结果"""

    query: str = Field(..., description="生成的SQL查询语句")
    success: bool = Field(..., description="查询语句是否成功执行")
    error_message: Optional[str] = Field(
        None, description="如果查询失败，这里会包含错误信息"
    )
    result: Optional[List[str]] = Field(None, description="查询结果")
    result_summary: Optional[str] = Field(None, description="查询结果的文本摘要")


async def run(mcp_server: MCPServer):
    sql_agent = Agent(
        name="sql query agent",
        model=external_model,
        instructions=TEXT2SQL_AGENT_SYSTEM_INSTRUCTIONS,
        # output_type=SQLQueryResult,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    agent = Agent(
        name="Assistant",
        instructions="判读用户的问题是否数据库SQL查询相关问题,如果是交接给sql query agent处理,如果不是,则直接回答用户问题",
        model=external_model,
        handoffs=[sql_agent],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    # 示例查询
    queries = [
        "获取所有员工的姓名和部门",
        "查找薪资高于15000的员工信息",
        "计算每个部门的平均薪资",
        "查找参与项目最多的员工",
        "获取研发部门中参与'新产品开发'项目的员工信息",
    ]
    # while True:
    #     try:
    #         query = input("\nQuery: ").strip()
    #         if query.lower() == "quit":
    #             break
    #         result = await Runner.run(starting_agent=agent, input=query)
    #         print("\n" + result.final_output)
    #     except Exception as e:
    #         print(f"\nError: {str(e)}")

    # 处理每个查询
    for i, query in enumerate(queries):
        print(f"\n===== 示例 {i+1}: {query} =====")
        # 运行代理
        result = await Runner.run(starting_agent=agent, input=query)
        print(f"\n{result.final_output}\n")
    # 输出结果
    # print(f"生成的SQL查询: {result.final_output.query}")
    # print(f"查询是否成功: {result.final_output.success}")
    # if result.output.success:
    #     print(f"结果摘要: {result.output.result_summary}")
    #     if result.output.result:
    #         print("查询结果:")
    #         for j, row in enumerate(result.output.result):
    #             if j < 5:  # 只显示前5行结果
    #                 print(f"  {row}")
    #         if len(result.output.result) > 5:
    #             print(f"  ...(共 {len(result.output.result)} 行)")
    # else:
    #     print(f"错误信息: {result.output.error_message}")


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
        server_file = os.path.join(this_dir, "mcp_server.py")

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
