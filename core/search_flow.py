import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from services import (
    AdvancedMyQuantAPIService,
    SmartDownloader,
    WhooshSearchEngine
)
from config import MAX_RESULTS, CACHE_TTL
from utils import logger, log_search_operation, log_search_result

class SearchFlow:
    """完整搜索流程控制器"""
    
    def __init__(self):
        # 初始化各服务
        self.api_service = AdvancedMyQuantAPIService()
        self.downloader = SmartDownloader()
        self.search_engine = WhooshSearchEngine()
        self.cache = {}
    
    async def _download_and_index(self, urls: List[str]) -> Dict[str, Any]:
        """下载文档并建立索引（智能跳过已存在的文档）"""
        # 下载文档
        download_results = await self.downloader.download_urls(urls)

        # 准备索引的文件-URL对（只包含真正成功下载的，排除跳过的）
        file_url_pairs = []
        for url, result in download_results.items():
            if result is True:  # 只有真正成功下载的文件才需要索引
                file_path = self.downloader.get_file_path(url)
                file_url_pairs.append({
                    'file_path': str(file_path),
                    'url': url
                })

        # 建立索引（智能跳过已存在的文档）
        if file_url_pairs:
            index_results = self.search_engine.add_documents(file_url_pairs)
        else:
            index_results = {
                'total_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'skipped_count': len(urls)
            }

        # 计算实际统计
        newly_downloaded = sum(1 for result in download_results.values() if result is True)
        newly_indexed = index_results.get('success_count', 0)
        skipped_docs = len([result for result in download_results.values() if result is None])
        skipped_indexing = index_results.get('skipped_count', 0)

        return {
            'download_results': download_results,
            'index_results': index_results,
            'newly_downloaded': newly_downloaded,
            'newly_indexed': newly_indexed,
            'skipped_existing_downloads': skipped_docs,
            'skipped_existing_indexing': skipped_indexing,
            'total_skipped': skipped_docs + skipped_indexing
        }
    
    async def search(self, keyword: str, max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """完整搜索流程"""
        log_context = log_search_operation(logger, keyword, max_results=max_results)
        
        try:
            # 直接使用现有索引进行搜索
            search_result = self.search_engine.search(keyword, max_results=max_results)
            
            # 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            return search_result
            
        except Exception as e:
            logger.error(f"搜索流程失败: {keyword}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": keyword,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    async def full_search(self, keyword: str, max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """完整搜索流程（包含API调用和下载）"""
        log_context = log_search_operation(logger, keyword, max_results=max_results)
        
        try:
            # 1. 调用掘金量化API获取相关文档URL
            api_response = self.api_service.search(keyword, limit=50)
            urls = self.api_service.extract_unique_urls(api_response)
            
            if not urls:
                log_search_result(logger, log_context, 0)
                return {
                    "query": keyword,
                    "total_hits": 0,
                    "results": [],
                    "message": "未找到相关文档"
                }
            
            # 2. 下载URL到本地并建立索引
            download_index_result = await self._download_and_index(urls)
            
            # 3. 本地Whoosh检索
            search_result = self.search_engine.search(keyword, max_results=max_results)
            
            # 4. 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            # 5. 添加流程统计信息
            search_result['api_hits'] = len(api_response.hits)
            search_result['newly_downloaded'] = download_index_result['newly_downloaded']
            search_result['newly_indexed'] = download_index_result['newly_indexed']
            search_result['skipped_existing_downloads'] = download_index_result['skipped_existing_downloads']
            search_result['skipped_existing_indexing'] = download_index_result['skipped_existing_indexing']
            search_result['total_skipped'] = download_index_result['total_skipped']
            search_result['processing_efficiency'] = {
                'total_urls': len(urls),
                'download_skip_ratio': download_index_result['skipped_existing_downloads'] / len(urls) if urls else 0,
                'index_skip_ratio': download_index_result['skipped_existing_indexing'] / len(urls) if urls else 0,
                'total_efficiency': download_index_result['total_skipped'] / len(urls) if urls else 0,
                'time_saved': download_index_result['total_skipped'] > 0
            }
            
            return search_result
            
        except Exception as e:
            logger.error(f"搜索流程失败: {keyword}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": keyword,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    async def boolean_search(self, query_string: str, max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """布尔查询搜索流程"""
        log_context = log_search_operation(logger, query_string, max_results=max_results, search_type="boolean")
        
        try:
            # 直接使用现有索引进行布尔搜索
            search_result = self.search_engine.boolean_search(query_string, max_results=max_results)
            
            # 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            return search_result
            
        except Exception as e:
            logger.error(f"布尔搜索流程失败: {query_string}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": query_string,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    async def phrase_search(self, phrase: str, max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """短语搜索流程"""
        log_context = log_search_operation(logger, phrase, max_results=max_results, search_type="phrase")
        
        try:
            # 直接使用现有索引进行短语搜索
            search_result = self.search_engine.phrase_search(phrase, max_results=max_results)
            
            # 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            return search_result
            
        except Exception as e:
            logger.error(f"短语搜索流程失败: {phrase}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": phrase,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    async def fuzzy_search(self, term: str, max_distance: int = 2, max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """模糊搜索流程"""
        log_context = log_search_operation(logger, term, max_results=max_results, search_type="fuzzy")
        
        try:
            # 直接使用现有索引进行模糊搜索
            search_result = self.search_engine.fuzzy_search(term, max_distance, max_results=max_results)
            
            # 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            return search_result
            
        except Exception as e:
            logger.error(f"模糊搜索流程失败: {term}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": term,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    async def tag_search(self, tag: str, keyword: str = "", max_results: int = MAX_RESULTS) -> Dict[str, Any]:
        """标签搜索流程"""
        log_context = log_search_operation(logger, keyword or tag, max_results=max_results, search_type="tag", tag=tag)
        
        try:
            # 直接使用现有索引进行标签搜索
            search_result = self.search_engine.tag_search(tag, keyword, max_results=max_results)
            
            # 记录搜索结果
            log_search_result(logger, log_context, search_result['total_hits'])
            
            return search_result
            
        except Exception as e:
            logger.error(f"标签搜索流程失败: {tag} {keyword}, 错误: {e}")
            log_search_result(logger, log_context, 0)
            return {
                "query": f"{tag} {keyword}",
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
        
    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        # 获取各服务的统计信息
        download_stats = self.downloader.get_file_stats()
        index_stats = self.search_engine.get_index_stats()
        
        return {
            "downloader": download_stats,
            "search_engine": index_stats,
            "cache_size": len(self.cache)
        }