import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent

# 默认文档下载目录
DEFAULT_DOCS_DIR = ROOT_DIR / "docs"

# 可通过环境变量覆盖
DOCS_DIR = Path(os.getenv("MYQUANT_DOC_MCP_DOCS_DIR", DEFAULT_DOCS_DIR))

# 默认上下文行数
DEFAULT_CONTEXT_LINES = 4

# 搜索结果限制配置
DEFAULT_MAX_RESULTS = int(os.getenv("MYQUANT_DOC_MCP_MAX_RESULTS", "10"))  # 默认最多返回10个结果
DEFAULT_ENABLE_RESULT_SCORING = os.getenv("MYQUANT_DOC_MCP_ENABLE_RESULT_SCORING", "true").lower() == "true"  # 是否启用结果评分排序
DEFAULT_ENABLE_CONTENT_SUMMARY = os.getenv("MYQUANT_DOC_MCP_ENABLE_CONTENT_SUMMARY", "false").lower() == "true"  # 是否启用内容摘要

# 搜索API配置
SEARCH_API_URL = "https://www.myquant.cn/Search/indexes/mq-website-docs/search"

# 请求头配置
REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Authorization": "Bearer MYQUANT",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Cookie": "doc=64b3146a5acd9f7d02bde79df48727ae; sl-session=oskrQCQsMGnyiuYlogNwCA==; gr_user_id=fe5cc2fc-0efa-4ab5-8542-a449cbdbe2bf; 945f221bc86a3207_gr_session_id=acb95417-5cc7-4cf7-8eae-12c07f6d5880; 945f221bc86a3207_gr_session_id_sent_vst=acb95417-5cc7-4cf7-8eae-12c07f6d5880; Hm_lvt_43263a73f5a3ee526aa272d164acb53b=1764678310; HMACCOUNT=419FBBF2FE4D14B8; Hm_lpvt_43263a73f5a3ee526aa272d164acb53b=1764678525",
    "DNT": "1",
    "Host": "www.myquant.cn",
    "Origin": "https://www.myquant.cn",
    "Referer": "https://www.myquant.cn/docs2/sdk/cSharp/%E6%95%B0%E6%8D%AE%E6%9F%A5%E8%AF%A2%E5%87%BD%E6%95%B0/%E9%80%9A%E7%94%A8%E6%95%B0%E6%8D%AE%E5%87%BD%E6%95%B0%EF%BC%88%E5%85%8D%E8%B4%B9%EF%BC%89.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "X-Meilisearch-Client": "Meilisearch Vuepress (v0.13.0) ; Meilisearch docs-searchbar.js (v2.5.0) ; Meilisearch JavaScript (v0.30.0)",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

# 文档下载请求头
DOC_DOWNLOAD_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://www.myquant.cn/docs2/",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}
