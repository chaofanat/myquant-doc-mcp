from typing import List, Optional, Dict, Any
import requests
from pydantic import BaseModel, Field
from enum import Enum
from config import MYQUANT_SEARCH_API, REQUEST_HEADERS
from utils import logger, log_api_call, log_api_result

class DocumentType(str, Enum):
    API = "api"
    TUTORIAL = "tutorial"
    FAQ = "faq"
    QUICK_START = "quick_start"

class Language(str, Enum):
    PYTHON = "python"
    CPP = "cpp"
    CSHARP = "csharp"
    MATLAB = "matlab"

class Category(str, Enum):
    API = "api"
    DATA = "data"
    TRADING = "trading"
    SDK = "sdk"
    TOOLS = "tools"

class MatchingStrategy(str, Enum):
    ALL = "all"
    LAST = "last"

class MeiliSearchRequest(BaseModel):
    """MeiliSearch标准请求模型"""
    q: str = Field(..., description="搜索查询词")
    limit: int = Field(default=500, description="返回结果数量限制")
    offset: int = Field(default=0, description="结果偏移量")
    attributes_to_highlight: List[str] = Field(
        default=["*"],
        description="需要高亮的属性字段列表"
    )
    attributes_to_crop: List[str] = Field(
        default=["content"],
        description="需要裁剪的属性字段列表"
    )
    crop_length: int = Field(default=50, description="裁剪内容长度")
    index: str = Field(default="mq-website-docs", description="搜索索引名称")
    show_matches_position: bool = Field(default=True, description="是否显示匹配位置")
    matching_strategy: MatchingStrategy = Field(default=MatchingStrategy.ALL, description="匹配策略")
    sort: List[str] = Field(
        default=["timestamp:desc", "relevance:desc"],
        description="排序规则"
    )
    filter: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="过滤条件"
    )

class FormattedHierarchy(BaseModel):
    """格式化层级信息"""
    hierarchy_radio_lvl0: Optional[str] = None
    hierarchy_radio_lvl1: Optional[str] = None
    hierarchy_radio_lvl2: Optional[str] = None
    hierarchy_radio_lvl3: Optional[str] = None
    hierarchy_radio_lvl4: Optional[str] = None
    hierarchy_radio_lvl5: Optional[str] = None

class FormattedHierarchy(BaseModel):
    """格式化层级信息"""
    hierarchy_radio_lvl0: Optional[str] = None
    hierarchy_radio_lvl1: Optional[str] = None
    hierarchy_radio_lvl2: Optional[str] = None
    hierarchy_radio_lvl3: Optional[str] = None
    hierarchy_radio_lvl4: Optional[str] = None
    hierarchy_radio_lvl5: Optional[str] = None

class DocumentHit(BaseModel):
    """文档搜索结果项"""
    content: Optional[str] = None
    objectID: str  # 注意：API返回的是 objectID 而不是 object_id
    anchor: Optional[str] = None
    url: str
    hierarchy_radio_lvl0: Optional[str] = None
    hierarchy_radio_lvl1: Optional[str] = None
    hierarchy_radio_lvl2: Optional[str] = None
    hierarchy_radio_lvl3: Optional[str] = None
    hierarchy_radio_lvl4: Optional[str] = None
    hierarchy_radio_lvl5: Optional[str] = None
    hierarchy_lvl0: Optional[str] = None
    hierarchy_lvl1: Optional[str] = None
    hierarchy_lvl2: Optional[str] = None
    hierarchy_lvl3: Optional[str] = None
    hierarchy_lvl4: Optional[str] = None
    hierarchy_lvl5: Optional[str] = None
    hierarchy_lvl6: Optional[str] = None
    _formatted: Optional[FormattedHierarchy] = None

    # 为向后兼容添加属性访问器
    @property
    def id(self) -> str:
        return self.objectID

    @property
    def title(self) -> str:
        # 从内容或格式化信息中提取标题
        if self._formatted and hasattr(self._formatted, 'hierarchy_radio_lvl0'):
            return self._formatted.hierarchy_radio_lvl0 or ""
        content = self.content or ""
        return content[:100] if content else "未知标题"

    @property
    def object_id(self) -> str:
        return self.objectID

class MeiliSearchResponse(BaseModel):
    """MeiliSearch标准响应模型"""
    hits: List[DocumentHit]
    query: str
    processingTimeMs: int  # 注意：API返回的是 processingTimeMs
    limit: int
    offset: int
    estimatedTotalHits: int  # 注意：API返回的是 estimatedTotalHits

    # 为向后兼容添加属性访问器
    @property
    def processing_time_ms(self) -> int:
        return self.processingTimeMs

    @property
    def estimated_total_hits(self) -> int:
        return self.estimatedTotalHits

