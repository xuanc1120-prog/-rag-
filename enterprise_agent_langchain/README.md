# Enterprise Agent MVP - LangChain Edition

这是原始 `enterprise_agent_mvp` 的 LangChain 技术栈版本。

## 目标

保持同样的业务场景不变：

- 企业知识库问答
- 多轮支持对话
- 工单创建 / 查询 / 升级
- OpenAI 兼容接口与 Anthropic 风格接口切换

但实现方式改成 LangChain 风格：

- `ChatOpenAI` / `ChatAnthropic`
- `@tool` 工具定义
- `create_agent(...)` 创建 Agent
- LangChain 消息对象作为内部上下文

## 目录结构

```text
enterprise_agent_langchain/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ schemas.py
│  ├─ utils.py
│  ├─ langchain_runtime/
│  ├─ tools/
│  ├─ rag/
│  ├─ db/
│  └─ static/
├─ data/
│  └─ knowledge_base.txt
└─ requirements.txt
```

## 运行前准备

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## 示例 `.env`

### OpenAI 兼容接口

```env
LLM_PROVIDER=openai_compatible
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic 风格接口

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

如果你使用的是 Anthropic 兼容平台，例如 MiniMax 的 `/anthropic/v1` 风格接口，可把 `ANTHROPIC_BASE_URL` 指向兼容地址。

## 启动

```bash
uvicorn app.main:app --reload
```

默认地址：

- 前端主页：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`

## 说明

这个版本重点是帮助你学习：

1. 手写 agent loop 和 LangChain agent 的差别
2. 工具调用在 LangChain 里是怎么组织的
3. 同一个业务题目如何迁移到不同技术栈

