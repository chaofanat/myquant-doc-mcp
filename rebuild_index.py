#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重建Whoosh索引脚本
用于从已下载的文档重建搜索索引
"""

import json
from pathlib import Path

from config import DOCS_DIR
from services import WhooshSearchEngine
from utils import logger


def rebuild_index():
    """重建索引"""
    logger.info("开始重建索引...")

    # 获取所有已下载的文档
    url_map_file = DOCS_DIR / "url_map.json"

    if not url_map_file.exists():
        logger.error("找不到url_map.json文件，无法重建索引")
        return

    with open(url_map_file, "r", encoding="utf-8") as f:
        url_map = json.load(f)

    logger.info(f"找到 {len(url_map)} 个文档记录")

    # 准备文件-URL对
    file_url_pairs = []
    missing_files = []

    for filename, info in url_map.items():
        url = info.get("url", "")
        file_path = DOCS_DIR / filename
        if file_path.exists():
            file_url_pairs.append({"file_path": str(file_path), "url": url})
        else:
            missing_files.append(filename)

    logger.info(f"有效文档: {len(file_url_pairs)}")
    if missing_files:
        logger.warning(f"缺失文件: {len(missing_files)}")

    # 重建索引
    search_engine = WhooshSearchEngine()
    results = search_engine.rebuild_index(file_url_pairs)

    logger.info("索引重建完成！")
    logger.info(f"总文档数: {results['total_count']}")
    logger.info(f"成功索引: {results['success_count']}")
    logger.info(f"失败: {results['failure_count']}")
    logger.info(f"跳过: {results['skipped_count']}")

    # 显示索引统计
    stats = search_engine.get_index_stats()
    logger.info(f"\n索引统计:")
    logger.info(f"  文档总数: {stats['total_docs']}")
    logger.info(f"  索引目录: {stats['index_dir']}")
    logger.info(f"  评分算法: {stats['scorer']}")


if __name__ == "__main__":
    rebuild_index()
