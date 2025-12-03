from fastmcp import FastMCP
from core import SearchFlow
from config import MAX_RESULTS
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
import json

# 创建FastMCP应用实例
app = FastMCP(
    name="myquant-doc-mcp-service",
    version="1.0.0",
)

# 创建搜索流程实例
search_flow = SearchFlow()

@app.tool
async def search_documents(keyword: str, max_results: int = MAX_RESULTS) -> dict:
    """
    完整的掘金量化文档搜索，包含API调用、文档下载、索引建立和本地检索的完整流程
    确保获取最新内容并进行精准搜索

    Args:
        keyword: 搜索关键词，支持中文分词
        max_results: 最大返回结果数

    Returns:
        搜索结果，包含高亮显示和上下文，以及流程统计信息
    """
    return await search_flow.full_search(keyword, max_results)

@app.tool
async def search_boolean(query_string: str, max_results: int = MAX_RESULTS, mode: str = "full") -> dict:
    """
    掘金量化文档布尔查询搜索

    Args:
        query_string: 布尔查询表达式，如：title:"API" AND (content:"交易" OR content:"行情")
        max_results: 最大返回结果数
        mode: 搜索模式
            - "full": 完整搜索（API+下载+索引+检索），确保最新内容
            - "local": 仅本地搜索（快速，可能使用过时内容）

    Returns:
        布尔查询搜索结果
    """
    if mode == "full":
        # 对于完整模式，先进行完整搜索获取最新内容
        # 然后对最新索引进行布尔查询
        # 注意：这里我们提取关键词进行完整搜索，然后用布尔查询
        keywords = []
        import re
        # 简单提取关键词用于完整搜索
        for match in re.finditer(r'"([^"]+)"|(\w+)', query_string):
            keyword = match.group(1) or match.group(2)
            if keyword.lower() not in ['and', 'or', 'not', 'title:', 'content:']:
                keywords.append(keyword)

        if keywords:
            combined_keyword = " ".join(keywords)
            await search_flow.full_search(combined_keyword, 50)  # 先获取最新内容

    return await search_flow.boolean_search(query_string, max_results)

@app.tool
async def search_phrase(phrase: str, max_results: int = MAX_RESULTS, mode: str = "full") -> dict:
    """
    掘金量化文档精确短语搜索，保持词语顺序

    Args:
        phrase: 要精确匹配的短语
        max_results: 最大返回结果数
        mode: 搜索模式
            - "full": 完整搜索（API+下载+索引+检索），确保最新内容
            - "local": 仅本地搜索（快速，可能使用过时内容）

    Returns:
        短语匹配的搜索结果
    """
    if mode == "full":
        # 先进行完整搜索获取最新内容
        await search_flow.full_search(phrase, 50)

    return await search_flow.phrase_search(phrase, max_results)

@app.tool
async def search_fuzzy(term: str, max_distance: int = 2, max_results: int = MAX_RESULTS, mode: str = "full") -> dict:
    """
    掘金量化文档模糊搜索，支持拼写纠错

    Args:
        term: 搜索词（支持拼写错误）
        max_distance: 编辑距离（1-2）
        max_results: 最大返回结果数
        mode: 搜索模式
            - "full": 完整搜索（API+下载+索引+检索），确保最新内容
            - "local": 仅本地搜索（快速，可能使用过时内容）

    Returns:
        模糊匹配的搜索结果
    """
    if mode == "full":
        # 先进行完整搜索获取最新内容
        await search_flow.full_search(term, 50)

    return await search_flow.fuzzy_search(term, max_distance, max_results)

@app.tool
async def search_tag(tag: str, keyword: str = "", max_results: int = MAX_RESULTS, mode: str = "full") -> dict:
    """
    掘金量化文档标签过滤搜索

    Args:
        tag: 标签名称
        keyword: 可选的搜索关键词
        max_results: 最大返回结果数
        mode: 搜索模式
            - "full": 完整搜索（API+下载+索引+检索），确保最新内容
            - "local": 仅本地搜索（快速，可能使用过时内容）

    Returns:
        标签过滤的搜索结果
    """
    if mode == "full" and keyword:
        # 先进行完整搜索获取最新内容
        await search_flow.full_search(keyword, 50)

    return await search_flow.tag_search(tag, keyword, max_results)


