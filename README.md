# 转专业知识库问答系统（RAG）

我的一个练手项目

基于 **RAG（检索增强生成）** 的高校转专业政策问答系统。将学校教务处发布的《转专业管理办法》抓取入库，
通过向量检索 + 大模型生成，实现**有据可依、可溯源**的政策问答，避免大模型凭空编造规章制度。

> 数据来源示例：太原工业学院教务处《转专业管理办法》（太工院发〔2022〕151号）


---

## 系统流程

```
网页正文抓取  →  文本切分  →  向量化入库  →  语义检索  →  大模型生成回答
  2.1paqu.py     2.2qiefeng.py   2.3cunchu.py   Retriever    2.4agent.py
```

| 阶段 | 脚本 | 说明 |
|---|---|---|
| ① 数据采集 | `2.1paqu.py` | 用 `WebBaseLoader` + `SoupStrainer` 只抓取正文容器，输出 `web_content.txt` |
| ② 文本切分 | `2.2qiefeng.py` | `RecursiveCharacterTextSplitter`，`chunk_size=500 / overlap=20`，按中文标点优先切分 |
| ③ 向量入库 | `2.3cunchu.py` | 千问 `text-embedding-v4` 生成向量，持久化到 `zhuanzhuanye_db/` |
| ④ 问答 Agent | `2.4agent.py` | `create_agent` 注册 `search_knowledge` 工具，强制先检索再作答 |

### 技术选型

| 组件 | 选型 |
|---|---|
| 编排框架 | LangChain 1.x |
| 向量库 | Chroma（本地持久化，无需外部服务） |
| 嵌入模型 | 阿里云百炼 `text-embedding-v4` |
| 对话模型 | DeepSeek `deepseek-v4-flash`（`temperature=0`，保证稳定复现） |

### 防幻觉设计

`2.4agent.py` 中的 system prompt 设置了硬性规则：

1. 转专业相关问题**必须**调用 `search_knowledge` 工具，禁止直接作答；
2. 回答内容只能来自检索结果，**禁止编造**不存在的规定；
3. 检索为空时如实告知「知识库暂未查询到该信息」，而不是猜测。

同时工具返回值会带上 `[来源 N: ...]` 标记，便于人工核对原文。

---

## 快速开始

### 1. 环境要求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)（包管理）

### 2. 安装依赖

```bash
git clone <(https://github.com/fenggg06/rag-demo)>
cd agent-uv
uv sync
```

### 3. 配置 API Key

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

然后编辑 `.env` 填入真实密钥：

```ini
DEEPSEEK_API_KEY=sk-xxxxxxxx        # https://platform.deepseek.com/
QIANWEN_API_KEY=sk-xxxxxxxx         # https://bailian.console.aliyun.com/
```

> ⚠️ `.env` 已被 `.gitignore` 忽略，**不要**把真实密钥提交到仓库。

### 4. 运行

```bash
# 第一步：抓取政策原文（可选，仓库已含抓取结果 web_content.txt）
uv run 2.1paqu.py

# 第二步：查看切分效果，确认块大小合理
uv run 2.2qiefeng.py

# 第三步：向量化并写入数据库
uv run 2.3cunchu.py

# 第四步：启动问答（输入 exit 退出）
uv run 2.4agent.py
```

问答效果示例：

```
===== 转专业知识库问答助手（输入 exit 退出）=====

请输入你的问题: 休学期间可以转专业吗？

🤖 回答：不可以。根据《转专业管理办法》第三条第 2 款，正在休学或保留学籍的学生不得转专业。
```

---

## 项目结构

```
.
├── 2.1paqu.py            # ① 网页正文抓取
├── 2.2qiefeng.py         # ② 文本切分预览
├── 2.3cunchu.py          # ③ 向量化入库
├── 2.4agent.py           # ④ RAG 问答 Agent
├── web_content.txt       # 抓取到的政策原文（含来源元数据头）
├── zhuanzhuanye_db/      # Chroma 向量库（已入库，可直接检索）
├── .env.example          # 环境变量模板
└── pyproject.toml        # 依赖与项目元数据
```


---

## 常见问题

**Q：换个学校能用吗？**
可以。修改 `2.1paqu.py` 里的 `SOURCE_URL` 和 `CONTENT_SELECTOR` 指向目标学校教务处的正文容器，
再依次重跑 ①②③ 即可。若源文档已是本地文件，直接用 `TextLoader` 读取，跳过第 ① 步。
（注意同时改写 `2.2qiefeng.py` 与 `2.3cunchu.py` 中的 `WebBaseLoader`/`TextLoader` 路径。）



**Q：为什么检索结果不理想？**
优先调整 `2.2qiefeng.py` / `2.3cunchu.py` 中的 `chunk_size` 与 `chunk_overlap`。
政策类文本条款边界清晰，过大的块会稀释语义，过小则会切断条款，建议在 300～600 字之间试验。

---

