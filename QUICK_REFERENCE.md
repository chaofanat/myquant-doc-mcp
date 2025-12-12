# 快速参考卡片

## 🚀 一键启动

```bash
# 1. 激活环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. 测试搜索
python quick_test.py

# 3. 重建索引（如需要）
python rebuild_index.py
```

## 🔧 Claude Desktop 配置

### Windows
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

### macOS/Linux
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

**配置文件位置**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

## 💬 使用示例

| 功能 | 示例提示词 |
|------|-----------|
| 基础搜索 | "搜索掘金量化关于'交易接口'的文档" |
| 快速搜索 | "快速搜索本地索引中关于'K线数据'的内容" |
| 布尔查询 | "使用布尔查询: title:\"API\" AND content:\"Python\"" |
| 短语搜索 | "精确搜索短语'实时行情接口'" |
| 模糊搜索 | "模糊搜索'jiaoyi'（可能拼写错误）" |
| 标签搜索 | "搜索标签为'API'的文档" |
| 发现文档 | "发现关于'策略回测'的相关文档" |
| 系统统计 | "查看文档搜索系统的统计信息" |

## 🛠️ 常用命令

```bash
# 测试搜索功能
python quick_test.py

# 全面测试
python test_search.py

# 重建索引
python rebuild_index.py

# 初始化（首次使用）
python init.py

# 查看统计
python -c "from core import SearchFlow; print(SearchFlow().get_stats())"

# 验证 MCP 库
python -c "import mcp; print('MCP OK')"
```

## 🔍 8 个可用工具

1. **search_documents** - 完整搜索（API+下载+索引+检索）
2. **search_documents_local** - 快速本地搜索
3. **search_boolean** - 布尔查询（AND/OR/NOT）
4. **search_phrase** - 精确短语搜索
5. **search_fuzzy** - 模糊搜索（拼写纠错）
6. **search_tag** - 标签过滤搜索
7. **discover_documents** - 文档发现（返回元数据）
8. **get_system_stats** - 系统统计信息

## 📊 系统状态

```bash
# 检查索引
ls data/index  # macOS/Linux
dir data\index # Windows

# 检查文档数量
ls data/docs/*.html | wc -l  # macOS/Linux
dir data\docs\*.html | find /c ".html"  # Windows

# 查看日志
tail -f *.log  # macOS/Linux
type *.log  # Windows
```

## ⚡ 故障排查

| 问题 | 解决方案 |
|------|----------|
| 无法连接 MCP | 检查配置文件路径，重启 Claude Desktop |
| 搜索无结果 | 运行 `python rebuild_index.py` |
| 索引失败 | 运行 `python init.py` 下载文档 |
| 路径错误 | 使用双反斜杠 `\\` 或单斜杠 `/` |

## 📈 性能指标

- **索引文档**: 409 个
- **搜索速度**: 0.05-0.3 秒
- **质量通过率**: 100%
- **覆盖率**: 200-400 结果/查询

## 🔄 定期维护

```bash
# 每周运行一次
cd /path/to/myquant-doc-mcp
source venv/bin/activate  # 或 venv\Scripts\activate
python init.py
python rebuild_index.py
```

## 📚 更多文档

- **README.md** - 项目说明
- **QUICKSTART.md** - 快速启动指南（详细）
- **CLAUDE_CONFIG.md** - 配置指南（详细）
- **CHANGELOG.md** - 更新日志
- **PROJECT_SUMMARY.md** - 项目总结

## 🆘 获取帮助

1. 查看日志文件
2. 运行 `python test_search.py`
3. 查看 GitHub Issues
4. 阅读详细文档

---

**提示**: 将此文件打印或保存为书签，方便日常使用！