# Claude Desktop 配置指南

本文档详细说明如何在 Claude Desktop 中配置 myquant-doc-mcp 服务。

## 前提条件

1. 已安装 Claude Desktop
2. 已完成 myquant-doc-mcp 的安装和索引构建
3. Python 虚拟环境已激活并安装所有依赖

## 配置步骤

### 1. 找到配置文件位置

Claude Desktop 的 MCP 配置文件位置因操作系统而异：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. 编辑配置文件

打开 `claude_desktop_config.json` 文件（如果不存在则创建），添加 myquant-doc-mcp 服务配置。

#### Windows 配置示例

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

**注意事项**:
- 路径中使用双反斜杠 `\\` 或单斜杠 `/`
- 确保 Python 解释器路径指向虚拟环境中的 python.exe
- 确保 mcp_server.py 的路径正确

#### macOS/Linux 配置示例

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

**注意事项**:
- 使用绝对路径
- 确保虚拟环境中的 python 可执行文件有执行权限
- 可以使用 `which python` (在虚拟环境中) 来确认 Python 路径

### 3. 验证路径

在配置前，请验证路径是否正确：

#### Windows
```cmd
D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe --version
D:\workspace\myquant-doc-mcp\venv\Scripts\python.exe D:\workspace\myquant-doc-mcp\mcp_server.py --help
```

#### macOS/Linux
```bash
/path/to/myquant-doc-mcp/venv/bin/python --version
/path/to/myquant-doc-mcp/venv/bin/python /path/to/myquant-doc-mcp/mcp_server.py --help
```

### 4. 重启 Claude Desktop

配置文件修改后，需要**完全重启** Claude Desktop：

1. 退出 Claude Desktop（确保完全关闭，不只是最小化）
2. 重新打开 Claude Desktop
3. 等待 MCP 服务连接（首次启动可能需要几秒钟）

## 验证配置

### 1. 检查 MCP 连接状态

在 Claude Desktop 中，查看底部状态栏：
- 应该看到 MCP 服务器已连接的指示
- 可能显示 "myquant-doc" 或类似标识

### 2. 测试工具调用

在 Claude Desktop 的对话中测试以下命令：

```
请帮我搜索掘金量化关于"交易接口"的文档
```

如果配置成功，Claude 应该能够：
1. 识别 myquant-doc 服务
2. 调用 search_documents 工具
3. 返回搜索结果

### 3. 查看可用工具

询问 Claude:
```
你可以使用哪些掘金量化文档搜索工具？
```

Claude 应该能列出以下工具：
- search_documents - 完整文档搜索
- search_documents_local - 快速本地搜索
- search_boolean - 布尔查询
- search_phrase - 精确短语搜索
- search_fuzzy - 模糊搜索
- search_tag - 标签搜索
- discover_documents - 文档发现
- get_system_stats - 系统统计

## 故障排查

### 问题1: Claude Desktop 无法连接 MCP 服务

**症状**: 底部状态栏显示 MCP 服务未连接

**解决方案**:
1. 检查配置文件 JSON 格式是否正确（使用 JSON 验证器）
2. 确认 Python 路径是否正确
3. 确认 mcp_server.py 路径是否正确
4. 检查虚拟环境是否包含所有依赖：
   ```bash
   pip list | grep mcp
   ```
5. 查看 Claude Desktop 日志（通常在用户目录下的 `.claude` 文件夹）

### 问题2: 工具调用失败

**症状**: Claude 尝试调用工具但返回错误

**解决方案**:
1. 确认索引已构建：
   ```bash
   python rebuild_index.py
   ```
2. 检查数据目录是否存在：
   ```bash
   ls data/index  # macOS/Linux
   dir data\index # Windows
   ```
3. 手动测试 MCP 服务器：
   ```bash
   python mcp_server.py
   ```
4. 查看日志文件（项目根目录）

### 问题3: Windows 路径问题

**症状**: 配置文件中的路径无法识别

**解决方案**:
1. 使用双反斜杠：`D:\\workspace\\...`
2. 或使用单斜杠：`D:/workspace/...`
3. 避免使用单反斜杠：`D:\workspace\...` （会被转义）

### 问题4: 权限问题 (macOS/Linux)

**症状**: 无法执行 Python 或脚本

**解决方案**:
```bash
chmod +x /path/to/venv/bin/python
chmod +x /path/to/mcp_server.py
```

## 高级配置

### 配置多个 MCP 服务

如果需要同时配置多个 MCP 服务：

```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe",
      "args": ["D:\\workspace\\myquant-doc-mcp\\mcp_server.py"]
    },
    "another-service": {
      "command": "/path/to/another/service",
      "args": ["--some-option"]
    }
  }
}
```

### 配置环境变量

如果需要为 MCP 服务设置环境变量：

```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe",
      "args": ["D:\\workspace\\myquant-doc-mcp\\mcp_server.py"],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

## 使用示例

配置成功后，可以在 Claude Desktop 中这样使用：

### 基础搜索
```
搜索掘金量化关于"Python API"的文档
```

### 快速本地搜索
```
快速搜索本地索引中关于"K线数据"的内容
```

### 布尔查询
```
使用布尔查询搜索: title:"API" AND content:"交易"
```

### 系统统计
```
查看掘金量化文档搜索系统的统计信息
```

### 文档发现
```
发现关于"策略回测"的相关文档，但不需要具体内容
```

## 更新和维护

### 更新索引

定期更新索引以获取最新文档：

```bash
cd D:\workspace\myquant-doc-mcp
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

python rebuild_index.py
```

### 更新依赖

当项目依赖更新时：

```bash
pip install -r requirements.txt --upgrade
```

之后重启 Claude Desktop。

## 支持

如遇到问题：

1. 查看项目日志文件
2. 运行测试脚本：`python test_search.py`
3. 查看 GitHub Issues
4. 检查 README.md 文档

## 附录：完整配置示例

### Windows 完整示例

```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "D:\\workspace\\myquant-doc-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "D:\\workspace\\myquant-doc-mcp\\mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### macOS 完整示例

```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/Users/username/workspace/myquant-doc-mcp/venv/bin/python",
      "args": [
        "/Users/username/workspace/myquant-doc-mcp/mcp_server.py"
      ],
      "env": {
        "LANG": "en_US.UTF-8"
      }
    }
  }
}
```

### Linux 完整示例

```json
{
  "mcpServers": {
    "myquant-doc": {
      "command": "/home/username/workspace/myquant-doc-mcp/venv/bin/python",
      "args": [
        "/home/username/workspace/myquant-doc-mcp/mcp_server.py"
      ],
      "env": {
        "LANG": "en_US.UTF-8"
      }
    }
  }
}
```

---

**注意**: 请根据你的实际安装路径修改配置文件中的路径。