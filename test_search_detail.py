#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细的搜索结果展示测试
用于评估和展示搜索结果的质量
"""

import asyncio

from core import SearchFlow


def print_result_detail(result: dict, index: int):
    """详细打印单个搜索结果"""
    print(f"\n{'─' * 80}")
    print(f"结果 #{index}")
    print(f"{'─' * 80}")
    print(f"标题: {result.get('title', '无标题')}")
    print(f"URL: {result.get('url', 'N/A')}")
    print(f"评分: {result.get('score', 0):.4f}")
    print(f"\n高亮标题:")
    print(f"  {result.get('highlights', {}).get('title', 'N/A')}")
    print(f"\n高亮内容:")
    highlight_content = result.get("highlights", {}).get("content", "N/A")
    # 分行显示高亮内容
    lines = highlight_content.split("\n")
    for line in lines[:5]:  # 只显示前5行
        if line.strip():
            print(f"  {line.strip()}")
    print(f"\n原始内容预览:")
    content = result.get("content", "")[:200]
    print(f"  {content}...")


async def test_search_with_detail(query: str, max_results: int = 5):
    """测试搜索并详细展示结果"""
    print(f"\n{'=' * 80}")
    print(f"搜索查询: {query}")
    print(f"{'=' * 80}")

    search_flow = SearchFlow()
    result = await search_flow.search(query, max_results=max_results)

    print(f"\n查询: {result.get('query', 'N/A')}")
    print(f"总命中数: {result.get('total_hits', 0)}")
    print(f"返回结果数: {len(result.get('results', []))}")

    for i, res in enumerate(result.get("results", []), 1):
        print_result_detail(res, i)


async def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("详细搜索结果测试")
    print("=" * 80)

    # 测试多个查询
    test_queries = [
        ("交易接口", 3),
        ("行情数据", 3),
        ("Python SDK", 3),
        ("策略回测", 3),
        ("实时行情", 3),
        ("K线", 3),
    ]

    for query, max_results in test_queries:
        await test_search_with_detail(query, max_results)
        print("\n" + "=" * 80)
        print("按Enter键继续下一个查询...")
        print("=" * 80)
        input()


if __name__ == "__main__":
    asyncio.run(main())
