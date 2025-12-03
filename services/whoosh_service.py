from pathlib import Path
from typing import List, Dict, Any, Optional
import jieba
from config import INDEX_DIR, HIGHLIGHT_PRE, HIGHLIGHT_POST
from utils import logger

# 预初始化jieba，避免首次搜索时的延迟
logger.info("预初始化jieba分词器...")
jieba.initialize()  # 预加载词典和模型
# 触发一次分词操作，完成完整的初始化
list(jieba.cut("初始化测试"))
logger.info("jieba分词器初始化完成")

from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.qparser import QueryParser, MultifieldParser, plugins
from whoosh.query import Phrase, FuzzyTerm, Term, And
from whoosh.analysis import Tokenizer, Token
from bs4 import BeautifulSoup

class ChineseTokenizer(Tokenizer):
    """中文分词器"""

    def __call__(self, text, **kwargs):
        # 使用jieba进行分词，并生成Token对象
        pos = 0
        for token in jieba.cut(text):
            if token.strip():  # 跳过空白token
                # 创建Token对象，设置所有必要属性
                t = Token()
                t.text = token.strip()
                t.boost = 1.0
                t.pos = pos
                # 设置startchar和endchar为None，避免错误
                t.startchar = None
                t.endchar = None
                yield t
                pos += 1

def chinese_analyzer():
    """创建中文分析器"""
    return ChineseTokenizer()

