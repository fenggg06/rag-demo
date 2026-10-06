import os
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
from bs4 import SoupStrainer
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader(
    "https://jwc.tit.edu.cn/info/1053/6730.htm",
    requests_kwargs={"verify": False},
    bs_kwargs=dict(parse_only=SoupStrainer(id="vsb_content"))
)
docs = loader.load()
print(f"文档内容：{docs[0].page_content[:150]}...")
with open("web_content.txt", "w", encoding="utf-8") as f:
    # 把元数据写在md头部
    f.write(f"""---
source_url: {docs[0].metadata.get('source')}
title: {docs[0].metadata.get('title')}
---

{docs[0].page_content}
""")
print("✅ Markdown已保存至 web_content.txt")