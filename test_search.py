#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
搜索功能测试脚本
用于测试和调试Whoosh搜索引擎的检索效果
"""

import asyncio
import json
from pathlib import Path

from core import SearchFlow
from services import WhooshSearchEngine
from utils import logger


def print_results(results: dict, title: str = "搜索结果"):
    """打印搜索结果"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}")
    print(f"查询: {results.get('query', 'N/A')}")
    print(f"总命中数: {results.get('total_hits', 0)}")
    print(f"{'=' * 80}\n")

    for i, result in enumerate(results.get("results", []), 1):
        print(f"[{i}] {result.get('title', '无标题')}")
        print(f"    URL: {result.get('url', 'N/A')}")
        print(f"    评分: {result.get('score', 0):.4f}")
        print(f"    高亮标题: {result.get('highlights', {}).get('title', 'N/A')[:100]}")
        print(
            f"    高亮内容: {result.get('highlights', {}).get('content', 'N/A')[:200]}"
        )
        print()


async def test_basic_search():
    """测试基础搜索功能"""
    print("\n" + "=" * 80)
    print("测试 1: 基础关键词搜索")
    print("=" * 80)

    search_flow = SearchFlow()

    # 测试用例
    test_queries = [
        "交易接口",
        "行情数据",
        "策略回测",
        "Python API",
        "实时行情",
        "历史数据",
        "K线数据",
        "订阅行情",
    ]

    for query in test_queries:
        print(f"\n>>> 搜索: {query}")
        result = await search_flow.search(query, max_results=5)
        print(f"命中数: {result['total_hits']}")
        if result["total_hits"] > 0:
            print(f"最佳结果: {result['results'][0]['title']}")
            print(f"评分: {result['results'][0]['score']:.4f}")


async def test_full_search():
    """测试完整搜索流程（包含API调用和下载）"""
    print("\n" + "=" * 80)
    print("测试 2: 完整搜索流程")
    print("=" * 80)

    search_flow = SearchFlow()

    query = "交易接口"
    print(f"\n>>> 完整搜索: {query}")
    result = await search_flow.full_search(query, max_results=5)

    print_results(result, f"完整搜索: {query}")
    print(f"API命中数: {result.get('api_hits', 'N/A')}")
    print(f"新下载: {result.get('newly_downloaded', 'N/A')}")
    print(f"新索引: {result.get('newly_indexed', 'N/A')}")
    print(f"跳过数: {result.get('total_skipped', 'N/A')}")


async def test_boolean_search():
    """测试布尔查询"""
    print("\n" + "=" * 80)
    print("测试 3: 布尔查询")
    print("=" * 80)

    search_flow = SearchFlow()

    # 测试用例
    test_queries = [
        'title:"API" AND content:"Python"',
        "交易 AND 行情",
        "股票 OR 期货",
        "交易 NOT 期货",
        "(行情 OR 数据) AND Python",
    ]

    for query in test_queries:
        print(f"\n>>> 布尔查询: {query}")
        result = await search_flow.boolean_search(query, max_results=3)
        print(f"命中数: {result['total_hits']}")
        if result["total_hits"] > 0:
            print(f"最佳结果: {result['results'][0]['title']}")


async def test_phrase_search():
    """测试精确短语搜索"""
    print("\n" + "=" * 80)
    print("测试 4: 精确短语搜索")
    print("=" * 80)

    search_flow = SearchFlow()

    # 测试用例
    test_phrases = [
        "实时行情接口",
        "历史K线数据",
        "Python SDK",
        "策略回测",
    ]

    for phrase in test_phrases:
        print(f"\n>>> 短语搜索: {phrase}")
        result = await search_flow.phrase_search(phrase, max_results=3)
        print(f"命中数: {result['total_hits']}")
        if result["total_hits"] > 0:
            print(f"最佳结果: {result['results'][0]['title']}")


async def test_fuzzy_search():
    """测试模糊搜索"""
    print("\n" + "=" * 80)
    print("测试 5: 模糊搜索")
    print("=" * 80)

    search_flow = SearchFlow()

    # 测试用例（包含拼写错误）
    test_terms = [
        ("jiaoyi", "交易"),  # 拼音
        ("hangqing", "行情"),  # 拼音
        ("APi", "API"),  # 大小写错误
        ("pythn", "python"),  # 拼写错误
    ]

    for term, correct in test_terms:
        print(f"\n>>> 模糊搜索: {term} (正确: {correct})")
        result = await search_flow.fuzzy_search(term, max_distance=2, max_results=3)
        print(f"命中数: {result['total_hits']}")
        if result["total_hits"] > 0:
            print(f"最佳结果: {result['results'][0]['title']}")