class WhooshSearchEngine:
    """Whoosh搜索引擎"""
    
    def __init__(self, index_dir: Path = INDEX_DIR):
        self.index_dir = index_dir
        self.schema = Schema(
            title=TEXT(stored=True, analyzer=chinese_analyzer()),
            content=TEXT(stored=True, analyzer=chinese_analyzer()),
            headings=TEXT(stored=True, analyzer=chinese_analyzer()),
            code_blocks=TEXT(stored=True, analyzer=chinese_analyzer()),
            tags=KEYWORD(stored=True, commas=True),
            url=ID(stored=True, unique=True),
            file_path=ID(stored=True)
        )
        self.index = self._get_or_create_index()
    
    def _get_or_create_index(self) -> index.Index:
        """获取或创建索引"""
        if index.exists_in(self.index_dir):
            logger.info(f"使用现有索引: {self.index_dir}")
            return index.open_dir(self.index_dir)
        else:
            logger.info(f"创建新索引: {self.index_dir}")
            return index.create_in(self.index_dir, self.schema)
    
    def _parse_html(self, file_path: Path, url: str) -> Dict[str, Any]:
        """解析HTML文档，提取结构化内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题
        title = str(soup.title.string) if soup.title and soup.title.string else ""
        
        # 提取正文内容 - 使用增强的多方法提取
        content = ""
        
        # 方法1: 提取所有p标签内容
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        if paragraphs:
            content = "\n".join(paragraphs)
        else:
            # 方法2: 尝试提取常见的内容容器div
            content_div = None
            # 尝试多种常见的内容容器类名
            for container_class in ['content', 'main-content', 'theme-default-content']:
                content_div = soup.find('div', class_=container_class)
                if content_div:
                    break
            
            if content_div:
                # 提取content_div下的所有文本内容
                content = content_div.get_text(separator='\n')
            else:
                # 方法3: 直接使用body文本
                if soup.body:
                    content = soup.body.get_text(separator='\n')
        
        # 提取标题和副标题
        headings = "\n".join([h.get_text() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        
        # 提取代码块
        code_blocks = "\n".join([code.get_text() for code in soup.find_all('code')])
        
        # 提取标签（从meta标签的keywords中提取）
        tags = []
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            # 分割关键词并去除空格，支持英文逗号和中文逗号
            meta_content = keywords_meta.get('content')
            # 先尝试用中文逗号分割，如果没有则用英文逗号
            if '、' in meta_content:
                tags = [tag.strip() for tag in meta_content.split('、') if tag.strip()]
            else:
                tags = [tag.strip() for tag in meta_content.split(',') if tag.strip()]
        
        return {
            'title': title,
            'content': content,
            'headings': headings,
            'code_blocks': code_blocks,
            'tags': ",".join(tags),
            'url': url,
            'file_path': str(file_path)
        }
    
    def add_document(self, file_path: Path, url: str) -> bool:
        """添加单个文档到索引"""
        try:
            document = self._parse_html(file_path, url)
            
            with self.index.writer() as writer:
                writer.add_document(**document)
            
            logger.info(f"文档添加到索引: {url}")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {url}, 错误: {e}")
            return False
    
    def add_documents(self, file_url_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加文档到索引（智能跳过已存在的文档）"""
        success_count = 0
        skipped_count = 0
        total_count = len(file_url_pairs)

        # 首先检查哪些文档已经在索引中
        with self.index.searcher() as searcher:
            existing_urls = set()
            # 搜索所有文档来获取已存在的URL
            query = Term("url", "")  # 空查询会匹配所有文档
            all_docs = searcher.search(query, limit=None)
            for doc in all_docs:
                existing_urls.add(doc.get("url", ""))

        # 只处理不在索引中的文档
        new_documents = []
        for item in file_url_pairs:
            url = item['url']
            if url not in existing_urls:
                new_documents.append(item)
            else:
                skipped_count += 1

        if not new_documents:
            logger.info(f"所有文档已存在，跳过索引: {skipped_count}/{total_count}个文档")
            return {
                'total_count': total_count,
                'success_count': 0,
                'failure_count': 0,
                'skipped_count': skipped_count
            }

        # 只为新文档创建索引
        for item in new_documents:
            file_path = Path(item['file_path'])
            url = item['url']

            try:
                document = self._parse_html(file_path, url)

                # 为每个新文档创建单独的writer上下文
                with self.index.writer() as writer:
                    writer.add_document(**document)

                success_count += 1
            except Exception as e:
                logger.error(f"添加新文档失败: {url}, 错误: {e}")

        logger.info(f"索引更新完成: {success_count}个新文档添加, {skipped_count}个已存在跳过")

        return {
            'total_count': total_count,
            'success_count': success_count,
            'failure_count': len(new_documents) - success_count,
            'skipped_count': skipped_count
        }
    
    def update_index(self, file_url_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """更新索引"""
        return self.add_documents(file_url_pairs)
    
    def search(self, keyword: str, max_results: int = 10) -> Dict[str, Any]:
        """基础关键词搜索"""
        with self.index.searcher() as searcher:
            parser = QueryParser("content", self.schema)
            query = parser.parse(keyword)
            results = searcher.search(query, limit=max_results)
            return self._format_results(results, keyword, searcher)
    
    def boolean_search(self, query_string: str, max_results: int = 10) -> Dict[str, Any]:
        """布尔查询搜索"""
        try:
            with self.index.searcher() as searcher:
                try:
                    # 尝试使用复杂的布尔查询语法
                    parser = MultifieldParser(
                        ["title", "content", "headings", "code_blocks"],
                        self.schema
                    )
                    # 启用字段特定的语法
                    parser.add_plugin(plugins.WhitespacePlugin())
                    parser.add_plugin(plugins.PhrasePlugin())
                    parser.add_plugin(plugins.GroupPlugin())
                    parser.add_plugin(plugins.OperatorsPlugin())
                    parser.add_plugin(plugins.FieldsPlugin())

                    query = parser.parse(query_string)
                    results = searcher.search(query, limit=max_results)
                    return self._format_results(results, query_string, searcher)

                except Exception as e:
                    logger.warning(f"布尔查询解析失败: {query_string}, 错误: {e}")

                    # 降级为简单的关键词组合搜索
                    # 简化查询字符串，移除复杂的布尔语法
                    import re
                    # 提取关键词，去除布尔操作符和字段限定符
                    cleaned_query = re.sub(r'\b(AND|OR|NOT)\b', ' ', query_string, flags=re.IGNORECASE)
                    cleaned_query = re.sub(r'[a-zA-Z_]+:', '', cleaned_query)  # 移除字段限定符
                    cleaned_query = re.sub(r'["\(\)]', ' ', cleaned_query)  # 移除引号和括号
                    cleaned_query = ' '.join(cleaned_query.split())  # 清理多余空格

                    if cleaned_query.strip():
                        # 使用简化后的查询进行搜索
                        simple_parser = QueryParser("content", self.schema)
                        simple_query = simple_parser.parse(cleaned_query.strip())
                        results = searcher.search(simple_query, limit=max_results)
                        logger.info(f"使用简化查询: '{cleaned_query.strip()}' 替代原查询")
                        return self._format_results(results, query_string, searcher)
                    else:
                        # 如果没有有效关键词，返回空结果
                        return {
                            "query": query_string,
                            "total_hits": 0,
                            "results": [],
                            "note": "查询中没有有效的搜索关键词"
                        }

        except Exception as e:
            logger.error(f"布尔搜索失败: {query_string}, 错误: {e}")
            # 返回空结果而不是崩溃
            return {
                "query": query_string,
                "total_hits": 0,
                "results": [],
                "error": str(e)
            }
    
    def phrase_search(self, phrase: str, max_results: int = 10) -> Dict[str, Any]:
        """精确短语搜索"""
        with self.index.searcher() as searcher:
            parser = QueryParser("content", self.schema)
            query = Phrase("content", phrase.split())
            results = searcher.search(query, limit=max_results)
            return self._format_results(results, phrase, searcher)
    
    def fuzzy_search(self, term: str, max_distance: int = 2, max_results: int = 10) -> Dict[str, Any]:
        """模糊搜索"""
        with self.index.searcher() as searcher:
            query = FuzzyTerm("content", term, maxdist=max_distance)
            results = searcher.search(query, limit=max_results)
            return self._format_results(results, term, searcher)
    
    def tag_search(self, tag: str, keyword: str = "", max_results: int = 10) -> Dict[str, Any]:
        """标签过滤搜索"""
        with self.index.searcher() as searcher:
            # 使用QueryParser来解析标签搜索，这样可以处理逗号分隔的标签字段
            parser = QueryParser("tags", self.schema)
            tag_query = parser.parse(tag)
            
            if keyword:
                # 标签 + 关键词组合搜索
                content_query = QueryParser("content", self.schema).parse(keyword)
                query = And([tag_query, content_query])
            else:
                # 仅标签搜索
                query = tag_query
            
            results = searcher.search(query, limit=max_results)
            return self._format_results(results, f"tag:{tag} {keyword}", searcher)
    
    def _format_results(self, results: List[Any], original_query: str, searcher=None) -> Dict[str, Any]:
        """格式化搜索结果"""
        formatted_results = []

        for hit in results:
            # 高亮处理 - 安全处理可能的None值
            title = hit.get("title", "") or ""
            content = hit.get("content", "") or ""

            # 简单的关键词高亮实现
            highlighted_title = title
            highlighted_content = content[:300] + "..." if len(content) > 300 else content
            
            # 使用简单的关键词高亮实现
            if original_query and len(original_query.strip()) > 0:
                try:
                    # 简单的关键词高亮
                    keywords = original_query.split()
                    for keyword in keywords:
                        if len(keyword) > 1:  # 只高亮长度大于1的关键词
                            highlighted_content = highlighted_content.replace(
                                keyword, f"{HIGHLIGHT_PRE}{keyword}{HIGHLIGHT_POST}"
                            )
                            highlighted_title = highlighted_title.replace(
                                keyword, f"{HIGHLIGHT_PRE}{keyword}{HIGHLIGHT_POST}"
                            )
                except Exception as e:
                    logger.warning(f"高亮处理失败: {e}")
            
            formatted_results.append({
                "title": title,
                "content": content,
                "url": hit.get("url", ""),
                "score": hit.score,
                "highlights": {
                    "title": highlighted_title,
                    "content": highlighted_content
                }
            })
        
        return {
            "query": original_query,
            "total_hits": len(results),
            "results": formatted_results
        }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        with self.index.searcher() as searcher:
            return {
                "total_docs": searcher.doc_count(),
                "index_dir": str(self.index_dir),
                "schema_fields": list(self.schema.names())
            }
    
    def rebuild_index(self, file_url_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """重建索引"""
        # 删除旧索引
        if self.index_dir.exists():
            for file in self.index_dir.glob("*"):
                file.unlink()
        
        # 创建新索引
        self.index = self._get_or_create_index()
        
        # 添加文档
        return self.add_documents(file_url_pairs)