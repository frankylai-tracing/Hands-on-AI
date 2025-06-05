# SQLite MCP OpenAI Agents

这是一个基于MCP和openai-agents的的小型项目, 用于测试sqlite-mcp-server的功能。

## 安装与使用

1. **生成 SQLite 数据库**  
   运行以下命令生成样本 SQLite 数据库（`sample.db`）：  
   ```bash
   python generate_sample_db.py
   ```

2. **启动客户端并测试服务器**  
   运行以下命令启动客户端以测试 `sqlite-mcp-server`：  
   ```bash
   python main.py
   ```
   > 运行后,会自动启动mcp服务`server.py`

## 文件说明
- `generate_sample_db.py`: 用于生成样本 SQLite 数据库的脚本。
- `main.py`: 客户端脚本，用于与服务器交互。
- `sample.db`: SQLite 数据库文件（由 `generate_sample_db.py` 生成）。
- `server.py`: 服务器端脚本，用于运行 SQLite MCP 服务器。
- `.env`: 环境配置文件（在运行脚本前请确保正确设置）。