@app.tool
async def search_documents_local(keyword: str, max_results: int = MAX_RESULTS) -> dict:
    """
    快速本地搜索（仅使用现有索引，可能使用过时内容但响应更快）
    适用于已知内容没有变化或需要快速查询的场景

    Args:
        keyword: 搜索关键词，支持中文分词
        max_results: 最大返回结果数

    Returns:
        本地搜索结果，包含高亮显示和上下文
    """
    return await search_flow.search(keyword, max_results)

@app.tool
def get_system_stats() -> dict:
    """
    获取系统统计信息

    Returns:
        系统统计信息，包括下载文档数量、索引文档数量等
    """
    return search_flow.get_stats()

@app.tool
def discover_documents(keyword: str, limit: int = 100,
                      doc_type: str = None, language: str = None,
                      category: str = None) -> dict:
    """
    发现掘金量化相关文档（仅返回文档URL和元数据，不进行内容检索）
    用于了解有哪些相关文档，但不返回具体的文档内容

    Args:
        keyword: 搜索关键词
        limit: 返回结果数量
        doc_type: 文档类型过滤 (api, tutorial, faq, quick_start)
        language: 编程语言过滤 (python, cpp, csharp, matlab)
        category: 功能分类过滤 (api, data, trading, sdk, tools)

    Returns:
        文档发现结果，包含文档URL、标题、分类等结构化信息，但不包含具体内容
    """
    # 构建过滤条件
    filters = {}
    if doc_type:
        filters['document_type'] = [doc_type]
    if language:
        filters['language'] = [language]
    if category:
        filters['category'] = [category]

    api_response = search_flow.api_service.search(keyword, limit, filters)
    urls = search_flow.api_service.extract_unique_urls(api_response)
    categories = search_flow.api_service.get_document_categories(api_response)

    # 格式化文档摘要信息
    document_summaries = []
    for hit in api_response.hits[:20]:  # 只返回前20个摘要
        # 安全处理content字段，避免None值
        content = hit.content or ""
        summary = content[:200] + "..." if len(content) > 200 else content

        document_summaries.append({
            'title': hit.title or "未知标题",
            'url': hit.url,
            'summary': summary,
            'document_type': getattr(hit, 'document_type', 'unknown'),
            'language': getattr(hit, 'language', 'unknown'),
            'relevance_score': getattr(hit, 'relevance_score', 0)
        })

    return {
        'query': keyword,
        'total_hits': len(api_response.hits),
        'document_summaries': document_summaries,
        'unique_urls': urls,
        'processing_time_ms': api_response.processing_time_ms,
        'document_categories': categories,
        'search_filters': filters,
        'estimated_total_hits': api_response.estimated_total_hits,
        'usage_note': '此工具仅用于发现相关文档。如需获取具体内容和详细搜索，请使用 search_documents 等搜索工具'
    }

