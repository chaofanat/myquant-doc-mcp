from pathlib import Path
from typing import Any, Dict, List
import re

import jieba
import jieba.analyse
from bs4 import BeautifulSoup
from whoosh import index
from whoosh.analysis import Token, Tokenizer
from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.highlight import ContextFragmenter, HtmlFormatter
from whoosh.qparser import MultifieldParser, OrGroup, QueryParser
from whoosh.query import And, Every, Or
from whoosh.scoring import BM25F

from config import INDEX_DIR
from utils import logger

# 预初始化jieba，避免首次搜索时的延迟
logger.info("预初始化jieba分词器...")
jieba.initialize()  # 预加载词典和模型

# 添加专业术语到jieba词典，提高分词准确性
custom_terms = [
    "掘金量化",
    "策略",
    "回测",
    "行情",
    "交易",
    "接口",
    "SDK",
    "实时行情",
    "历史数据",
    "K线",
    "分笔",
    "逐笔",
    "委托",
    "成交",
    "持仓",
    "账户",
    "资金",
    "风控",
    "滑点",
    "手续费",
    "保证金",
    "多因子",
    "Alpha",
    "量价",
    "技术指标",
    "基本面",
    "股票",
    "期货",
    "期权",
    "基金",
    "债券",
    "外汇",
    "数字货币",
    "Python",
    "C++",
    "C#",
    "MATLAB",
    "API",
    "数据查询",
    "下单",
    "撤单",
    "查询",
    "订阅",
    "推送",
    "回调",
    "事件",
    "MACD",
    "KDJ",
    "RSI",
    "布林带",
    "均线",
    "成交量",
    "换手率",
    "市盈率",
    "市净率",
    "ROE",
    "毛利率",
    "净利率",
]

for term in custom_terms:
    jieba.add_word(term, freq=10000)  # 高频词，确保不被切分

# 触发一次分词操作，完成完整的初始化
list(jieba.cut("初始化测试"))
logger.info("jieba分词器初始化完成，已加载专业术语词典")


class ImprovedChineseTokenizer(Tokenizer):
    """改进的中文分词器，支持位置信息"""

    def __call__(
        self,
        text,
        positions=False,
        chars=False,
        keeporiginal=False,
        removestops=True,
        start_pos=0,
        start_char=0,
        **kwargs,
    ):
        """
        执行分词并生成Token流

        Args:
            text: 待分词文本
            positions: 是否记录位置信息
            chars: 是否记录字符位置
            keeporiginal: 是否保留原始文本
            removestops: 是否移除停用词
            start_pos: 起始位置
            start_char: 起始字符位置
        """
        pos = start_pos
        char_pos = start_char

        # 使用jieba进行分词
        for word in jieba.cut_for_search(text):  # 使用搜索模式，更细粒度的切分
            if not word or not word.strip():
                continue

            word = word.strip()

            # 创建Token对象
            t = Token()
            t.text = word  # type: ignore
            t.boost = 1.0  # type: ignore
            t.stopped = False  # type: ignore

            if positions:
                t.pos = pos  # type: ignore

            if chars:
                # 查找词在原文中的位置
                word_start = text.find(word, char_pos - start_char)
                if word_start >= 0:
                    t.startchar = start_char + word_start  # type: ignore
                    t.endchar = t.startchar + len(word)  # type: ignore
                    char_pos = word_start + len(word)
                else:
                    t.startchar = char_pos  # type: ignore
                    t.endchar = char_pos + len(word)  # type: ignore
                    char_pos += len(word)

            yield t
            pos += 1


def improved_chinese_analyzer():
    """创建改进的中文分析器"""
    return ImprovedChineseTokenizer()