async def test_tag_search():
    """测试标签搜索"""
    print("\n" + "=" * 80)
    print("测试 6: 标签搜索")
    print("=" * 80)

    search_flow = SearchFlow()

    # 测试用例
    test_tags = [
        ("API", ""),
        ("Python", ""),
        ("SDK", "交易"),
    ]

    for tag, keyword in test_tags:
        print(f"\n>>> 标签搜索: tag={tag}, keyword={keyword}")
        result = await search_flow.tag_search(tag, keyword, max_results=3)
        print(f"命中数: {result['total_hits']}")
        if result["total_hits"] > 0:
            print(f"最佳结果: {result['results'][0]['title']}")


def test_index_stats():
    """测试索引统计"""
    print("\n" + "=" * 80)
    print("测试 7: 索引统计")
    print("=" * 80)

    search_engine = WhooshSearchEngine()
    stats = search_engine.get_index_stats()

    print(f"\n索引统计:")
    print(f"文档总数: {stats.get('total_docs', 0)}")
    print(f"索引目录: {stats.get('index_dir', 'N/A')}")
    print(f"评分算法: {stats.get('scorer', 'N/A')}")
    print(f"\n字段信息:")
    for field_name, field_info in stats.get("schema_fields", {}).items():
        print(f"  {field_name}:")
        print(f"    类型: {field_info.get('type', 'N/A')}")
        print(f"    存储: {field_info.get('stored', False)}")


async def test_system_stats():
    """测试系统统计"""
    print("\n" + "=" * 80)
    print("测试 8: 系统统计")
    print("=" * 80)

    search_flow = SearchFlow()
    stats = search_flow.get_stats()

    print(f"\n系统统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


async def test_search_quality():
    """测试搜索质量和相关性"""
    print("\n" + "=" * 80)
    print("测试 9: 搜索质量评估")
    print("=" * 80)

    search_flow = SearchFlow()

    # 定义期望的搜索结果（关键词 -> 期望包含的关键词）
    quality_tests = [
        {
            "query": "交易接口",
            "expected_keywords": ["交易", "接口", "API", "下单", "委托"],
            "min_results": 3,
        },
        {
            "query": "行情数据",
            "expected_keywords": ["行情", "数据", "K线", "实时", "历史"],
            "min_results": 3,
        },
        {
            "query": "Python SDK",
            "expected_keywords": ["Python", "SDK", "API", "接口"],
            "min_results": 2,
        },
        {
            "query": "策略回测",
            "expected_keywords": ["策略", "回测", "测试", "模拟"],
            "min_results": 2,
        },
    ]

    passed = 0
    failed = 0

    for test in quality_tests:
        query = test["query"]
        expected_keywords = test["expected_keywords"]
        min_results = test["min_results"]

        print(f"\n>>> 质量测试: {query}")
        result = await search_flow.search(query, max_results=10)

        # 检查结果数量
        if result["total_hits"] < min_results:
            print(
                f"    ❌ 失败: 结果数量不足 (期望>={min_results}, 实际={result['total_hits']})"
            )
            failed += 1
            continue

        # 检查关键词相关性
        found_keywords = set()
        for doc in result["results"][:5]:
            title_lower = doc["title"].lower()
            content_lower = doc["content"].lower()

            for keyword in expected_keywords:
                if keyword.lower() in title_lower or keyword.lower() in content_lower:
                    found_keywords.add(keyword)

        relevance_score = len(found_keywords) / len(expected_keywords)

        if relevance_score >= 0.4:  # 至少40%的期望关键词被找到
            print(
                f"    ✓ 通过: 相关性评分 {relevance_score:.2%} ({len(found_keywords)}/{len(expected_keywords)})"
            )
            print(f"    找到的关键词: {', '.join(found_keywords)}")
            passed += 1
        else:
            print(
                f"    ❌ 失败: 相关性评分过低 {relevance_score:.2%} ({len(found_keywords)}/{len(expected_keywords)})"
            )
            print(f"    找到的关键词: {', '.join(found_keywords)}")
            print(
                f"    缺失的关键词: {', '.join(set(expected_keywords) - found_keywords)}"
            )
            failed += 1

    print(f"\n{'=' * 80}")
    print(
        f"质量测试总结: 通过 {passed}/{passed + failed} ({passed / (passed + failed) * 100:.1f}%)"
    )
    print(f"{'=' * 80}")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("开始运行所有测试")
    print("=" * 80)

    # 测试索引统计（同步）
    test_index_stats()

    # 测试系统统计
    await test_system_stats()

    # 测试基础搜索
    await test_basic_search()

    # 测试搜索质量
    await test_search_quality()

    # 如果需要，可以启用其他测试
    # await test_full_search()  # 这个会调用API和下载，比较慢
    # await test_boolean_search()
    # await test_phrase_search()
    # await test_fuzzy_search()
    # await test_tag_search()

    print("\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_all_tests())
