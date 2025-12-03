import pytest
from services.whoosh_service import WhooshSearchEngine, ChineseTokenizer
from pathlib import Path
from bs4 import BeautifulSoup

class TestSearchEngine:
    """测试Whoosh搜索引擎"""
    
    def test_chinese_tokenizer(self):
        """测试中文分词器"""
        tokenizer = ChineseTokenizer()
        tokens = list(tokenizer("测试中文分词功能"))
        
        assert len(tokens) > 0
        assert any(token.text == "测试" for token in tokens)
    
    def test_get_or_create_index(self, index_dir, tmp_path):
        """测试获取或创建索引"""
        # 使用临时目录创建索引
        search_engine = WhooshSearchEngine(tmp_path)
        
        assert search_engine.index is not None
        assert len(search_engine.schema.names()) > 0
    
    def test_parse_html(self, sample_html):
        """测试HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test")
        
        assert "title" in document
        assert "测试文档" in document["title"]
        assert "content" in document
        assert "测试内容" in document["content"]
        assert "headings" in document
        assert "测试标题" in document["headings"]
        assert "code_blocks" in document
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_get_index_stats(self, tmp_path):
        """测试获取索引统计信息"""
        search_engine = WhooshSearchEngine(tmp_path)
        stats = search_engine.get_index_stats()
        
        assert "total_docs" in stats
        assert "index_dir" in stats
        assert "schema_fields" in stats
        assert len(stats["schema_fields"]) > 0
    
    def test_search(self, tmp_path, sample_html):
        """测试搜索功能"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 添加到索引
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行搜索
        results = search_engine.search("测试")
        
        assert "total_hits" in results
        assert results["total_hits"] >= 1
        assert "results" in results
        assert len(results["results"]) >= 1
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_boolean_search(self, tmp_path, sample_html):
        """测试布尔查询搜索"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 添加到索引
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行布尔搜索
        results = search_engine.boolean_search("title:测试 AND content:内容")
        
        assert "total_hits" in results
        assert "results" in results
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_phrase_search(self, tmp_path, sample_html):
        """测试短语搜索"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 添加到索引
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行短语搜索
        results = search_engine.phrase_search("测试文档")
        
        assert "total_hits" in results
        assert "results" in results
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_fuzzy_search(self, tmp_path, sample_html):
        """测试模糊搜索"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 添加到索引
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行模糊搜索（故意拼写错误）
        results = search_engine.fuzzy_search("测试档", max_distance=1)
        
        assert "total_hits" in results
        assert "results" in results
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_format_results(self, tmp_path, sample_html):
        """测试结果格式化"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 添加到索引
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行搜索
        results = search_engine.search("测试")
        
        assert "results" in results
        if results["results"]:
            first_result = results["results"][0]
            assert "title" in first_result
            assert "content" in first_result
            assert "url" in first_result
            assert "score" in first_result
            assert "highlights" in first_result
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_rebuild_index(self, tmp_path, sample_html):
        """测试重建索引"""
        search_engine = WhooshSearchEngine(tmp_path)
        
        # 创建一个测试文档
        tmp_file = Path("tmp_test.html")
        tmp_file.write_text(sample_html, encoding="utf-8")
        
        # 第一次添加
        search_engine.add_document(tmp_file, "https://www.example.com/test")
        
        # 执行搜索
        results_before = search_engine.search("测试")
        
        # 重建索引
        search_engine.rebuild_index([{
            "file_path": str(tmp_file),
            "url": "https://www.example.com/test"
        }])
        
        # 再次搜索
        results_after = search_engine.search("测试")
        
        assert "total_hits" in results_after
        
        # 清理临时文件
        tmp_file.unlink()