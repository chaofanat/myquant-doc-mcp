from fastmcp import FastMCP
from core import SearchFlow
from config import MAX_RESULTS
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
import json
import os
from typing import Optional

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
    # 获取当前脚本所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file_path = os.path.join(current_dir, "web", "index.html")

    try:
        # 读取HTML文件内容
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # 如果文件不存在，返回错误信息
        error_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>错误 - 文件未找到</title>
        </head>
        <body>
            <h1>错误</h1>
            <p>找不到HTML文件: {html_file_path}</p>
            <p>请确保web/index.html文件存在。</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=404)
    except Exception as e:
        # 其他错误处理
        error_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>错误 - 服务器错误</title>
        </head>
        <body>
            <h1>错误</h1>
            <p>读取HTML文件时发生错误: {str(e)}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)



# API端点辅助 - 文档发现实现
def api_discover_documents_impl(keyword: str, limit: int = 100,
                               doc_type: str = None, language: str = None,
                               category: str = None) -> dict:
    """文档发现实现"""
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


# API端点 - 复刻MCP工具功能

@app.custom_route("/api/search", methods=["POST"])
async def api_search_documents(request: Request):
    """完整文档搜索API"""
    try:
        data = await request.json()
        keyword = data.get("keyword", "")
        max_results = data.get("max_results", MAX_RESULTS)

        result = await search_flow.full_search(keyword, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/search_boolean", methods=["POST"])
async def api_search_boolean(request: Request):
    """布尔搜索API"""
    try:
        data = await request.json()
        query_string = data.get("query_string", "")
        max_results = data.get("max_results", MAX_RESULTS)
        mode = data.get("mode", "full")
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


        result = await search_flow.boolean_search(query_string, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/search_phrase", methods=["POST"])
async def api_search_phrase(request: Request):
    """短语搜索API"""
    try:
        data = await request.json()
        phrase = data.get("phrase", "")
        max_results = data.get("max_results", MAX_RESULTS)
        mode = data.get("mode", "full")
        if mode == "full":
        # 对于完整模式，先进行完整搜索获取最新内容
        # 然后对最新索引进行短语查询
        # 注意：这里我们直接对短语进行查询
            await search_flow.full_search(phrase, 50)  # 先获取最新内容


        result = await search_flow.phrase_search(phrase, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/search_fuzzy", methods=["POST"])
async def api_search_fuzzy(request: Request):
    """模糊搜索API"""
    try:
        data = await request.json()
        term = data.get("term", "")
        max_distance = data.get("max_distance", 2)
        max_results = data.get("max_results", MAX_RESULTS)
        mode = data.get("mode", "full")
        if mode == "full":
        # 对于完整模式，先进行完整搜索获取最新内容
        # 然后对最新索引进行模糊查询
        # 注意：这里我们直接对术语进行模糊查询
            await search_flow.full_search(term, 50)  # 先获取最新内容


        result = await search_flow.fuzzy_search(term, max_distance, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/search_tag", methods=["POST"])
async def api_search_tag(request: Request):
    """标签搜索API"""
    try:
        data = await request.json()
        tag = data.get("tag", "")
        keyword = data.get("keyword", "")
        max_results = data.get("max_results", MAX_RESULTS)
        mode = data.get("mode", "full")
        if mode == "full":
        # 对于完整模式，先进行完整搜索获取最新内容
        # 然后对最新索引进行标签查询
        # 注意：这里我们直接对标签进行查询
            await search_flow.full_search(tag, 50)  # 先获取最新内容


        result = await search_flow.tag_search(tag, keyword, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/search_local", methods=["POST"])
async def api_search_documents_local(request: Request):
    """本地搜索API"""
    try:
        data = await request.json()
        keyword = data.get("keyword", "")
        max_results = data.get("max_results", MAX_RESULTS)

        result = await search_flow.search(keyword, max_results)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/stats", methods=["GET"])
async def api_get_system_stats(request: Request):
    """系统统计API"""
    try:
        result = search_flow.get_stats()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.custom_route("/api/discover", methods=["POST"])
async def api_discover_documents(request: Request):
    """文档发现API"""
    try:
        data = await request.json()
        keyword = data.get("keyword", "")
        limit = data.get("limit", 100)
        doc_type = data.get("doc_type")
        language = data.get("language")
        category = data.get("category")

        result = api_discover_documents_impl(keyword, limit, doc_type, language, category)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    app.run(
        # transport="stdio"  # 使用标准输入输出模式
        # 或者使用sse模式
        transport="sse",
        host="127.0.0.1",
        port=8001
    )
