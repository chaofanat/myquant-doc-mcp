# myquant-doc-mcp

掘金量化文档搜索MCP服务，为需要掘金量化SDK文档的智能体提供专业文档查询工具。采用"API调用 → 文档下载 → 索引建立 → 本地检索"的智能流程，在保证高效准确检索的同时，最大程度减轻官方文档服务器的负担。

## ✨ 特性

- **完整搜索流程**：API调用 + 文档下载 + 索引建立 + 本地检索
- **智能缓存**：自动跳过已下载和已索引的文档，大幅提升效率
- **优化的中文搜索**：
  - 基于jieba分词，支持70+量化交易专业术语
  - 多字段加权搜索（标题、内容、标题、代码、标签）
  - BM25F评分算法，相关性更高
- **多种搜索模式**：
  - 关键词搜索（支持OR组合）
  - 布尔查询（AND、OR、NOT）
  - 精确短语搜索
  - 模糊搜索（拼写纠错）
  - 标签过滤搜索
- **stdio模式**：标准MCP协议，完美支持Claude Desktop

## 📊 性能指标

- **搜索速度**：0.05-0.3秒
- **质量测试通过率**：100%
- **索引文档数**：409+
- **搜索覆盖率**：200-400结果/查询

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repository-url>
cd myquant-doc-mcp

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate          # Windows
source venv/bin/activate        # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 构建索引
python rebuild_index.py
```

### 2. 配置Claude Desktop

找到并编辑配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Windows配置**:
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe",
      "args": ["D:\\workspace\\myquant-doc-mcp\\mcp_server.py"]
    }
  }
}
```

**macOS/Linux配置**:
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/path/to/myquant-doc-mcp/venv/bin/python",
      "args": ["/path/to/myquant-doc-mcp/mcp_server.py"]
    }
  }
}
```

⚠️ **重要提示**：
- Windows路径使用双反斜杠 `\\` 或单斜杠 `/`
- 将路径替换为你的实际项目路径
- 必须使用虚拟环境中的Python

### 3. 启动使用

1. 保存配置文件
2. 完全重启Claude Desktop
3. 在Claude中发送：`搜索掘金量化关于"交易接口"的文档`

## 📖 使用指南

### 8个可用工具

| 工具 | 描述 | 使用示例 |
|------|------|----------|
| **search_documents** | 完整搜索（API+下载+索引+检索） | "搜索关于'Python API'的文档" |
| **search_documents_local** | 快速本地搜索 | "快速搜索'K线数据'" |
| **search_boolean** | 布尔查询 | "搜索: title:\"API\" AND content:\"交易\"" |
| **search_phrase** | 精确短语搜索 | "精确搜索'实时行情接口'" |
| **search_fuzzy** | 模糊搜索 | "模糊搜索'jiaoyi'（拼写错误）" |
| **search_tag** | 标签搜索 | "搜索标签为'SDK'的文档" |
| **discover_documents** | 文档发现 | "发现关于'策略回测'的文档" |
| **get_system_stats** | 系统统计 | "查看系统统计信息" |

### 搜索技巧

**基础搜索**：
```
搜索掘金量化关于"行情数据"的文档
```

**布尔查询**：
```
使用布尔查询搜索：title:"API" AND (content:"Python" OR content:"交易")
```

**快速本地搜索**（已有索引时更快）：
```
快速搜索本地索引中关于"K线"的内容
```

## 🔧 配置详解

### 获取正确路径

**Windows**:
```cmd
cd D:\workspace\myquant-doc-mcp
echo %CD%\venv\Scripts\python.exe
echo %CD%\mcp_server.py
```

**macOS/Linux**:
```bash
cd /path/to/myquant-doc-mcp
echo $(pwd)/venv/bin/python
echo $(pwd)/mcp_server.py
```

### 验证配置

```bash
# 检查Python版本
venv\Scripts\python.exe --version  # Windows
venv/bin/python --version          # macOS/Linux

# 验证MCP库
venv\Scripts\python.exe -c "import mcp; print('MCP OK')"

# 测试服务器
python quick_test.py
```

## 🛠️ 故障排查

### 问题1: Claude Desktop无法连接MCP服务

**症状**：底部状态栏无MCP服务连接指示

**解决方案**：
1. 检查配置文件JSON格式是否正确
2. 确认Python路径正确（使用虚拟环境中的Python）
3. 确认mcp_server.py路径正确
4. 完全重启Claude Desktop（不是最小化）
5. 查看Claude日志（通常在 `~/.claude/` 或 `%APPDATA%\Claude\`）

### 问题2: 搜索无结果

**症状**：工具调用成功但返回0结果

**解决方案**：
```bash
# 重建索引
python rebuild_index.py

