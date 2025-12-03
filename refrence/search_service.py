import requests
from config import SEARCH_API_URL, REQUEST_HEADERS
from models.response import SearchResponse
from typing import List


class SearchService:
    """
    搜索API服务类，用于调用掘金量化的搜索API
    """
    
    def __init__(self):
        """
        初始化搜索服务
        """
        self.api_url = SEARCH_API_URL
        self.headers = REQUEST_HEADERS
    
    def search(self, keyword: str, limit: int = 500) -> SearchResponse:
        """
        调用搜索API获取结果
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            搜索响应模型
        """
        # 构建请求参数
        payload = {
            "q": keyword,
            "limit": limit,
            "attributesToHighlight": ["*"],
            "attributesToCrop": ["content"],
            "cropLength": 50
        }
        
        try:
            # 发送POST请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            # 检查请求是否成功
            response.raise_for_status()
            
            # 解析响应数据
            search_response = SearchResponse.model_validate(response.json())
            
            return search_response
        except requests.exceptions.RequestException as e:
            print(f"Search API request failed: {e}")
            # 返回空结果
            return SearchResponse(
                hits=[],
                query=keyword,
                processingTimeMs=0,
                limit=limit,
                offset=0,
                estimatedTotalHits=0
            )
        except Exception as e:
            print(f"Error processing search response: {e}")
            # 返回空结果
            return SearchResponse(
                hits=[],
                query=keyword,
                processingTimeMs=0,
                limit=limit,
                offset=0,
                estimatedTotalHits=0
            )
    
    def extract_urls(self, search_response: SearchResponse) -> List[str]:
        """
        从搜索结果中提取URL列表
        
        Args:
            search_response: 搜索响应模型
            
        Returns:
            URL列表
        """
        urls = []
        
        for hit in search_response.hits:
            if hit.url:
                urls.append(hit.url)
        
        # 去重
        return list(set(urls))
    
    def search_and_extract_urls(self, keyword: str, limit: int = 500) -> List[str]:
        """
        搜索并提取URL列表
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            URL列表
        """
        search_response = self.search(keyword, limit)
        return self.extract_urls(search_response)
