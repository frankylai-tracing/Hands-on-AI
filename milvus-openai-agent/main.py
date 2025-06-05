import json
from typing import Any
from pymilvus import MilvusClient
from agents import function_tool, RunContextWrapper
import asyncio
from pydantic import BaseModel
from dotenv import load_dotenv
import agentops
import os


load_dotenv()

WORKING_MODEL = str(os.getenv("WORKING_MODEL", "qwen/qwen2.5-32b-instruct"))

PPINFRA_BASE_URL = str(
    os.getenv("PPINFRA_BASE_URL", "https://api.ppinfra.com/v3/openai")
)

PPINFRA_API_KEY = str(os.getenv("PPINFRA_API_KEY", ""))

AGENTS_API_KEY = str(os.getenv("AGENTS_API_KEY", ""))

agentops.init(api_key=AGENTS_API_KEY)


def serialize_hit(hit):
    """将 Hit 对象转换为可序列化的字典"""
    return {
        "id": hit.id,
        "distance": hit.distance,
        "score": getattr(hit, "score", None),
        "entity": dict(hit.entity) if hasattr(hit.entity, "__dict__") else hit.entity,
    }


@function_tool
async def search_milvus_text(
    ctx: RunContextWrapper[Any], collection_name: str, query_text: str, limit: int
) -> str:
    """Search for text documents in a Milvus collection using full text search.

    Args:
        collection_name: Name of the Milvus collection to search.
        query_text: The text query to search for.
        limit: Maximum number of results to return.
    """
    try:
        # Initialize Milvus client
        client = MilvusClient()

        # Prepare search parameters for BM25
        search_params = {"metric_type": "BM25", "params": {"drop_ratio_search": 0.2}}

        # Execute search with text query
        results = client.search(
            collection_name=collection_name,
            data=[query_text],
            anns_field="sparse",
            limit=limit,
            search_params=search_params,
            output_fields=["text"],
        )
        # 序列化结果
        serializable_results = [
            [serialize_hit(hit) for hit in hits] for hits in results
        ]

        return json.dumps(
            {
                "results": serializable_results,
                "query": query_text,
                "collection": collection_name,
            }
        )

    except Exception as e:
        print(f"Exception is: {e}")
        return f"Error searching Milvus: {str(e)}"


from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel


external_client = AsyncOpenAI(
    api_key=PPINFRA_API_KEY,
    base_url=PPINFRA_BASE_URL,
)
external_model = OpenAIChatCompletionsModel(
    model=WORKING_MODEL, openai_client=external_client
)


from agents import Agent, Runner, WebSearchTool, trace
from agents import set_tracing_disabled

set_tracing_disabled(disabled=True)


async def main():
    agent = Agent(
        name="Milvus Searcher",
        model=external_model,
        instructions="你是一个助手，你需要判断是否需要使用工具来回答问题。如果不需要工具,请直接回答. 如果需要工具,请使用工具来回答问题.",
        tools=[
            search_milvus_text,
        ],
        # output_type=MilvusSearchResults,
    )

    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break
            result = await Runner.run(starting_agent=agent, input=query)
            print("\n" + result.final_output)
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
