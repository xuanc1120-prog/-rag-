# 企业知识库问答与工单协同 Agent（LangChain 版）

这是 `enterprise_agent_mvp` 的 **LangChain 技术栈版本**。  
它保留了原始项目的业务目标：企业知识库问答、工单协同、多轮对话和模型 provider 切换；同时把核心实现改成更贴近主流 AI 应用框架的写法，方便展示你对 LangChain 生态的理解与使用能力。

## 项目定位

这个版本适合用来回答下面这类面试问题：

- 你会不会用 LangChain 搭 Agent？
- LangChain 版和手写 Agent 版有什么区别？
- 你如何在框架能力和可控性之间做取舍？
- 如何把业务工具接进 LangChain Agent？

## 这个版本展示了什么

- 使用 `create_agent(...)` 构建 Agent
- 使用 `ChatOpenAI` / `ChatAnthropic` 接入不同 provider
- 使用 `@tool` 暴露业务工具
- 保留知识库问答、工单创建、工单升级等业务动作
- 保留本地前端控制台和 FastAPI API

## 业务场景

和原始 MVP 一样，这个项目模拟企业支持场景：

1. 用户提出问题
2. Agent 优先检索知识库
3. 如果无法直接解决，则调用工具创建或升级工单
4. 输出最终回复，并保留可读的中间轨迹

它的重点不是做一个“能聊天”的页面，而是验证：

- LangChain 是否能胜任这类企业支持型 Agent 原型
- 工具调用是否能稳定接入业务逻辑
- 多 provider 接入是否能保持统一使用体验

## 技术栈

- Python
- FastAPI
- LangChain
- `langchain-openai`
- `langchain-anthropic`
- SQLite
- 本地知识库检索

## 与手写 Agent 版的差异

### 手写版更适合展示

- 你能否独立设计 Agent Loop
- 你如何定义 provider 抽象层
- 你是否理解消息结构与工具调度

### LangChain 版更适合展示

- 你会不会使用主流 AI 应用框架
- 你能否把业务工具接入框架生态
- 你是否理解框架封装后的运行方式

如果是在面试里，这两个版本放在一起会很有说服力：  
一个说明你理解底层结构，另一个说明你能使用行业常见工具链快速落地。

## 核心功能

- 企业知识库问答
- 多轮对话支持
- 创建工单 / 查询工单 / 升级工单
- OpenAI-compatible / Anthropic provider 切换
- LangChain Agent 运行时
- 本地前端控制台

## 项目结构

```text
enterprise_agent_langchain/
  app/
    langchain_runtime/   # LangChain 运行时封装
    tools/               # @tool 业务工具
    rag/                 # 轻量级检索
    db/                  # SQLite 工单存储
    static/              # 本地前端控制台
    config.py            # 配置加载
    schemas.py           # API 输入输出结构
    utils.py             # 工具函数与内容提取
    main.py              # FastAPI 入口
  data/
    knowledge_base.txt
  tests/
  .env.example
  requirements.txt
```

## 设计亮点

### 1. 模型工厂封装

项目通过 `model_factory.py` 统一创建 LangChain 模型对象，根据配置切换：

- `ChatOpenAI`
- `ChatAnthropic`

这样业务层不直接依赖具体模型 SDK，切换 provider 时成本更低。

### 2. 业务工具接入 LangChain

项目把工单相关能力封装成 `@tool`：

- 创建工单
- 查询工单
- 升级工单
- 查询知识库

这样 Agent 可以在合适的时机自动调用工具，而不是只输出自然语言答案。

### 3. Anthropic 兼容接口适配

为了兼容 MiniMax 这类 Anthropic 风格接口，项目在 LangChain 封装外又补了一层 base URL 处理逻辑，避免路径拼接错误导致的 `404`。

这部分非常适合在面试里讲，因为它能体现你：

- 不只是会调用框架
- 还会处理真实接入时的兼容性问题

### 4. 中文知识检索优化

为了让中文问答场景更稳定，检索器对中文 token 做了额外处理，避免简单英文分词逻辑导致中文命中率太差。

## 如何运行

### 1. 创建环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 2. 配置 `.env`

#### OpenAI-compatible

```env
LLM_PROVIDER=openai_compatible
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.5
```

#### Anthropic 风格接口

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
ANTHROPIC_MODEL=claude-4.6-sonnet
```

如果使用的是 Anthropic 兼容平台，例如 MiniMax 的 `/anthropic/v1` 风格接口，可以把 `ANTHROPIC_BASE_URL` 指向对应地址。

### 3. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后默认访问：

- 前端控制台：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## 推荐阅读顺序

1. `app/main.py`  
   看 API 层如何与 LangChain 运行时连接
2. `app/langchain_runtime/model_factory.py`  
   看模型 provider 如何切换
3. `app/langchain_runtime/agent_service.py`  
   看 LangChain Agent 是怎么组织起来的
4. `app/tools/support_tools.py`  
   看业务工具如何暴露给 Agent
5. `app/rag/retriever.py`  
   看知识库检索逻辑
6. `app/db/ticket_repository.py`  
   看工单如何落地存储

## 面试时可以怎么讲

建议这样讲这版项目：

1. 先说明它和手写版解决的是同一个业务问题
2. 再说明为什么要额外做一个 LangChain 版
3. 强调你比较过“手写控制力”与“框架开发效率”
4. 点出你处理过真实兼容问题，而不是只跑官方 happy path

## 后续可扩展方向

- 接入更正式的 memory/session 机制
- 引入 tracing / observability
- 增加评测脚本与对比实验
- 接入更完整的知识库管线
- 增加前端工单详情与操作工作台
