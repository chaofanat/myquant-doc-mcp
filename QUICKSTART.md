# 快速启动指南

本指南帮助你在 5 分钟内快速启动 myquant-doc-mcp 服务并在 Claude Desktop 中使用。

## 📋 前提条件

- Python 3.7+ 已安装
- Claude Desktop 已安装
- 网络连接正常

## 🚀 快速安装（5 步完成）

### 步骤 1: 克隆项目

```bash
git clone <repository-url>
cd myquant-doc-mcp
```

或者如果你已经有项目文件：

```bash
cd D:\workspace\myquant-doc-mcp  # Windows
# cd /path/to/myquant-doc-mcp    # macOS/Linux
```

### 步骤 2: 创建虚拟环境并安装依赖

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤 3: 构建搜索索引

如果数据目录已经有文档（检查 `data/docs/` 目录），直接重建索引：

```bash
python rebuild_index.py
```

如果没有文档，先运行初始化脚本：

```bash
python init.py
```

**预期输出:**
```
2024-12-12 - INFO - 开始重建索引...
2024-12-12 - INFO - 找到 410 个文档记录
2024-12-12 - INFO - 有效文档: 409
2024-12-12 - INFO - 索引重建完成！
2024-12-12 - INFO - 总文档数: 409
2024-12-12 - INFO - 成功索引: 409
```

⏱️ **预计时间**: 2-3 分钟

### 步骤 4: 测试搜索功能

```bash
python quick_test.py
```

**预期输出:**
```
============================================================
搜索: 交易接口
============================================================
总命中数: 387

前3个结果:

1. 算法交易 - 掘金量化
   评分: 29.75
   ...
```

如果看到搜索结果，说明索引构建成功！✅

### 步骤 5: 配置 Claude Desktop

#### 5.1 找到配置文件

打开 Claude Desktop 配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

💡 **快速打开方式 (Windows)**:
```cmd
notepad %APPDATA%\Claude\claude_desktop_config.json
```

💡 **快速打开方式 (macOS)**:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### 5.2 添加配置

**Windows 配置:**
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

**macOS/Linux 配置:**
```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/Users/你的用户名/workspace/myquant-doc-mcp/venv/bin/python",
      "args": [
        "/Users/你的用户名/workspace/myquant-doc-mcp/mcp_server.py"
      ]
    }
  }
}
```

⚠️ **重要**: 
- 将路径替换为你的实际项目路径
- Windows 路径使用双反斜杠 `\\` 或单斜杠 `/`
- 确保路径指向虚拟环境中的 Python

#### 5.3 获取正确的路径

不确定路径？运行以下命令获取：

**Windows:**
```cmd
cd D:\workspace\myquant-doc-mcp
echo %CD%\venv\Scripts\python.exe
echo %CD%\mcp_server.py
```

**macOS/Linux:**
```bash
cd /path/to/myquant-doc-mcp
echo $(pwd)/venv/bin/python
echo $(pwd)/mcp_server.py
```

#### 5.4 重启 Claude Desktop

1. **完全退出** Claude Desktop（不是最小化）
2. 重新打开 Claude Desktop
3. 等待 3-5 秒，让 MCP 服务连接

## ✅ 验证安装

在 Claude Desktop 中发送以下消息：

```
请搜索掘金量化关于"交易接口"的文档
```

**成功标志:**
- Claude 调用了 `search_documents` 工具
- 返回了搜索结果
- 结果包含标题、URL、评分等信息

## 🎯 快速使用示例

### 1. 基础搜索
```
搜索掘金量化关于"Python API"的文档
```

### 2. 快速本地搜索
```
快速搜索本地索引中关于"K线数据"的内容
```

### 3. 查看系统统计
```
查看掘金量化文档搜索系统的统计信息
```

### 4. 布尔查询
```
使用布尔查询: title:"API" AND content:"Python"
```

### 5. 发现文档
```
发现关于"策略回测"的相关文档
```

## 🔧 常见问题

### Q1: Claude Desktop 无法连接 MCP 服务

**检查清单:**
1. ✅ 配置文件 JSON 格式正确（无逗号错误）
2. ✅ Python 路径正确（使用虚拟环境中的 Python）
3. ✅ mcp_server.py 路径正确
4. ✅ 已完全重启 Claude Desktop
5. ✅ 虚拟环境中已安装 mcp 库

**验证配置:**
```bash
# 验证 Python 路径
D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe --version

# 验证 MCP 库
D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe -c "import mcp; print('MCP OK')"

# 测试服务器
D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe mcp_server.py
```

### Q2: 搜索没有结果

**解决方案:**
```bash
# 重建索引
python rebuild_index.py

# 测试搜索
python quick_test.py
```

### Q3: 索引构建失败

**原因:** 没有文档文件

**解决方案:**
```bash
# 运行初始化脚本下载文档
python init.py
```

### Q4: Windows 路径问题

**错误配置 ❌:**
```json
"command": "D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe"
```

**正确配置 ✅:**
```json
"command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe"
```
或
```json
"command": "D:/workspace/myquant-doc-mcp/venv/Scripts/python.exe"
```

## 📊 系统要求

### 最低配置
- CPU: 双核
- RAM: 2GB
- 磁盘: 500MB（索引 + 文档）
- Python: 3.7+

### 推荐配置
- CPU: 四核+
- RAM: 4GB+
- 磁盘: 1GB+
- Python: 3.9+

## 🔄 日常使用

### 更新索引（建议每周一次）

```bash
cd D:\workspace\myquant-doc-mcp  # 你的项目路径
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

python init.py                   # 下载新文档
python rebuild_index.py          # 重建索引
```

### 查看统计信息

```bash
python -c "from core import SearchFlow; import json; print(json.dumps(SearchFlow().get_stats(), indent=2, ensure_ascii=False))"
```

## 📚 下一步

- 📖 阅读 [README.md](README.md) 了解更多功能
- 🔧 查看 [CLAUDE_CONFIG.md](CLAUDE_CONFIG.md) 了解详细配置
- 📝 查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史
- 🧪 运行 `python test_search.py` 进行全面测试

## 💡 提示

1. **首次使用会下载大量文档**，需要 5-10 分钟
2. **索引构建**需要 2-3 分钟
3. **搜索速度**通常在 0.1-0.3 秒
4. **定期更新索引**以获取最新文档
5. **保持虚拟环境激活**在开发时

## 🆘 获取帮助

遇到问题？

1. 查看日志文件（项目根目录）
2. 运行 `python test_search.py` 诊断问题
3. 查看 GitHub Issues
4. 阅读详细文档

---

**恭喜！🎉 你已经成功设置 myquant-doc-mcp 服务！**

现在可以在 Claude Desktop 中享受强大的掘金量化文档搜索功能了。