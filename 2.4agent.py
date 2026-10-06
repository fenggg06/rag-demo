from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-v4",
    api_key=os.environ["QIANWEN_API_KEY"],
    base_url="https://maas.qianwenaiapi.com/compatible-mode/v1",
    check_embedding_ctx_length=False,
    chunk_size=10,
)

loaded_store = Chroma(
    persist_directory="./zhuanzhuanye_db",
    embedding_function=embeddings,
)
retriever = loaded_store.as_retriever(search_kwargs={"k": 3})

@tool
def search_knowledge(query: str) -> str:
    """
    用于查询本校转专业规章制度、申请资格、休学能否转专业、申请时间、流程、成绩要求、名额等内容。
    当用户询问任何和转专业相关问题，调用这个工具检索知识库原文，不能凭空回答。
    Args:
        query: 用户的问题，直接作为检索词
    """
    docs = retriever.invoke(query)
    if not docs:
        return "没有找到相关的知识。"
    result = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "xx学校转专业知识库")
        result.append(f"[来源 {i}: {source}]\n{doc.page_content}")
    return "\n\n".join(result)

model = init_chat_model(
    "deepseek-v4-flash",
    temperature=0,
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

agent = create_agent(
    model=model,
    tools=[search_knowledge],
    system_prompt="""你是转专业知识库问答助手。
# 硬性规则（严格遵守，不能违反）
1. 用户只要询问转专业相关问题，**必须调用 search_knowledge 工具检索知识库**，禁止直接回答、禁止反问引导用户。
2. 所有回答内容只能来自工具返回的检索结果，**绝对不能编造、脑补不存在的规定**。
3. 如果工具返回「没有找到相关的知识」，直接如实告诉用户：知识库暂未查询到该信息。
4. 不要输出多余开场白、不要列举可查询的项目，直接基于检索结果作答。
5. 回答简洁准确。"""
)

# ===================== 实时问答循环 =====================
print("===== 转专业知识库问答助手（输入 exit 退出）=====")
while True:
    user_input = input("\n请输入你的问题:")
    if user_input.strip().lower() == "exit":
        print("👋 退出问答")
        break
    if not user_input.strip():
        continue
    resp = agent.invoke({"input": user_input})
    ai_msg = resp["messages"][-1]
    print("\n🤖 回答：", ai_msg.content)
