import asyncio
import aiohttp
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any
from config import (
    DOCS_DIR, DOC_DOWNLOAD_HEADERS, MAX_CONCURRENT_DOWNLOADS,
    REQUEST_DELAY
)
from utils import logger

class SmartDownloader:
    """智能文档下载器"""
    
    def __init__(self, docs_dir: Path = DOCS_DIR, request_delay: float = REQUEST_DELAY):
        self.docs_dir = docs_dir
        self.headers = DOC_DOWNLOAD_HEADERS
        self.url_map_file = docs_dir / "url_map.json"
        self.url_map = self._load_url_map()
        self.request_delay = request_delay
    
    def _load_url_map(self) -> Dict[str, Dict[str, Any]]:
        """加载URL映射文件"""
        if self.url_map_file.exists():
            try:
                with open(self.url_map_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"URL映射文件解析失败: {self.url_map_file}")
                return {}
        return {}
    
    def _save_url_map(self) -> None:
        """保存URL映射文件"""
        with open(self.url_map_file, 'w', encoding='utf-8') as f:
            json.dump(self.url_map, f, ensure_ascii=False, indent=2)
    
    def _file_exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        file_path = self.docs_dir / filename
        return file_path.exists()
    
    def url_to_filename(self, url: str) -> str:
        """将URL转换为唯一的文件名"""
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return f"{url_hash}.html"
    
    def get_file_path(self, url: str) -> Path:
        """获取URL对应的文件路径"""
        filename = self.url_to_filename(url)
        return self.docs_dir / filename
    
    def filter_new_urls(self, urls: List[str]) -> Tuple[List[str], List[str]]:
        """智能过滤未下载的URL"""
        new_urls = []
        existing_urls = []
        
        for url in urls:
            filename = self.url_to_filename(url)
            if filename in self.url_map and self._file_exists(filename):
                existing_urls.append(url)
            else:
                new_urls.append(url)
        
        return new_urls, existing_urls
    
    async def _download_single_url_async(self, url: str) -> bool:
        """异步下载单个URL，包含重试机制"""
        # 请求频率控制
        await asyncio.sleep(self.request_delay)
        
        file_path = self.get_file_path(url)
        filename = file_path.name
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=30) as response:
                    response.raise_for_status()
                    
                    # 确保响应是HTML
                    content_type = response.headers.get('content-type', '')
                    if 'html' not in content_type.lower():
                        logger.warning(f"非HTML响应: {url}, 内容类型: {content_type}")
                        return False
                    
                    # 读取并保存文件
                    html_content = await response.text()
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # 更新URL映射
                    self.url_map[filename] = {
                        'url': url,
                        'downloaded_at': datetime.now().isoformat(),
                        'file_size': len(html_content.encode('utf-8'))
                    }
                    
                    self._save_url_map()
                    logger.info(f"下载成功: {url} -> {filename}")
                    return True
                    
        except aiohttp.ClientError as e:
            logger.error(f"下载失败: {url}, 错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"下载失败: {url}, 错误: {str(e)}")
            return False
    
    async def _concurrent_download(self, urls: List[str], max_concurrent: int) -> Dict[str, bool]:
        """并发下载实现，控制并发数和请求间隔"""
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(url):
            async with semaphore:
                return await self._download_single_url_async(url)
        
        # 执行并发下载
        tasks = [download_with_semaphore(url) for url in urls]
        download_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for url, result in zip(urls, download_results):
            if isinstance(result, Exception):
                logger.error(f"下载失败: {url}, 错误: {result}")
                results[url] = False
            else:
                results[url] = result
        
        return results
    
    async def download_urls(self, urls: List[str], max_concurrent: int = MAX_CONCURRENT_DOWNLOADS) -> Dict[str, bool]:
        """智能批量下载，支持并发控制和去重"""
        # 过滤新URL
        new_urls, existing_urls = self.filter_new_urls(urls)
        
        logger.info(f"下载状态: {len(existing_urls)}个已存在, {len(new_urls)}个需下载")

        # 并发下载新URL
        download_results = {}
        if new_urls:
            download_results = await self._concurrent_download(new_urls, max_concurrent)

        # 合并结果：已存在文件标记为'skipped'，下载结果保持原样
        results = {}

        # 先添加下载结果
        results.update(download_results)

        # 然后添加已存在文件的结果（标记为None表示跳过）
        for url in existing_urls:
            results[url] = None  # None表示跳过，不是下载

        newly_downloaded = sum(1 for success in download_results.values() if success)
        logger.info(f"下载完成: {newly_downloaded}/{len(new_urls)}个新下载, {len(existing_urls)}个已存在跳过")

        return results
    
    def get_url_map(self) -> Dict[str, Dict[str, Any]]:
        """获取URL到文件路径的映射关系"""
        return self.url_map
    
    def get_file_stats(self) -> Dict[str, Any]:
        """获取下载文件统计信息"""
        total_files = len(self.url_map)
        total_size = sum(
            info.get('file_size', 0)
            for info in self.url_map.values()
            if isinstance(info, dict)
        )
        
        # 计算下载时间分布
        download_dates = {}
        for info in self.url_map.values():
            if isinstance(info, dict) and 'downloaded_at' in info:
                date = info['downloaded_at'].split('T')[0]
                download_dates[date] = download_dates.get(date, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'download_directory': str(self.docs_dir),
            'download_dates': download_dates,
            'url_map_file': str(self.url_map_file)
        }
    
    def delete_old_files(self, days: int = 30) -> int:
        """删除指定天数前的旧文件"""
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        files_to_delete = []
        for filename, info in self.url_map.items():
            if isinstance(info, dict) and 'downloaded_at' in info:
                downloaded_time = datetime.fromisoformat(info['downloaded_at']).timestamp()
                if downloaded_time < cutoff_time:
                    files_to_delete.append(filename)
        
        for filename in files_to_delete:
            file_path = self.docs_dir / filename
            try:
                if file_path.exists():
                    file_path.unlink()
                    del self.url_map[filename]
                    deleted_count += 1
            except Exception as e:
                logger.error(f"删除文件失败: {file_path}, 错误: {e}")
        
        if files_to_delete:
            self._save_url_map()
        
        logger.info(f"删除旧文件完成: {deleted_count}个文件被删除")
        return deleted_count