import asyncio
from pathlib import Path
from services.search_service import SearchService
from services.downloader import SmartDownloader
from services.whoosh_service import WhooshSearchEngine
from utils import logger
from config import DOCS_DIR, INDEX_DIR

async def initialize_docs(test_mode=False, test_limit=5):
    """初始化文档下载和索引
    
    Args:
        test_mode: 是否为测试模式，测试模式下只下载少量文档
        test_limit: 测试模式下下载的文档数量限制
    """
    # 确保目录存在
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    # 初始化服务
    search_service = SearchService()
    downloader = SmartDownloader()
    search_engine = WhooshSearchEngine()
    
    # 根据模式设置搜索限制
    search_limit = test_limit if test_mode else 100
    
    # 搜索热门文档
    logger.info(f"正在搜索热门文档... (模式: {'测试' if test_mode else '完整'}, 限制: {search_limit})")
    search_response = search_service.search("", limit=search_limit)
    
    # 提取URL
    logger.info("提取文档URL...")
    urls = search_service.extract_urls(search_response)
    
    if not urls:
        logger.warning("未找到任何文档")
        return
    
    logger.info(f"找到 {len(urls)} 个唯一URL")
    
    # 过滤已下载的URL
    new_urls, existing_urls = downloader.filter_new_urls(urls)
    logger.info(f"新URL: {len(new_urls)}, 已存在URL: {len(existing_urls)}")
    
    # 下载新文档
    if new_urls:
        logger.info(f"开始下载 {len(new_urls)} 个新文档...")
        results = await downloader.download_urls(new_urls)
        
        success_count = sum(1 for r in results.values() if r is True)
        logger.info(f"成功下载 {success_count}/{len(new_urls)} 个文档")
    
    # 只索引新下载的文档
    logger.info("开始索引新下载的文档...")
    
    # 构建文件路径和URL的映射
    file_url_pairs = []
    for url in new_urls:
        file_path = downloader.get_file_path(url)
        if file_path.exists():
            file_url_pairs.append({"file_path": file_path, "url": url})
    
    # 批量添加到索引
    if file_url_pairs:
        result = search_engine.add_documents(file_url_pairs)
        logger.info(f"索引完成: {result}")
    else:
        logger.info("没有新文档需要索引")
    
    logger.info("初始化完成")

if __name__ == "__main__":
    import argparse
    
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="初始化文档下载和索引")
    parser.add_argument("--test", action="store_true", help="启用测试模式，只下载少量文档")
    parser.add_argument("--limit", type=int, default=5, help="测试模式下下载的文档数量限制 (默认: 5)")
    
    args = parser.parse_args()
    
    # 运行初始化
    asyncio.run(initialize_docs(test_mode=args.test, test_limit=args.limit))