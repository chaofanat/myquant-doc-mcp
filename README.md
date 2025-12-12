# myquant-doc-mcp

掘金量化文档搜索MCP服务，为需要掘金量化SDK文档的智能体提供专业文档查询工具，采用"收集查询请求 -> 请求掘金量化API -> 下载URL到本地 -> 本地Whoosh检索 -> 返回结果"的流程设计，在保证高效准确检索的同时，最大程度减轻官方文档服务器的负担。

## 特性

- **完整搜索流程**：API调用 + 文档下载 + 索引建立 + 本地检索
- **智能缓存**：自动跳过已下载和已索引的文档，提升效率
- **中文支持**：基于jieba分词的中文全文搜索
- **多种搜索模式**：
  - 关键词搜索
  - 布尔查询（AND、OR、NOT）
  - 精确短语搜索
  - 模糊搜索（拼写纠错）
  - 标签过滤搜索
- **stdio模式**：标准MCP协议，支持Claude Desktop等MCP客户端

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd myquant-doc-mcp
```

### 2. 创建虚拟环境

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### Claude Desktop配置

在Claude Desktop的MCP配置文件中添加：

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "D:\\workspace\\myquant-doc-mcp\\mcp_server.py"
      ]
    }
  }
}
```

**macOS** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/path/to/myquant-doc-mcp/venv/bin/python",
      "args": [
        "/path/to/myquant-doc-mcp/mcp_server.py"
      ]
    }
  }
}
```

**Linux** (`~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/path/to/myquant-doc-mcp/venv/bin/python",
      "args": [
        "/path/to/myquant-doc-mcp/mcp_server.py"
      ]
    }
  }
}
```

注意：请将路径替换为你的实际项目路径。

## 使用方法

配置完成后，重启Claude Desktop，即可在对话中使用以下工具：

### 1. search_documents - 完整文档搜索
```
搜索掘金量化关于"交易接口"的文档
```

### 2. search_documents_local - 快速本地搜索
```
快速搜索本地索引中关于"行情数据"的内容
```

### 3. search_boolean - 布尔查询
```
使用布尔查询：title:"API" AND content:"Python"
```

### 4. search_phrase - 精确短语搜索
```
精确搜索短语"实时行情接口"
```

### 5. search_fuzzy - 模糊搜索
```
模糊搜索"jiaoyi"（交易的拼音错误）
```

### 6. search_tag - 标签搜索
```
搜索标签为"API"的文档
```

### 7. discover_documents - 发现文档
```
发现关于"策略回测"的相关文档
```

### 8. get_system_stats - 系统统计
```
获取当前系统的文档数量和索引统计
```

## 工作原理

1. **首次搜索**：
   - 调用掘金量化API获取相关文档URL
   - 下载文档到本地（智能跳过已存在的）
   - 建立Whoosh全文索引（智能跳过已索引的）
   - 在本地索引中搜索并返回结果

2. **后续搜索**：
   - 直接使用本地索引，快速响应
   - 自动跳过已处理的文档，节省时间

3. **缓存机制**：
   - 文档级别的缓存（跳过已下载）
   - 索引级别的缓存（跳过已索引）
   - 提升处理效率，减少网络请求

## 目录结构

```
myquant-doc-mcp/
├── mcp_server.py          # MCP服务主文件（stdio模式）
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── core/                  # 核心业务逻辑
│   └── search_flow.py     # 搜索流程控制
├── services/              # 服务层
│   ├── myquant_api.py     # 掘金量化API服务
│   ├── downloader.py      # 文档下载服务
│   └── whoosh_service.py  # Whoosh搜索引擎服务
├── utils/                 # 工具模块
├── data/                  # 数据目录
│   ├── docs/              # 下载的文档
│   └── index/             # Whoosh索引
└── tests/                 # 测试文件

```

## 技术栈

- **MCP协议**：标准MCP stdio传输
- **搜索引擎**：Whoosh全文搜索
- **中文分词**：jieba
- **异步框架**：asyncio
- **文档解析**：BeautifulSoup4

## 开发

### 运行测试
```bash
pytest tests/
```

### 初始化索引
```bash
python init.py
```

## 注意事项

1. 首次使用会下载和索引大量文档，需要一定时间
2. 本地索引会占用一定磁盘空间
3. 建议定期更新索引以获取最新文档
4. 日志文件位于项目根目录

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！