class WhooshSearchEngine:
    """优化的Whoosh搜索引擎"""

    def __init__(self, index_dir: Path = INDEX_DIR):
        self.index_dir = index_dir

        # 使用改进的Schema，添加字段权重
        self.schema = Schema(
            title=TEXT(
                stored=True, analyzer=improved_chinese_analyzer(), field_boost=3.0
            ),
            content=TEXT(
                stored=True, analyzer=improved_chinese_analyzer(), field_boost=1.0
            ),
            headings=TEXT(
                stored=True, analyzer=improved_chinese_analyzer(), field_boost=2.0
            ),
            code_blocks=TEXT(
                stored=True, analyzer=improved_chinese_analyzer(), field_boost=1.5
            ),
            tags=KEYWORD(stored=True, commas=True, field_boost=2.5),
            url=ID(stored=True, unique=True),
            file_path=ID(stored=True),
        )

        self.index = self._get_or_create_index()

        # 使用BM25F评分算法，支持字段权重
        self.scorer = BM25F()

    def _get_or_create_index(self) -> index.Index:
        """获取或创建索引"""
        if index.exists_in(self.index_dir):
            logger.info(f"使用现有索引: {self.index_dir}")
            return index.open_dir(self.index_dir)
        else:
            logger.info(f"创建新索引: {self.index_dir}")
            return index.create_in(self.index_dir, self.schema)

    def _parse_html(self, file_path: Path, url: str) -> Dict[str, Any]:
        """增强的HTML文档解析，提取更多结构化内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # 移除脚本和样式标签
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # 提取标题
        title = ""
        if soup.title and soup.title.string:
            title = str(soup.title.string).strip()

        # 如果title标签没有内容，尝试从h1获取
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()

        # 提取正文内容 - 使用增强的多方法提取
        content_parts = []

        # 方法1: 尝试查找主要内容容器
        content_containers = [
            "content",
            "main-content",
            "theme-default-content",
            "article-content",
            "post-content",
            "entry-content",
            "page-content",
            "documentation-content",
        ]

        main_content = None
        for container_class in content_containers:
            main_content = soup.find(["div", "main", "article"], class_=container_class)
            if main_content:
                break

        # 如果找不到特定容器，使用main或article标签
        if not main_content:
            main_content = soup.find(["main", "article"])

        # 如果还是找不到，使用body
        if not main_content:
            main_content = soup.body if soup.body else soup

        # 提取段落文本
        if main_content:
            # 提取所有段落
            for p in main_content.find_all("p"):
                text = p.get_text(separator=" ", strip=True)
                if text:
                    content_parts.append(text)

            # 提取列表项
            for li in main_content.find_all("li"):
                text = li.get_text(separator=" ", strip=True)
                if text:
                    content_parts.append(text)

            # 提取表格内容
            for table in main_content.find_all("table"):
                for row in table.find_all("tr"):
                    cells = [
                        td.get_text(strip=True) for td in row.find_all(["td", "th"])
                    ]
                    if cells:
                        content_parts.append(" | ".join(cells))

            # 提取div中的文本（排除已提取的元素）
            for div in main_content.find_all("div", recursive=False):
                text = div.get_text(separator=" ", strip=True)
                if text and len(text) > 10:  # 只添加有意义的文本
                    content_parts.append(text)

        # 合并内容并去重
        content = "\n".join(dict.fromkeys(content_parts))  # 保持顺序的去重

        # 如果内容太少，使用整个body的文本
        if len(content) < 100 and soup.body:
            content = soup.body.get_text(separator="\n", strip=True)

        # 清理内容：移除多余空白、特殊字符
        content = re.sub(r"\s+", " ", content)  # 多个空白符替换为单个空格
        content = re.sub(r"\n+", "\n", content)  # 多个换行替换为单个换行

        # 提取所有标题（h1-h6）
        headings = []
        for h in (
            main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if main_content
            else []
        ):
            heading_text = h.get_text(strip=True)
            if heading_text:
                headings.append(heading_text)
        headings_text = "\n".join(headings)

        # 提取代码块 - 包括code、pre标签
        code_blocks = []
        for code in main_content.find_all(["code", "pre"]) if main_content else []:
            code_text = code.get_text(strip=True)
            if code_text and len(code_text) > 2:  # 排除太短的代码片段
                code_blocks.append(code_text)
        code_blocks_text = "\n\n".join(code_blocks)

        # 提取标签（从meta标签的keywords中提取）
        tags = []
        keywords_meta = soup.find("meta", attrs={"name": "keywords"})
        if keywords_meta and keywords_meta.get("content"):
            meta_content = keywords_meta.get("content")
            if meta_content and isinstance(meta_content, str):
                if "、" in meta_content:
                    tags = [tag.strip() for tag in meta_content.split("、") if tag.strip()]
                else:
                    tags = [tag.strip() for tag in meta_content.split(",") if tag.strip()]

        # 如果没有keywords meta标签，尝试从内容中提取关键词
        if not tags:
            # 使用jieba提取关键词
            try:
                keywords = jieba.analyse.extract_tags(
                    content, topK=10, withWeight=False
                )
                tags = keywords[:5]  # 只取前5个
            except Exception as e:
                logger.debug(f"关键词提取失败: {e}")

        return {
            "title": title,
            "content": content,
            "headings": headings_text,
            "code_blocks": code_blocks_text,
            "tags": ",".join(tags),
            "url": url,
            "file_path": str(file_path),
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

        # 检查哪些文档已经在索引中
        with self.index.searcher() as searcher:
            existing_urls = set()
            # 使用Every查询获取所有文档
            all_docs = searcher.search(Every(), limit=None)
            for doc in all_docs:
                existing_urls.add(doc.get("url", ""))

        # 只处理不在索引中的文档
        new_documents = []
        for item in file_url_pairs:
            url = item["url"]
            if url not in existing_urls:
                new_documents.append(item)
            else:
                skipped_count += 1

        if not new_documents:
            logger.info(
                f"所有文档已存在，跳过索引: {skipped_count}/{total_count}个文档"
            )
            return {
                "total_count": total_count,
                "success_count": 0,
                "failure_count": 0,
                "skipped_count": skipped_count,
            }

        # 只为新文档创建索引
        for item in new_documents:
            file_path = Path(item["file_path"])
            url = item["url"]

            try:
                document = self._parse_html(file_path, url)

                with self.index.writer() as writer:
                    writer.add_document(**document)

                success_count += 1
            except Exception as e:
                logger.error(f"添加新文档失败: {url}, 错误: {e}")

        logger.info(
            f"索引更新完成: {success_count}个新文档添加, {skipped_count}个已存在跳过"
        )

        return {
            "total_count": total_count,
            "success_count": success_count,
            "failure_count": len(new_documents) - success_count,
            "skipped_count": skipped_count,
        }

    def update_index(self, file_url_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """更新索引"""
        return self.add_documents(file_url_pairs)

    def search(self, keyword: str, max_results: int = 10) -> Dict[str, Any]:
        """增强的关键词搜索 - 使用多字段搜索和OR组合"""
        with self.index.searcher(weighting=self.scorer) as searcher:
            # 使用MultifieldParser在多个字段中搜索
            parser = MultifieldParser(
                ["title", "content", "headings", "code_blocks"],
                self.schema,
                group=OrGroup,  # 使用OR组合，扩大搜索范围
            )

            try:
                query = parser.parse(keyword)
            except Exception as e:
                logger.warning(f"查询解析失败: {keyword}, 错误: {e}")
                # 降级为简单搜索
                parser = QueryParser("content", self.schema)
                query = parser.parse(keyword)

            results = searcher.search(query, limit=max_results * 2)  # 多取一些结果
            return self._format_results(list(results), keyword, searcher)  # type: ignore

    def boolean_search(
        self, query_string: str, max_results: int = 10
    ) -> Dict[str, Any]:
        """布尔查询搜索"""
        try:
            with self.index.searcher(weighting=self.scorer) as searcher:
                try:
                    # 使用MultifieldParser支持多字段布尔查询
                    parser = MultifieldParser(
                        ["title", "content", "headings", "code_blocks"], self.schema
                    )

                    query = parser.parse(query_string)
                    results = searcher.search(query, limit=max_results * 2)
                    return self._format_results(list(results), query_string, searcher)  # type: ignore

                except Exception as e:
                    logger.warning(f"布尔查询解析失败: {query_string}, 错误: {e}")

                    # 降级：提取关键词进行OR搜索
                    cleaned_query = re.sub(
                        r"\b(AND|OR|NOT)\b", " ", query_string, flags=re.IGNORECASE
                    )
                    cleaned_query = re.sub(r"[a-zA-Z_]+:", "", cleaned_query)
                    cleaned_query = re.sub(r'["\(\)]', " ", cleaned_query)
                    cleaned_query = " ".join(cleaned_query.split())

                    if cleaned_query.strip():
                        parser = MultifieldParser(
                            ["title", "content", "headings", "code_blocks"],
                            self.schema,
                            group=OrGroup,
                        )
                        simple_query = parser.parse(cleaned_query.strip())
                        results = searcher.search(simple_query, limit=max_results * 2)
                        logger.info(
                            f"使用简化查询: '{cleaned_query.strip()}' 替代原查询"
                        )
                        return self._format_results(results, query_string, searcher)
                    else:
                        return {
                            "query": query_string,
                            "total_hits": 0,
                            "results": [],
                            "note": "查询中没有有效的搜索关键词",
                        }

        except Exception as e:
            logger.error(f"布尔搜索失败: {query_string}, 错误: {e}")
            return {
                "query": query_string,
                "total_hits": 0,
                "results": [],
                "error": str(e),
            }

    def phrase_search(self, phrase: str, max_results: int = 10) -> Dict[str, Any]:
        """精确短语搜索 - 在多个字段中搜索"""
        with self.index.searcher(weighting=self.scorer) as searcher:
            # 在多个字段中进行短语搜索
            from whoosh.query import Phrase

            # 分词
            terms = list(jieba.cut(phrase))

            # 在多个字段中创建短语查询
            queries = []
            for field in ["title", "content", "headings", "code_blocks"]:
                queries.append(Phrase(field, terms))

            # 使用OR组合多个字段的查询
            query = Or(queries)

            results = searcher.search(query, limit=max_results * 2)
            return self._format_results(results, phrase, searcher)

    def fuzzy_search(
        self, term: str, max_distance: int = 2, max_results: int = 10
    ) -> Dict[str, Any]:
        """模糊搜索 - 在多个字段中搜索"""
        with self.index.searcher(weighting=self.scorer) as searcher:
            from whoosh.query import FuzzyTerm

            # 在多个字段中创建模糊查询
            queries = []
            for field in ["title", "content", "headings", "code_blocks"]:
                queries.append(FuzzyTerm(field, term, maxdist=max_distance))

            # 使用OR组合多个字段的查询
            query = Or(queries)

            results = searcher.search(query, limit=max_results * 2)
            return self._format_results(results, term, searcher)

    def tag_search(
        self, tag: str, keyword: str = "", max_results: int = 10
    ) -> Dict[str, Any]:
        """标签过滤搜索"""
        with self.index.searcher(weighting=self.scorer) as searcher:
            # 标签查询
            parser = QueryParser("tags", self.schema)
            tag_query = parser.parse(tag)

            if keyword:
                # 标签 + 关键词组合搜索
                content_parser = MultifieldParser(
                    ["title", "content", "headings", "code_blocks"],
                    self.schema,
                    group=OrGroup,
                )
                content_query = content_parser.parse(keyword)
                query = And([tag_query, content_query])
            else:
                # 仅标签搜索
                query = tag_query

            results = searcher.search(query, limit=max_results * 2)
            return self._format_results(results, f"tag:{tag} {keyword}", searcher)

    def _format_results(
        self, results: List[Any], original_query: str, searcher=None
    ) -> Dict[str, Any]:
        """格式化搜索结果，使用Whoosh的高亮功能"""
        formatted_results = []

        # 配置高亮器
        fragmenter = ContextFragmenter(maxchars=300, surround=50)
        formatter = HtmlFormatter(tagname="mark", between="...")

        for hit in results:
            # 安全获取字段值
            title = hit.get("title", "") or ""
            content = hit.get("content", "") or ""
            url = hit.get("url", "")
            score = hit.score

            # 使用Whoosh的高亮功能
            highlighted_title = title
            highlighted_content = (
                content[:300] + "..." if len(content) > 300 else content
            )

            try:
                # 高亮标题
                if title:
                    highlighted_title = hit.highlights("title", text=title, top=1)
                    if not highlighted_title:
                        highlighted_title = title

                # 高亮内容 - 显示最相关的片段
                if content:
                    highlighted_content = hit.highlights("content", text=content, top=3)
                    if not highlighted_content:
                        # 如果没有高亮片段，尝试其他字段
                        headings = hit.get("headings", "")
                        if headings:
                            highlighted_content = hit.highlights(
                                "headings", text=headings, top=2
                            )

                        if not highlighted_content:
                            # 使用内容的开头
                            highlighted_content = content[:300] + (
                                "..." if len(content) > 300 else ""
                            )

            except Exception as e:
                logger.debug(f"高亮处理失败: {e}")
                # 回退到简单截取
                highlighted_content = content[:300] + (
                    "..." if len(content) > 300 else ""
                )

            formatted_results.append(
                {
                    "title": title,
                    "content": content[:500],  # 返回更多原始内容
                    "url": url,
                    "score": score,
                    "highlights": {
                        "title": highlighted_title,
                        "content": highlighted_content,
                    },
                }
            )

        return {
            "query": original_query,
            "total_hits": len(results),
            "results": formatted_results,
        }

    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        with self.index.searcher() as searcher:
            doc_count = searcher.doc_count()

            # 获取字段信息
            field_info = {}
            for field_name in self.schema.names():
                field_info[field_name] = {
                    "type": str(type(self.schema[field_name]).__name__),
                    "stored": self.schema[field_name].stored,
                }

            return {
                "total_docs": doc_count,
                "index_dir": str(self.index_dir),
                "schema_fields": field_info,
                "scorer": str(type(self.scorer).__name__),
            }

    def rebuild_index(self, file_url_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """重建索引"""
        # 删除旧索引
        if self.index_dir.exists():
            for file in self.index_dir.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"删除索引文件失败: {file}, 错误: {e}")

        # 创建新索引
        self.index = self._get_or_create_index()

        # 添加文档
        return self.add_documents(file_url_pairs)
