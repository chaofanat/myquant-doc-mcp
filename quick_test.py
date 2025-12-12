#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速搜索测试"""

import asyncio

from core import SearchFlow


async def main():
    search_flow = SearchFlow()

    queries = ["交易接口", "行情数据", "Python SDK", "策略回测"]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"搜索: {query}")
        print("=" * 60)

        result = await search_flow.search(query, max_results=3)

        print(f"总命中数: {result['total_hits']}")
        print(f"\n前3个结果:")

        for i, r in enumerate(result["results"][:3], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   评分: {r['score']:.2f}")
            print(f"   URL: {r['url']}")
            print(f"   高亮: {r['highlights']['content'][:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