# 测试搜索
python quick_test.py
```

### 问题3: 索引构建失败

**症状**：rebuild_index.py报错

**解决方案**：
```bash
# 检查数据目录
ls data/docs  # 应该有HTML文件

# 如果没有文档，先下载
python init.py

# 然后重建索引
python rebuild_index.py
```

### 问题4: Windows路径错误

**错误示例** ❌:
```json
"command": "D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe"
```

**正确配置** ✅:
```json
"command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe"
```
或
```json
"command": "D:/workspace/myquant-doc-mcp/venv/Scripts/python.exe"
```

### 问题5: 权限错误 (macOS/Linux)

**解决方案**：
```bash
chmod +x venv/bin/python
chmod +x mcp_server.py
```

## 🏗️ 项目结构

```
myquant-doc-mcp/
├── mcp_server.py              # MCP服务主文件（stdio模式）
├── init.py                    # 初始化脚本（下载文档）
├── rebuild_index.py           # 索引重建脚本
├── config.py                  # 配置文件
├── requirements.txt           # Python依赖
│
├── core/                      # 核心业务逻辑
│   └── search_flow.py         # 搜索流程控制
│
├── services/                  # 服务层
│   ├── myquant_api.py         # 掘金量化API服务
│   ├── downloader.py          # 智能下载器
│   ├── whoosh_service.py      # Whoosh搜索引擎（已优化）
│   └── search_service.py      # 搜索服务
│
├── models/                    # 数据模型
│   └── response.py            # API响应模型
│
├── utils/                     # 工具函数
│   └── logger.py              # 日志工具
│
├── data/                      # 数据目录
│   ├── docs/                  # 下载的文档（409个HTML）
│   └── index/                 # Whoosh搜索索引
│
└── tests/                     # 测试套件
    ├── test_search.py         # 搜索测试
    └── quick_test.py          # 快速验证
```

## 🔬 技术栈

- **MCP协议**：标准MCP stdio传输
- **搜索引擎**：Whoosh全文搜索 + BM25F算法
- **中文分词**：jieba（70+专业术语词典）
- **异步框架**：asyncio
- **文档解析**：BeautifulSoup4
- **数据模型**：Pydantic

## 🧪 开发与测试

### 运行测试

```bash
# 快速测试
python quick_test.py

# 完整测试套件
python test_search.py

# 单元测试
pytest tests/
```

### 维护索引

```bash
# 下载最新文档
python init.py

# 重建索引
python rebuild_index.py

# 查看统计
python -c "from core import SearchFlow; import json; print(json.dumps(SearchFlow().get_stats(), indent=2, ensure_ascii=False))"
```

### 日志查看

日志文件位于项目根目录，包含详细的搜索和错误信息。

## 📋 系统要求

### 最低配置
- Python 3.7+
- 2GB RAM
- 500MB 磁盘空间

### 推荐配置
- Python 3.9+
- 4GB+ RAM
- 1GB+ 磁盘空间

### 支持平台
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+)

## 💡 使用建议

1. **定期更新索引**（每周一次）：
   ```bash
   python init.py && python rebuild_index.py
   ```

2. **搜索技巧**：
   - 使用专业术语："交易接口"、"K线数据"、"策略回测"
   - 组合搜索：`title:"API" AND content:"Python"`
   - 短语搜索：`"实时行情接口"`（保持词序）

3. **性能优化**：
   - 使用 `search_documents_local` 进行快速查询
   - 避免过于宽泛的查询词
   - 定期清理和重建索引

## 📚 更多文档

- **QUICKSTART.md** - 5分钟快速启动指南
- **CHANGELOG.md** - 版本更新历史

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Whoosh](https://whoosh.readthedocs.io/) - 纯Python全文搜索引擎
- [jieba](https://github.com/fxsjy/jieba) - 中文分词库
- [MCP](https://modelcontextprotocol.io/) - 模型上下文协议
- [掘金量化](https://www.myquant.cn/) - 文档数据源

---

**问题反馈**：如遇到问题，请查看故障排查章节或提交Issue。

**Star⭐**: 如果这个项目对你有帮助，欢迎给个Star！