import asyncio
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from config import MAX_RESULTS
from core import SearchFlow
from utils import logger

# 创建MCP Server实例
server = Server("myquant-doc-mcp-service")

# 创建搜索流程实例
search_flow = SearchFlow()


# 注册工具列表
@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="search_documents",
            description="完整的掘金量化文档搜索，包含API调用、文档下载、索引建立和本地检索的完整流程，确保获取最新内容并进行精准搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，支持中文分词",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="search_boolean",
            description="掘金量化文档布尔查询搜索，支持AND、OR、NOT等逻辑操作符",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_string": {
                        "type": "string",
                        "description": '布尔查询表达式，如：title:"API" AND (content:"交易" OR content:"行情")',
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                    "mode": {
                        "type": "string",
                        "description": "搜索模式：full（完整搜索，确保最新内容）或 local（仅本地搜索，快速但可能使用过时内容）",
                        "enum": ["full", "local"],
                        "default": "full",
                    },
                },
                "required": ["query_string"],
            },
        ),
        Tool(
            name="search_phrase",
            description="掘金量化文档精确短语搜索，保持词语顺序",
            inputSchema={
                "type": "object",
                "properties": {
                    "phrase": {"type": "string", "description": "要精确匹配的短语"},
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                    "mode": {
                        "type": "string",
                        "description": "搜索模式：full（完整搜索）或 local（仅本地搜索）",
                        "enum": ["full", "local"],
                        "default": "full",
                    },
                },
                "required": ["phrase"],
            },
        ),
        Tool(
            name="search_fuzzy",
            description="掘金量化文档模糊搜索，支持拼写纠错",
            inputSchema={
                "type": "object",
                "properties": {
                    "term": {"type": "string", "description": "搜索词（支持拼写错误）"},
                    "max_distance": {
                        "type": "integer",
                        "description": "编辑距离（1-2）",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 2,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                    "mode": {
                        "type": "string",
                        "description": "搜索模式：full（完整搜索）或 local（仅本地搜索）",
                        "enum": ["full", "local"],
                        "default": "full",
                    },
                },
                "required": ["term"],
            },
        ),
        Tool(
            name="search_tag",
            description="掘金量化文档标签过滤搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "标签名称"},
                    "keyword": {
                        "type": "string",
                        "description": "可选的搜索关键词",
                        "default": "",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                    "mode": {
                        "type": "string",
                        "description": "搜索模式：full（完整搜索）或 local（仅本地搜索）",
                        "enum": ["full", "local"],
                        "default": "full",
                    },
                },
                "required": ["tag"],
            },
        ),
        Tool(
            name="search_documents_local",
            description="快速本地搜索（仅使用现有索引，可能使用过时内容但响应更快），适用于已知内容没有变化或需要快速查询的场景",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，支持中文分词",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大返回结果数",
                        "default": MAX_RESULTS,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_system_stats",
            description="获取系统统计信息，包括下载文档数量、索引文档数量等",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="discover_documents",
            description="发现掘金量化相关文档（仅返回文档URL和元数据，不进行内容检索），用于了解有哪些相关文档，但不返回具体的文档内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 100,
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "文档类型过滤 (api, tutorial, faq, quick_start)",
                        "enum": ["api", "tutorial", "faq", "quick_start"],
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言过滤 (python, cpp, csharp, matlab)",
                        "enum": ["python", "cpp", "csharp", "matlab"],
                    },
                    "category": {
                        "type": "string",
                        "description": "功能分类过滤 (api, data, trading, sdk, tools)",
                        "enum": ["api", "data", "trading", "sdk", "tools"],
                    },
                },
                "required": ["keyword"],
            },
        ),
    ]