class EnhancedMyQuantAPIService:
    """增强的掘金量化API服务"""
    
    def __init__(self):
        self.api_url = MYQUANT_SEARCH_API
        self.headers = REQUEST_HEADERS
    
    def build_search_request(self, keyword: str, limit: int = 500,
                          filters: Optional[Dict[str, List[str]]] = None) -> MeiliSearchRequest:
        """构建标准MeiliSearch请求"""
        
        request = MeiliSearchRequest(q=keyword, limit=limit)
        
        if filters:
            request.filter = filters
        
        return request
    
    def search(self, keyword: str, limit: int = 500,
                filters: Optional[Dict[str, List[str]]] = None) -> MeiliSearchResponse:
        """执行MeiliSearch API调用"""
        
        log_context = log_api_call(logger, "search", keyword=keyword, limit=limit, filters=filters)
        request = self.build_search_request(keyword, limit, filters)
        
        try:
            # 使用成功的请求格式（基于reference案例）
            request_data = {
                "q": keyword,
                "limit": limit,
                "attributesToHighlight": ["*"],
                "attributesToCrop": ["content"],
                "cropLength": 50
            }

            # 使用完整的请求头（基于成功案例）
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=request_data,
                timeout=15
            )

            logger.debug(f"API请求URL: {self.api_url}")
            logger.debug(f"API请求数据: {request_data}")
            logger.debug(f"API响应状态: {response.status_code}")
            logger.debug(f"API响应内容: {response.text[:500]}...")

            if response.status_code != 200:
                logger.error(f"API请求失败: {response.status_code} - {response.text[:200]}")
                # 返回空响应而不是抛出异常
                return MeiliSearchResponse(
                    hits=[],
                    query=keyword,
                    processing_time_ms=0,
                    limit=limit,
                    offset=0,
                    estimated_total_hits=0
                )

            # 使用Pydantic验证响应
            search_response = MeiliSearchResponse.model_validate(response.json())

            log_api_result(logger, log_context, search_response)

            return search_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            # 返回空响应
            return MeiliSearchResponse(
                hits=[],
                query=keyword,
                processing_time_ms=0,
                limit=limit,
                offset=0,
                estimated_total_hits=0
            )
        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            return MeiliSearchResponse(
                hits=[],
                query=keyword,
                processing_time_ms=0,
                limit=limit,
                offset=0,
                estimated_total_hits=0
            )
    
    def extract_unique_urls(self, response: MeiliSearchResponse) -> List[str]:
        """提取唯一URL列表"""
        urls = [hit.url for hit in response.hits if hit.url]
        return list(set(urls))  # 去重
    
    def get_document_categories(self, response: MeiliSearchResponse) -> Dict[str, Any]:
        """统计文档分类信息"""
        doc_types = {}
        languages = {}
        categories = {}
        
        for hit in response.hits:
            # 统计文档类型
            if hasattr(hit, '_formatted') and hit._formatted and hasattr(hit._formatted, 'hierarchy_radio_lvl0') and hit._formatted.hierarchy_radio_lvl0:
                doc_type = hit._formatted.hierarchy_radio_lvl0
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # 统计编程语言
            if hasattr(hit, '_formatted') and hit._formatted and hasattr(hit._formatted, 'hierarchy_radio_lvl1') and hit._formatted.hierarchy_radio_lvl1:
                language = hit._formatted.hierarchy_radio_lvl1.lower()
                languages[language] = languages.get(language, 0) + 1
            
            # 统计功能分类
            if hasattr(hit, '_formatted') and hit._formatted and hasattr(hit._formatted, 'hierarchy_radio_lvl2') and hit._formatted.hierarchy_radio_lvl2:
                category = hit._formatted.hierarchy_radio_lvl2.lower()
                categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_documents': len(response.hits),
            'document_types': doc_types,
            'languages': languages,
            'categories': categories
        }

class AdvancedMyQuantAPIService(EnhancedMyQuantAPIService):
    """高级掘金量化API服务，支持多种搜索模式"""
    
    def search_by_type(self, keyword: str, doc_type: str,
                     language: str = None, category: str = None,
                     limit: int = 100) -> MeiliSearchResponse:
        """按文档类型搜索"""
        
        filters = {
            'document_type': [doc_type]
        }
        
        if language:
            filters['language'] = [language]
        
        if category:
            filters['category'] = [category]
        
        return self.search(keyword, limit, filters)
    
    def search_by_language(self, keyword: str, language: Language,
                      limit: int = 100) -> MeiliSearchResponse:
        """按编程语言搜索"""
        
        return self.search_by_type(
            keyword,
            doc_type="",  # 添加默认doc_type参数
            language=language.value,
            limit=limit
        )
    
        
    def search_recent(self, limit: int = 50) -> MeiliSearchResponse:
        """搜索最近更新的文档"""
        
        # 按时间排序的最近文档搜索
        request = MeiliSearchRequest(
            q="",
            limit=limit,
            sort=["timestamp:desc"]
        )
        
        log_context = log_api_call(logger, "search_recent", limit=limit)
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=request.model_dump(exclude_none=True),
                timeout=15
            )
            
            response.raise_for_status()
            result = MeiliSearchResponse.model_validate(response.json())
            
            log_api_result(logger, log_context, result)
            return result
            
        except Exception as e:
            logger.error(f"最近文档搜索失败: {e}")
            return MeiliSearchResponse(
                hits=[],
                query="",
                processing_time_ms=0,
                limit=limit,
                offset=0,
                estimated_total_hits=0
            )