# 添加Web测试界面
@app.custom_route("/", methods=["GET"])
async def test_interface(request: Request):
    """Web测试界面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyQuant MCP 工具测试界面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .tool-section {
            border: 1px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tool-title {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .form-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 80px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        }
        .loading {
            color: #007bff;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        .success {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        .quick-test {
            background-color: #28a745;
            margin-left: 10px;
        }
        .quick-test:hover {
            background-color: #1e7e34;
        }
    </style>
</head>
<body>
    <h1>🔍 MyQuant MCP 工具测试界面</h1>
    <p>测试掘金量化文档搜索MCP服务的各种工具功能</p>

    <!-- 1. 完整搜索 -->
    <div class="tool-section">
        <div class="tool-title">📚 search_documents - 完整文档搜索</div>
        <div class="form-group">
            <label>搜索关键词:</label>
            <input type="text" id="search_keyword" placeholder="例如: API, 数据查询, 交易策略" value="API">
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="search_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_documents')">查看使用方法</button>
        <div id="search_documents_result" class="result" style="display:none;"></div>
    </div>

    <!-- 2. 布尔搜索 -->
    <div class="tool-section">
        <div class="tool-title">🔗 search_boolean - 布尔查询搜索</div>
        <div class="form-group">
            <label>布尔查询表达式:</label>
            <textarea id="boolean_query_string" placeholder="例如: title:'API' AND (content:'交易' OR content:'行情')">title:API AND content:接口</textarea>
        </div>
        <div class="form-group">
            <label>搜索模式:</label>
            <select id="boolean_mode">
                <option value="full">完整搜索（获取最新内容）</option>
                <option value="local">本地搜索（快速）</option>
            </select>
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="boolean_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_boolean')">查看使用方法</button>
        <div id="search_boolean_result" class="result" style="display:none;"></div>
    </div>

    <!-- 3. 短语搜索 -->
    <div class="tool-section">
        <div class="tool-title">📝 search_phrase - 短语精确搜索</div>
        <div class="form-group">
            <label>精确短语:</label>
            <input type="text" id="phrase_phrase" placeholder="例如: 数据查询函数" value="API接口">
        </div>
        <div class="form-group">
            <label>搜索模式:</label>
            <select id="phrase_mode">
                <option value="full">完整搜索（获取最新内容）</option>
                <option value="local">本地搜索（快速）</option>
            </select>
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="phrase_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_phrase')">查看使用方法</button>
        <div id="search_phrase_result" class="result" style="display:none;"></div>
    </div>

    <!-- 4. 模糊搜索 -->
    <div class="tool-section">
        <div class="tool-title">🔍 search_fuzzy - 模糊搜索</div>
        <div class="form-group">
            <label>搜索词（支持拼写错误）:</label>
            <input type="text" id="fuzzy_term" placeholder="例如: APi（支持拼写错误）" value="API">
        </div>
        <div class="form-group">
            <label>编辑距离 (1-2):</label>
            <input type="number" id="fuzzy_max_distance" value="2" min="1" max="3">
        </div>
        <div class="form-group">
            <label>搜索模式:</label>
            <select id="fuzzy_mode">
                <option value="full">完整搜索（获取最新内容）</option>
                <option value="local">本地搜索（快速）</option>
            </select>
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="fuzzy_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_fuzzy')">查看使用方法</button>
        <div id="search_fuzzy_result" class="result" style="display:none;"></div>
    </div>

    <!-- 5. 标签搜索 -->
    <div class="tool-section">
        <div class="tool-title">🏷️ search_tag - 标签过滤搜索</div>
        <div class="form-group">
            <label>标签名称:</label>
            <input type="text" id="tag_tag" placeholder="例如: tutorial, api, python" value="api">
        </div>
        <div class="form-group">
            <label>可选关键词:</label>
            <input type="text" id="tag_keyword" placeholder="例如: 数据查询" value="">
        </div>
        <div class="form-group">
            <label>搜索模式:</label>
            <select id="tag_mode">
                <option value="full">完整搜索（获取最新内容）</option>
                <option value="local">本地搜索（快速）</option>
            </select>
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="tag_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_tag')">查看使用方法</button>
        <div id="search_tag_result" class="result" style="display:none;"></div>
    </div>

    <!-- 6. 快速本地搜索 -->
    <div class="tool-section">
        <div class="tool-title">⚡ search_documents_local - 快速本地搜索</div>
        <div class="form-group">
            <label>搜索关键词:</label>
            <input type="text" id="local_keyword" placeholder="例如: API, 数据查询" value="API">
        </div>
        <div class="form-group">
            <label>最大结果数:</label>
            <input type="number" id="local_max_results" value="10" min="1" max="50">
        </div>
        <button onclick="showUsageInfo('search_documents_local')">查看使用方法</button>
        <div id="search_documents_local_result" class="result" style="display:none;"></div>
    </div>

    <!-- 7. 系统统计 -->
    <div class="tool-section">
        <div class="tool-title">📊 get_system_stats - 获取系统统计信息</div>
        <button onclick="showUsageInfo('get_system_stats')">查看使用方法</button>
        <div id="get_system_stats_result" class="result" style="display:none;"></div>
    </div>

    <!-- 8. 文档发现 -->
    <div class="tool-section">
        <div class="tool-title">🔎 discover_documents - 发现相关文档</div>
        <div class="form-group">
            <label>搜索关键词:</label>
            <input type="text" id="discover_keyword" placeholder="例如: Python, 数据分析" value="Python">
        </div>
        <div class="form-group">
            <label>返回结果数量:</label>
            <input type="number" id="discover_limit" value="20" min="1" max="100">
        </div>
        <div class="form-group">
            <label>文档类型过滤 (可选):</label>
            <select id="discover_doc_type">
                <option value="">全部</option>
                <option value="api">API文档</option>
                <option value="tutorial">教程</option>
                <option value="faq">FAQ</option>
                <option value="quick_start">快速开始</option>
            </select>
        </div>
        <div class="form-group">
            <label>编程语言过滤 (可选):</label>
            <select id="discover_language">
                <option value="">全部</option>
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
                <option value="matlab">MATLAB</option>
            </select>
        </div>
        <div class="form-group">
            <label>功能分类过滤 (可选):</label>
            <select id="discover_category">
                <option value="">全部</option>
                <option value="api">API</option>
                <option value="data">数据</option>
                <option value="trading">交易</option>
                <option value="sdk">SDK</option>
                <option value="tools">工具</option>
            </select>
        </div>
        <button onclick="showUsageInfo('discover_documents')">查看使用方法</button>
        <div id="discover_documents_result" class="result" style="display:none;"></div>
    </div>

    <script>
        function showUsageInfo(toolName) {
            const resultDiv = document.getElementById(toolName + '_result');
            resultDiv.style.display = 'block';
            resultDiv.className = 'result';

            const usageInfo = generateUsageInfo(toolName);
            resultDiv.textContent = usageInfo;
        }

        function generateUsageInfo(toolName) {
            switch (toolName) {
                case 'search_documents':
                    return `🔧 MCP工具调用示例:

在支持MCP的客户端中使用:
{
  "tool": "search_documents",
  "arguments": {
    "keyword": "API",
    "max_results": 10
  }
}

📋 功能说明:
- 完整的掘金量化文档搜索
- 包含API调用、文档下载、索引建立和本地检索
- 确保获取最新内容并进行精准搜索

⚡ 性能优化:
- jieba分词器已预初始化
- 智能跳过已存在的文档
- 增量索引更新`;

                case 'search_boolean':
                    return `🔧 MCP工具调用示例:

{
  "tool": "search_boolean",
  "arguments": {
    "query_string": "title:API AND content:接口",
    "max_results": 10,
    "mode": "full"
  }
}

📋 功能说明:
- 支持复杂的布尔查询表达式
- 字段限定搜索 (title:, content:)
- 逻辑操作符 (AND, OR, NOT)
- 模式选择: full(最新内容) 或 local(快速)`;

                case 'search_phrase':
                    return `🔧 MCP工具调用示例:

{
  "tool": "search_phrase",
  "arguments": {
    "phrase": "API接口",
    "max_results": 10,
    "mode": "local"
  }
}

📋 功能说明:
- 精确短语搜索，保持词语顺序
- 适用于查找固定术语和专有名词
- 支持完整模式和本地快速模式`;

                case 'search_fuzzy':
                    return `🔧 MCP工具调用示例:

{
  "tool": "search_fuzzy",
  "arguments": {
    "term": "API",
    "max_distance": 2,
    "max_results": 10,
    "mode": "local"
  }
}

📋 功能说明:
- 模糊搜索，支持拼写纠错
- 可配置编辑距离(1-2)
- 处理用户输入错误`;

                case 'search_tag':
                    return `🔧 MCP工具调用示例:

{
  "tool": "search_tag",
  "arguments": {
    "tag": "api",
    "keyword": "数据查询",
    "max_results": 10,
    "mode": "local"
  }
}

📋 功能说明:
- 基于标签的过滤搜索
- 可结合关键词进行二次筛选
- 支持多种标签类型: tutorial, api, python等`;

                case 'search_documents_local':
                    return `🔧 MCP工具调用示例:

{
  "tool": "search_documents_local",
  "arguments": {
    "keyword": "API",
    "max_results": 10
  }
}

📋 功能说明:
- 快速本地搜索，仅使用现有索引
- 响应时间 ~0.02秒
- 适用于内容没有变化的场景`;

                case 'get_system_stats':
                    return `🔧 MCP工具调用示例:

{
  "tool": "get_system_stats",
  "arguments": {}
}

📋 功能说明:
- 获取系统统计信息
- 包含下载文档数量
- 索引文档数量
- 缓存状态等信息`;

                case 'discover_documents':
                    return `🔧 MCP工具调用示例:

{
  "tool": "discover_documents",
  "arguments": {
    "keyword": "Python",
    "limit": 20,
    "doc_type": "api",
    "language": "python",
    "category": "api"
  }
}

📋 功能说明:
- 发现掘金量化相关文档
- 仅返回URL和元数据，不含具体内容
- 支持多种过滤器:
  • doc_type: api, tutorial, faq, quick_start
  • language: python, cpp, csharp, matlab
  • category: api, data, trading, sdk, tools`;

                default:
                    return '工具信息获取中...';
            }
        }

        // 页面加载时显示欢迎信息
        window.onload = function() {
            console.log('🚀 MyQuant MCP 工具展示界面已加载');
            console.log('💡 这是一个MCP工具的功能演示界面');
            console.log('📡 实际工具调用需要在支持MCP协议的客户端中进行');
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    app.run(
        # transport="stdio"  # 使用标准输入输出模式
        # 或者使用sse模式
        transport="sse",
        host="127.0.0.1",
        port=8001
    )