# 处理工具调用
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """处理工具调用请求"""
    try:
        result = None

        if name == "search_documents":
            keyword = arguments.get("keyword", "")
            max_results = arguments.get("max_results", MAX_RESULTS)
            result = await search_flow.full_search(keyword, max_results)

        elif name == "search_boolean":
            query_string = arguments.get("query_string", "")
            max_results = arguments.get("max_results", MAX_RESULTS)
            mode = arguments.get("mode", "full")

            if mode == "full":
                # 提取关键词进行完整搜索
                keywords = []
                import re

                for match in re.finditer(r'"([^"]+)"|(\w+)', query_string):
                    keyword = match.group(1) or match.group(2)
                    if keyword.lower() not in [
                        "and",
                        "or",
                        "not",
                        "title:",
                        "content:",
                    ]:
                        keywords.append(keyword)

                if keywords:
                    combined_keyword = " ".join(keywords)
                    await search_flow.full_search(combined_keyword, 50)

            result = await search_flow.boolean_search(query_string, max_results)

        elif name == "search_phrase":
            phrase = arguments.get("phrase", "")
            max_results = arguments.get("max_results", MAX_RESULTS)
            mode = arguments.get("mode", "full")

            if mode == "full":
                await search_flow.full_search(phrase, 50)

            result = await search_flow.phrase_search(phrase, max_results)

        elif name == "search_fuzzy":
            term = arguments.get("term", "")
            max_distance = arguments.get("max_distance", 2)
            max_results = arguments.get("max_results", MAX_RESULTS)
            mode = arguments.get("mode", "full")

            if mode == "full":
                await search_flow.full_search(term, 50)

            result = await search_flow.fuzzy_search(term, max_distance, max_results)

        elif name == "search_tag":
            tag = arguments.get("tag", "")
            keyword = arguments.get("keyword", "")
            max_results = arguments.get("max_results", MAX_RESULTS)
            mode = arguments.get("mode", "full")

            if mode == "full" and keyword:
                await search_flow.full_search(keyword, 50)

            result = await search_flow.tag_search(tag, keyword, max_results)

        elif name == "search_documents_local":
            keyword = arguments.get("keyword", "")
            max_results = arguments.get("max_results", MAX_RESULTS)
            result = await search_flow.search(keyword, max_results)

        elif name == "get_system_stats":
            result = search_flow.get_stats()

        elif name == "discover_documents":
            keyword = arguments.get("keyword", "")
            limit = arguments.get("limit", 100)
            doc_type = arguments.get("doc_type")
            language = arguments.get("language")
            category = arguments.get("category")

            # 构建过滤条件
            filters = {}
            if doc_type:
                filters["document_type"] = [doc_type]
            if language:
                filters["language"] = [language]
            if category:
                filters["category"] = [category]

            api_response = search_flow.api_service.search(keyword, limit, filters)
            urls = search_flow.api_service.extract_unique_urls(api_response)
            categories = search_flow.api_service.get_document_categories(api_response)

            # 格式化文档摘要信息
            document_summaries = []
            for hit in api_response.hits[:20]:
                content = hit.content or ""
                summary = content[:200] + "..." if len(content) > 200 else content

                document_summaries.append(
                    {
                        "title": hit.title or "未知标题",
                        "url": hit.url,
                        "summary": summary,
                        "document_type": getattr(hit, "document_type", "unknown"),
                        "language": getattr(hit, "language", "unknown"),
                        "relevance_score": getattr(hit, "relevance_score", 0),
                    }
                )

            result = {
                "query": keyword,
                "total_hits": len(api_response.hits),
                "document_summaries": document_summaries,
                "unique_urls": urls,
                "processing_time_ms": api_response.processing_time_ms,
                "document_categories": categories,
                "search_filters": filters,
                "estimated_total_hits": api_response.estimated_total_hits,
                "usage_note": "此工具仅用于发现相关文档。如需获取具体内容和详细搜索，请使用 search_documents 等搜索工具",
            }
        else:
            raise ValueError(f"Unknown tool: {name}")

        # 将结果转换为JSON字符串并返回
        import json

        result_str = json.dumps(result, ensure_ascii=False, indent=2)

        return [TextContent(type="text", text=result_str)]

    except Exception as e:
        logger.error(f"工具调用失败: {name}, 错误: {e}", exc_info=True)
        error_result = {"error": str(e), "tool": name, "arguments": arguments}
        import json

        return [
            TextContent(
                type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2)
            )
        ]


async def main():
    """主函数"""
    logger.info("启动 myquant-doc-mcp-service (stdio模式)")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
