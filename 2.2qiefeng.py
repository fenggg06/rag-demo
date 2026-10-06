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