# Enterprise Agent RAG Projects

一个面向企业支持场景的 AI Agent 项目仓库，包含两套实现版本：

- **enterprise_agent_mvp**：手写 Agent Loop + 自定义 Provider 适配层
- **enterprise_agent_langchain**：基于 LangChain / Agent Runtime 的实现版本

两个版本围绕同一个业务题目展开，便于从工程和框架两个角度理解 AI 应用开发。

## 项目场景

该项目模拟一个企业内部支持 Agent，负责处理常见客户支持问题，核心能力包括：

- 知识库问答
- 多轮对话
- 工单创建、查询、升级
- OpenAI 兼容接口 / Anthropic 风格接口切换
- 本地前端控制台与 API 服务

适合用于展示以下方向的能力：

- AI 应用开发
- Agent / Tool Calling
- RAG 基础实现
- LLM 接口兼容层设计
- FastAPI 服务搭建

## 仓库亮点

### 1. 两套实现并行对照

仓库同时提供：

- **原生实现版**：更适合理解底层数据流和 Agent Loop
- **LangChain 版**：更适合理解框架式 Agent 开发

面试时可以直接对比说明：

- 不依赖框架时，消息、工具、Provider 是怎么组织的
- 使用 LangChain 后，模型接入、工具调用、运行时封装如何简化
- 两种方式在可控性、开发效率、可解释性上的差异

### 2. Provider 兼容设计

项目支持两类模型接入方式：

- OpenAI-compatible
- Anthropic-style

其中已经处理过兼容平台接入细节，例如：

- `base_url` 路径差异
- tool calling 结构差异
- 响应格式归一化

### 3. 从接口到前端的完整闭环

不是单纯的脚本 demo，而是完整的应用原型：

- FastAPI 后端
- 本地前端控制台
- 会话轨迹展示
- 手动建单
- 工单列表查看

## 技术栈

### `enterprise_agent_mvp`

- Python
- FastAPI
- SQLite
- 自定义 Agent Loop
- 自定义 OpenAI / Anthropic Provider
- 轻量检索器

### `enterprise_agent_langchain`

- Python
- FastAPI
- LangChain
- `ChatOpenAI`
- `ChatAnthropic`
- LangChain Tools
- `create_agent(...)`
- SQLite

## 目录结构

```text
enterprise_agent_mvp/         原生实现版本
enterprise_agent_langchain/   LangChain 版本
```

## 推荐阅读顺序

1. 先看本 README，了解项目目标和结构
2. 再看 `enterprise_agent_mvp/README.md`
3. 然后看 `enterprise_agent_langchain/README.md`
4. 最后对比两版的入口和运行时实现：
   - `enterprise_agent_mvp/app/main.py`
   - `enterprise_agent_mvp/app/agent/engine.py`
   - `enterprise_agent_langchain/app/main.py`
   - `enterprise_agent_langchain/app/langchain_runtime/agent_service.py`

## 快速运行

### 原始 MVP 版本

```bash
cd enterprise_agent_mvp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### LangChain 版本

```bash
cd enterprise_agent_langchain
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

