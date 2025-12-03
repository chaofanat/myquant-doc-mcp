import pytest
import logging
from utils.logger import (
    setup_logger,
    LogPerformance,
    log_search_operation,
    log_search_result,
    log_api_call,
    log_api_result
)

class TestLogger:
    """测试日志工具类"""
    
    def test_setup_logger(self):
        """测试logger设置"""
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_log_performance(self, capsys):
        """测试性能日志上下文管理器"""
        logger = setup_logger("test_performance")
        
        with LogPerformance(logger, "test_operation"):
            pass
        
        captured = capsys.readouterr()
        assert "开始操作: test_operation" in captured.out
        assert "操作完成: test_operation" in captured.out
    
    def test_log_search_operation(self):
        """测试搜索操作日志记录"""
        logger = setup_logger("test_search")
        context = log_search_operation(logger, "test_keyword", max_results=5)
        
        assert "keyword" in context
        assert context["keyword"] == "test_keyword"
        assert "max_results" in context
        assert context["max_results"] == 5
    
    def test_log_search_result(self, capsys):
        """测试搜索结果日志记录"""
        logger = setup_logger("test_search_result")
        context = {"keyword": "test", "start_time": 0}
        
        log_search_result(logger, context, 10)
        
        captured = capsys.readouterr()
        assert "test" in captured.out
        assert "找到 10 个结果" in captured.out
    
    def test_log_api_call(self):
        """测试API调用日志记录"""
        logger = setup_logger("test_api")
        context = log_api_call(logger, "test_api", param1="value1")
        
        assert "api_name" in context
        assert context["api_name"] == "test_api"
    
    def test_log_api_result(self, capsys):
        """测试API结果日志记录"""
        logger = setup_logger("test_api_result")
        context = {"api_name": "test_api", "start_time": 0}
        result = {"hits": [1, 2, 3]}
        
        log_api_result(logger, context, result)
        
        captured = capsys.readouterr()
        assert "test_api" in captured.out
        assert "返回 3 个结果" in captured.out