from typing import List, Optional
from pydantic import BaseModel


class DocumentHit(BaseModel):
    """文档搜索结果项"""
    id: str
    title: str
    content: str
    url: str
    object_id: str
    anchor: Optional[str] = None
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
    _formatted: Optional[dict] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    hits: List[DocumentHit]
    query: str
    processingTimeMs: int
    limit: int
    offset: int
    estimatedTotalHits: int