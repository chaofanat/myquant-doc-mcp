import pytest
from services.whoosh_service import WhooshSearchEngine
from pathlib import Path

class TestHTMLParsing:
    """测试HTML解析的各种边缘情况"""
    
    def test_parse_html_without_p_tags(self):
        """测试没有p标签的HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # HTML内容没有p标签，只有div和span
        html_content = """
        <html>
        <head>
            <title>无p标签测试文档</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <div class="content">
                <span>这是一段没有p标签的内容。</span>
                <div>这是另一段内容，也没有p标签。</div>
            </div>
        </body>
        </html>
        """
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test_no_p.html")
        tmp_file.write_text(html_content, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test/no_p")
        
        assert "title" in document
        assert "无p标签测试文档" in document["title"]
        assert "content" in document
        assert "没有p标签的内容" in document["content"]
        assert len(document["content"]) > 0
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_parse_html_with_main_content_div(self):
        """测试主要内容在main-content div中的HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # HTML内容主要在main-content div中，没有p标签，测试main-content div提取
        html_content = """
        <html>
        <head>
            <title>Main Content测试文档</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <div class="main-content">
                <h2>章节标题</h2>
                <div>这是第一段内容。</div>
                <div>这是第二段内容。</div>
            </div>
            <div class="sidebar">
                <div>这是侧边栏内容，不应该被包含。</div>
            </div>
        </body>
        </html>
        """
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test_main_content.html")
        tmp_file.write_text(html_content, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test/main_content")
        
        assert "title" in document
        assert "Main Content测试文档" in document["title"]
        assert "content" in document
        assert "第一段内容" in document["content"]
        assert "第二段内容" in document["content"]
        assert "侧边栏内容" not in document["content"]  # 侧边栏内容不应该被包含
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_parse_html_with_theme_default_content(self):
        """测试主要内容在theme-default-content div中的HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # HTML内容主要在theme-default-content div中（常见于VuePress等静态网站）
        html_content = """
        <html>
        <head>
            <title>Theme Default Content测试文档</title>
        </head>
        <body>
            <div class="theme-default-content">
                <h1>测试标题</h1>
                <p>这是第一段内容。</p>
                <div>
                    <p>这是嵌套的内容。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test_theme_content.html")
        tmp_file.write_text(html_content, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test/theme_content")
        
        assert "title" in document
        assert "Theme Default Content测试文档" in document["title"]
        assert "content" in document
        assert "第一段内容" in document["content"]
        assert "嵌套的内容" in document["content"]
        assert len(document["content"]) > 0
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_parse_html_only_body(self):
        """测试只有body内容的HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # HTML内容只有body标签，没有p标签和特定的content div
        html_content = """
        <html>
        <head>
            <title>只有Body测试文档</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <div>这是直接在body中的内容1。</div>
            <div>这是直接在body中的内容2。</div>
            <span>这是span内容。</span>
        </body>
        </html>
        """
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test_only_body.html")
        tmp_file.write_text(html_content, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test/only_body")
        
        assert "title" in document
        assert "只有Body测试文档" in document["title"]
        assert "content" in document
        assert "直接在body中的内容1" in document["content"]
        assert "直接在body中的内容2" in document["content"]
        assert "span内容" in document["content"]
        assert len(document["content"]) > 0
        
        # 清理临时文件
        tmp_file.unlink()
    
    def test_parse_html_empty_content(self):
        """测试空内容的HTML解析"""
        search_engine = WhooshSearchEngine()
        
        # HTML内容只有标题，没有实际内容
        html_content = """
        <html>
        <head>
            <title>空内容测试文档</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <div class="content"></div>
        </body>
        </html>
        """
        
        # 保存示例HTML到临时文件
        tmp_file = Path("tmp_test_empty_content.html")
        tmp_file.write_text(html_content, encoding="utf-8")
        
        document = search_engine._parse_html(tmp_file, "https://www.example.com/test/empty_content")
        
        assert "title" in document
        assert "空内容测试文档" in document["title"]
        assert "content" in document
        assert "headings" in document
        assert len(document["content"]) >= 0  # 空内容也是允许的
        
        # 清理临时文件
        tmp_file.unlink()
