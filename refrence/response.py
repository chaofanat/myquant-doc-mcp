from pydantic import BaseModel
from typing import List, Optional

# 定义格式化后的内容模型
class FormattedHit(BaseModel):
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
    content: Optional[str] = None
    objectID: str
    anchor: Optional[str] = None
    url: str

# 定义单个搜索结果模型
class Hit(BaseModel):
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
    content: Optional[str] = None
    objectID: str
    anchor: Optional[str] = None
    url: str
    _formatted: Optional[FormattedHit] = None

# 定义完整搜索响应模型
class SearchResponse(BaseModel):
    hits: List[Hit]
    query: str
    processingTimeMs: int
    limit: int
    offset: int
    estimatedTotalHits: int

# 定义返回给客户端的检索结果
class LocalSearchResultItem(BaseModel):
    url: str
    content: str
    line_number: int
    context: List[str]
    # 内部使用字段，不序列化给客户端
    file_path: Optional[str] = None

    class Config:
        # 当序列化时忽略 file_path 字段
        exclude = {'file_path'}

# 定义完整的本地搜索响应
class LocalSearchResponse(BaseModel):
    query: str
    context_lines: int
    total_hits: int
    results: List[LocalSearchResultItem]
    loading_info: Optional[dict] = None
