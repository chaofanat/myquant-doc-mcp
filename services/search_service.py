import requests
from config import MYQUANT_SEARCH_API, REQUEST_HEADERS
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
        self.api_url = MYQUANT_SEARCH_API
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
            
            # 打印原始响应数据用于调试
            response_data = response.json()
            print("Raw response keys:", list(response_data.keys()))
            
            # 检查hits字段
            if 'hits' in response_data:
                print("Hits count:", len(response_data['hits']))
                if response_data['hits']:
                    print("First hit keys:", list(response_data['hits'][0].keys()))
                    print("First hit sample:", response_data['hits'][0])
            
            # 尝试直接返回响应数据，不使用模型验证
            return response_data
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
    
    def extract_urls(self, search_response) -> List[str]:
        """
        从搜索结果中提取URL列表
        
        Args:
            search_response: 搜索响应数据
            
        Returns:
            URL列表
        """
        urls = []
        
        # 检查响应是否包含hits字段
        if isinstance(search_response, dict) and 'hits' in search_response:
            for hit in search_response['hits']:
                # 尝试从不同字段获取URL
                if 'url' in hit and hit['url']:
                    urls.append(hit['url'])
                elif 'uri' in hit and hit['uri']:
                    urls.append(hit['uri'])
                elif 'link' in hit and hit['link']:
                    urls.append(hit['link'])
        
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