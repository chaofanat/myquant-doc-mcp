import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root():
    """返回项目根目录"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def data_dir(project_root):
    """返回数据目录"""
    return project_root / "data"

@pytest.fixture(scope="session")
def docs_dir(data_dir):
    """返回文档目录"""
    return data_dir / "docs"

@pytest.fixture(scope="session")
def index_dir(data_dir):
    """返回索引目录"""
    return data_dir / "index"

@pytest.fixture(scope="function")
def mock_requests():
    """创建requests模块的mock"""
    with patch('requests.post') as mock_post:
        yield mock_post

@pytest.fixture(scope="function")
def mock_aiohttp():
    """创建aiohttp模块的mock"""
    with patch('aiohttp.ClientSession') as mock_session:
        yield mock_session

@pytest.fixture(scope="function")
def sample_html():
    """返回示例HTML内容"""
    return """
    <html>
    <head>
        <title>测试文档</title>
    </head>
    <body>
        <h1>测试标题</h1>
        <p>这是一个测试文档，包含一些测试内容。</p>
        <h2>测试小节</h2>
        <p>这是测试小节的内容。</p>
        <code>print("Hello World")</code>
    </body>
    </html>
    """

@pytest.fixture(scope="function")
def sample_api_response():
    """返回示例API响应"""
    return {
        "hits": [
            {
                "id": "1",
                "title": "测试文档",
                "content": "这是一个测试文档，包含一些测试内容。",
                "url": "https://www.example.com/test",
                "object_id": "test1",
                "anchor": "",
                "hierarchy_radio_lvl0": "API文档",
                "hierarchy_radio_lvl1": "Python SDK",
                "hierarchy_radio_lvl2": "数据查询函数",
                "hierarchy_radio_lvl3": "",
                "hierarchy_radio_lvl4": "",
                "hierarchy_radio_lvl5": "",
                "hierarchy_lvl0": "API文档",
                "hierarchy_lvl1": "Python SDK",
                "hierarchy_lvl2": "数据查询函数",
                "hierarchy_lvl3": "",
                "hierarchy_lvl4": "",
                "hierarchy_lvl5": "",
                "hierarchy_lvl6": "",
                "_formatted": {
                    "hierarchy_radio_lvl0": "API文档",
                    "hierarchy_radio_lvl1": "Python SDK",
                    "hierarchy_radio_lvl2": "数据查询函数",
                    "hierarchy_radio_lvl3": "",
                    "hierarchy_radio_lvl4": "",
                    "hierarchy_radio_lvl5": ""
                }
            }
        ],
        "query": "测试",
        "processing_time_ms": 100,
        "limit": 1,
        "offset": 0,
        "estimated_total_hits": 1
    }