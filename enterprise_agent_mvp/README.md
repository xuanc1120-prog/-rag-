# 企业知识库问答与工单协同 Agent MVP

这是一个面向 **AI 应用开发实习 / Agent 应用实习** 展示的项目。  
它模拟企业内部支持场景：用户先向 Agent 提问，Agent 优先检索知识库；如果问题无法直接解决，则通过工具调用创建或升级工单，把问答流程衔接到后续处理流程中。

## 项目价值

这个项目不是单纯的聊天机器人，而是一个带有业务闭环的 Agent 原型。它重点展示了下面这些更贴近真实岗位需求的能力：

- 大模型 API 接入
- Agent Loop 设计
- Tool Calling（工具调用）
- 轻量级 RAG
- 多模型提供方兼容层设计
- 面向业务流程的 AI 应用原型开发

## 这个项目解决什么问题

在企业支持场景里，常见问题通常会经历这几个阶段：

1. 用户发起问题
2. 系统优先查询已有知识库
3. 如果知识库无法解决，则需要升级处理
4. 将未解决问题转成结构化工单

这个项目把这条链路做成了一个可运行的 MVP，用来验证：

- Agent 是否能先检索再回答
- Agent 是否能在合适的时机调用工具
- 系统是否能从“回答问题”过渡到“处理问题”

## 核心功能

- 企业知识库问答
- 多轮对话支持（由客户端显式传入历史消息）
- 创建工单、查询工单、升级工单
- `OpenAI-compatible` / `Anthropic` 两种 provider 切换
- 本地前端控制台 + FastAPI API

## 技术栈

- Python
- FastAPI
- SQLite
- 自定义 Agent Loop
- 自定义 Provider 适配层
- 轻量级检索器（非向量库版 RAG）

## 设计亮点

### 1. Provider 兼容层

项目定义了一套统一的 `LLMProvider` 接口，并分别实现：

- `OpenAICompatibleProvider`
- `AnthropicProvider`

这样做的好处是：  
Agent 主流程不需要关心不同模型接口在消息结构、工具调用格式上的差异，后续切换模型提供方时改动更小，也更适合在面试里讲清楚“为什么要做抽象层”。

### 2. 轻量级 RAG

这个项目没有一上来就接向量数据库，而是先做了一个轻量、可解释、可测试的检索器。

这样做的原因是：

- 更适合 MVP 快速验证
- 更方便阅读和讲解
- 更容易写单元测试

如果后续继续扩展，可以自然升级到：

- embedding 检索
- 向量数据库
- 更正式的 RAG 评测流程

### 3. 工单协同

项目不仅能回答问题，还能把未解决的问题转成工单，当前支持的核心流程包括：

- 创建工单
- 查询工单
- 升级工单

这让项目从“问答 demo”变成了“带业务动作的 AI 应用原型”。

### 4. 错误处理

针对模型调用失败、网络错误、返回结构异常等问题，provider 层做了统一错误包装，API 层返回明确的错误状态，避免把所有问题都变成难以定位的裸 `500`。

## 项目结构

```text
enterprise_agent_mvp/
  app/
    agent/        # Agent loop 与工具调度
    db/           # SQLite 工单持久化
    providers/    # OpenAI-compatible / Anthropic 适配层
    rag/          # 轻量级知识检索
    tools/        # 工单工具与业务动作
    static/       # 本地前端控制台
    config.py     # 配置加载
    main.py       # FastAPI 入口
    models.py     # 统一数据结构
  data/
    knowledge_base.txt
  tests/
  .env.example
  requirements.txt
```

## 如何运行

### 1. 创建环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 2. 配置 `.env`

根据你要使用的模型提供方，选择其中一组：

```env
LLM_PROVIDER=openai_compatible
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

或：

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

程序启动时会自动读取本地 `.env` 文件。

### 3. 运行测试

```bash
python -m unittest discover -s tests -v
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- 前端控制台：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## 推荐阅读顺序

如果你是面试官，或者准备快速理解项目，建议按下面顺序看：

1. `app/main.py`  
   看整个请求是怎么进入系统的
2. `app/providers/`  
   看模型提供方兼容层怎么设计
3. `app/agent/engine.py`  
   看 Agent Loop 的核心逻辑
4. `app/tools/ticket_tools.py`  
   看工具调用最终如何落到业务动作
5. `app/rag/retriever.py`  
   看知识检索的实现方式
6. `app/db/ticket_repository.py`  
   看工单如何持久化

## 面试时可以怎么讲

建议重点讲这几件事：

1. 为什么需要 provider 抽象层
2. 为什么 Agent 要先检索再回答
3. 为什么这个项目不只是聊天，而是“问答 + 工单协同”
4. 为什么 MVP 阶段先做轻量级 RAG
5. 如果继续扩展，下一步会优先补什么

## 后续可扩展方向

- 引入 embedding + 向量数据库
- 增加 session 级会话管理
- 增加工单状态流转与权限控制
- 增加日志、评测与 tracing
- 增加更完整的前端工作台
