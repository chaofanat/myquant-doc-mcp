# 更新日志 (CHANGELOG)

本文档记录 myquant-doc-mcp 项目的重要变更。

## [2.0.0] - 2024-12-12

### 🚀 重大更新

#### 架构迁移
- **从 fastmcp 迁移到标准 mcp 库**
  - 移除 fastmcp、uvicorn、fastapi 等 SSE 模式依赖
  - 采用标准 MCP 协议的 stdio 传输模式
  - 完全兼容 Claude Desktop 和其他 MCP 客户端
  - 移除 Web 测试界面（不再需要 HTTP 服务器）

#### 搜索引擎优化

**1. 中文分词增强**
- 添加 70+ 专业术语到 jieba 词典
  - 量化交易术语：掘金量化、策略、回测、行情、交易、接口
  - 数据类型：K线、分笔、逐笔、委托、成交、持仓
  - 技术指标：MACD、KDJ、RSI、布林带、均线
  - 金融品种：股票、期货、期权、基金、债券
  - 编程语言：Python、C++、C#、MATLAB
- 使用 `jieba.cut_for_search()` 搜索模式，提供更细粒度的分词
- 改进 Token 位置记录，完美支持高亮功能

**2. 多字段搜索**
- 从单字段（content）扩展到多字段搜索
  - title（标题）- 权重 3.0
  - headings（副标题）- 权重 2.0
  - tags（标签）- 权重 2.5
  - code_blocks（代码块）- 权重 1.5
  - content（正文）- 权重 1.0
- 使用 BM25F 评分算法，支持字段加权

**3. 搜索策略改进**
- 使用 OrGroup 组合多个搜索词，扩大搜索范围
- 布尔查询支持智能降级处理
- 短语搜索支持多字段匹配
- 模糊搜索支持多字段匹配
- 所有搜索返回更多候选结果（max_results * 2）

**4. HTML 内容提取增强**
- 支持多种内容容器识别（8+ 种常见容器类名）
- 提取段落（p）、列表（li）、表格（table）等多种结构
- 自动使用 jieba.analyse 提取关键词作为标签
- 清理多余空白和特殊字符
- 去重处理，避免重复内容

**5. 高亮功能修复**
- 使用 Whoosh 内置 Highlighter
- 配置 ContextFragmenter 显示上下文（300 字符，前后各 50 字符）
- 使用 HtmlFormatter 格式化高亮（<mark> 标签）
- 支持多字段高亮（title、content、headings）

### ✨ 新增功能

- **rebuild_index.py**: 索引重建脚本
- **test_search.py**: 全面的搜索测试套件
  - 基础关键词搜索测试
  - 布尔查询测试
  - 短语搜索测试
  - 模糊搜索测试
  - 标签搜索测试
  - 搜索质量评估
- **quick_test.py**: 快速搜索测试脚本
- **CLAUDE_CONFIG.md**: 详细的 Claude Desktop 配置指南
- **CHANGELOG.md**: 本更新日志

### 📊 性能提升

- **搜索相关性**: 质量测试通过率从未知提升到 **100%**
- **搜索覆盖率**: 
  - "交易接口" - 387 个结果（提升显著）
  - "行情数据" - 381 个结果
  - "Python SDK" - 242 个结果
  - "策略回测" - 268 个结果
- **搜索速度**: 平均响应时间 0.05-0.3 秒
- **索引效率**: 409 个文档，约 2.5 分钟完成索引

### 🔧 技术改进

- 改进 Token 生成器，正确设置 positions 和 chars 属性
- 使用 Every() 查询替代 Term("url", "") 获取所有文档
- 优化查询解析器，支持更复杂的查询语法
- 增强错误处理和日志记录
- 移除未使用的导入和代码

### 📝 文档更新

- **README.md**: 
  - 更新为 stdio 模式说明
  - 添加 Claude Desktop 配置示例
  - 添加工作原理说明
  - 添加目录结构说明
- **CLAUDE_CONFIG.md**: 详细的配置指南
  - 多平台配置示例（Windows/macOS/Linux）
  - 故障排查指南
  - 高级配置选项
  - 使用示例

### 🐛 问题修复

- 修复 Tokenizer 类名变更导致的索引不兼容问题
- 修复 URL 映射格式读取错误
- 修复高亮功能中的位置信息缺失问题
- 修复布尔查询解析失败时的降级处理
- 修复多字段查询的类型检查警告

### 🔄 依赖变更

**移除**:
- fastmcp>=0.2
- uvicorn>=0.20
- python-multipart>=0.0.6

**新增**:
- mcp>=1.0.0

**保留**:
- whoosh>=2.7
- requests>=2.30
- beautifulsoup4>=4.12
- jieba>=0.42
- pydantic>=2.0
- aiohttp>=3.8
- pytest>=7.0
- pytest-asyncio>=0.21.0
- pytest-cov>=4.0
- python-dotenv>=1.0

### ⚠️ 破坏性变更

- **不再支持 SSE 模式**: 只支持 stdio 模式
- **移除 Web 界面**: /api/* 和 / 路由不再可用
- **索引格式变更**: 旧索引需要重建（Tokenizer 类名变更）
- **配置方式变更**: 需要在 Claude Desktop 中配置，不再通过环境变量

### 📦 迁移指南

从 1.x 迁移到 2.0:

1. **备份数据**（可选）：
   ```bash
   cp -r data data.backup
   ```

2. **更新依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **删除旧索引**：
   ```bash
   rm -rf data/index/*
   ```

4. **重建索引**：
   ```bash
   python rebuild_index.py
   ```

5. **配置 Claude Desktop**：
   参考 CLAUDE_CONFIG.md

6. **测试**：
   ```bash
   python test_search.py
   ```

### 🎯 测试结果

**索引统计**:
- 文档总数: 409
- 索引大小: 约 10MB
- 构建时间: 约 2.5 分钟

**搜索质量测试**:
- 测试用例: 4 个
- 通过率: 100%
- 平均相关性: 56.25%

**性能测试**:
- 平均查询时间: 0.15 秒
- 最快查询: 0.04 秒
- 最慢查询: 0.33 秒

### 🙏 致谢

感谢以下技术和工具：
- [Whoosh](https://whoosh.readthedocs.io/) - 纯 Python 全文搜索引擎
- [jieba](https://github.com/fxsjy/jieba) - 优秀的中文分词库
- [MCP](https://modelcontextprotocol.io/) - 模型上下文协议
- [Claude Desktop](https://claude.ai/download) - AI 助手应用

---

## [1.0.0] - 2024-12-03

### 初始版本

- 基于 fastmcp 框架的 SSE 模式 MCP 服务
- 基础的 Whoosh 搜索功能
- 掘金量化 API 集成
- 智能文档下载器
- Web 测试界面
- 8 个搜索工具

---

## 版本说明

版本号格式: MAJOR.MINOR.PATCH

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

---

**注**: 本项目遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/) 规范。