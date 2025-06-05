from mcp.server.fastmcp import FastMCP
from pymilvus import MilvusClient
import json


mcp = FastMCP(name="milvus-openai-agent", host="127.0.0.1", port="8223")


def serialize_hit(hit):
    """将 Hit 对象转换为可序列化的字典"""
    return {
        "id": hit.id,
        "distance": hit.distance,
        "score": getattr(hit, "score", None),
        "entity": dict(hit.entity) if hasattr(hit.entity, "__dict__") else hit.entity,
    }


@mcp.tool()
async def search_milvus_text(collection_name: str, query_text: str, limit: int) -> str:
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


if __name__ == "__main__":
    mcp.run(transport="sse")
