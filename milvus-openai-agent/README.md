# Milvus-OpenAI-Agent

本项目展示了如何将 [Milvus 向量数据库](https://milvus.io) 集成到 OpenAI Agent 中，以测试大模型调用外部工具进行文本检索。

## 项目结构

```bash
milvus-openai-agent/
├── .env                        # 环境变量文件
├── init_milvus_demo_index.ipynb # 用于初始化 Milvus 向量索引的 Jupyter Notebook
├── main.py                     # OpenAI Function Calling 与 Milvus 集成的示例脚本
├── mcp_client.py               # MCP 客户端测试脚本
├── mcp_server.py               # MCP 服务器端脚本
├── README.md                   # 项目说明文档
```

## 使用说明

> 在初始化 Milvus 索引前，确保本地已经通过docker的方式拉去并启动Milvus服务动。

### 1. 初始化 Milvus 索引

运行init_milvus_demo_index.ipynb文件，以创建 Milvus 向量索引并插入示例数据.

### 2. 测试 Function Calling 模式

运行 `main.py` 脚本，展示如何通过 OpenAI 的 Function Calling 功能与 Milvus 向量索引集成：

```bash
python main.py
```

> - 测试用例: Find documents in the 'demo' collection that are similar to this concept: 'information retrieval'

### 3. 测试 MCP 模式（客户端-服务器）

将mcp server集成到openai-agents中，以测试文本检索功能。

```bash
python mcp_client.py
```

> 运行mcp_client.py时，会自动启动mcp_server.py
> - 测试用例: Find documents in the 'demo' collection that are similar to this concept: 'information retrieval'

