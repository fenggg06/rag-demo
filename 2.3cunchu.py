from langchain_community.document_loaders import TextLoader

loader = TextLoader("./web_content.txt",encoding="utf-8")

docs = loader.load()

from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=20,
    separators=["\n\n", "\n", "。", "!", "?", ";", ",", " ", ""],
    )

chunks = text_splitter.split_documents(docs)

print(f"切分后: {len(chunks)} 块\n")

for i, chunk in enumerate(chunks):
    print(f"--- 块 {i+1} ({len(chunk.page_content)} 字) ---")
    print(chunk.page_content)
    print()
from langchain_chroma import Chroma

import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-v4",
                              api_key=os.environ["QIANWEN_API_KEY"],
                              base_url="https://maas.qianwenaiapi.com/compatible-mode/v1",
                            check_embedding_ctx_length=False,
                            chunk_size=10,
                              )
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./zhuanzhuanye_db",
    )
print(f"已建立索引:{len(chunks)}个文档块")