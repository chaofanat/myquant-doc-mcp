import logging
import time
import sys
from typing import Dict, Any
from config import LOG_LEVEL

# 配置日志格式
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logger(name: str = "myquant-doc-mcp") -> logging.Logger:
    """
    设置并返回一个配置好的logger
    
    Args:
        name: logger名称
        
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复设置处理器
    if not logger.handlers:
        # 设置日志级别
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # 创建格式化器
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
    
    return logger

# 创建默认logger
logger = setup_logger()

class LogPerformance:
    """
    性能监控上下文管理器
    
    使用示例：
    with LogPerformance(logger, "耗时操作"):
        # 执行耗时操作
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"开始操作: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.info(f"操作完成: {self.operation_name}, 耗时 {duration:.2f}秒")
        else:
            self.logger.error(f"操作失败: {self.operation_name}, 耗时 {duration:.2f}秒, 错误: {exc_val}")

    def get_duration(self) -> float:
        """获取当前已执行时间"""
        return time.time() - self.start_time

def log_search_operation(logger: logging.Logger, keyword: str, **kwargs: Any) -> Dict[str, Any]:
    """
    记录搜索操作日志
    
    Args:
        logger: logger实例
        keyword: 搜索关键词
        **kwargs: 其他搜索参数
        
    Returns:
        包含开始时间的上下文信息
    """
    start_time = time.time()
    params = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"开始搜索: {keyword} {params}")
    
    return {
        "start_time": start_time,
        "keyword": keyword,
        **kwargs
    }

def log_search_result(logger: logging.Logger, context: Dict[str, Any], result_count: int) -> None:
    """
    记录搜索结果日志
    
    Args:
        logger: logger实例
        context: 搜索上下文信息
        result_count: 搜索结果数量
    """
    duration = time.time() - context["start_time"]
    keyword = context["keyword"]
    logger.info(f"搜索完成: {keyword}, 找到 {result_count} 个结果, 耗时 {duration:.2f}秒")

def log_api_call(logger: logging.Logger, api_name: str, **kwargs: Any) -> Dict[str, Any]:
    """
    记录API调用日志
    
    Args:
        logger: logger实例
        api_name: API名称
        **kwargs: API调用参数
        
    Returns:
        包含开始时间的上下文信息
    """
    start_time = time.time()
    params = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"开始API调用: {api_name} {params}")
    
    return {
        "start_time": start_time,
        "api_name": api_name,
        **kwargs
    }

def log_api_result(logger: logging.Logger, context: Dict[str, Any], result: Any) -> None:
    """
    记录API调用结果日志
    
    Args:
        logger: logger实例
        context: API调用上下文信息
        result: API调用结果
    """
    duration = time.time() - context["start_time"]
    api_name = context["api_name"]
    
    if isinstance(result, dict):
        result_info = f"返回 {len(result.get('hits', []))} 个结果"
    elif isinstance(result, list):
        result_info = f"返回 {len(result)} 个结果"
    else:
        result_info = "返回结果"
    
    logger.info(f"API调用完成: {api_name}, {result_info}, 耗时 {duration:.2f}秒")