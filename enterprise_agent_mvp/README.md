# 企业知识库问答与工单协同 Agent MVP

这是一个适合用于**实习简历、面试展示和本地演示**的 AI 应用项目。  
它模拟了一个企业内部支持 Agent，能够：

- 结合知识库进行问题回答
- 在回答过程中调用工具
- 创建、查询和升级工单
- 在 `OpenAI 兼容接口` 与 `Anthropic 接口` 之间切换
- 通过简单的 FastAPI 接口本地演示

## 这个项目为什么有价值

这个 MVP 重点展示了很多 AI 应用开发实习岗位真正看重的能力：

- 大模型 API 接入
- Agent Loop 设计
- Tool Calling（工具调用）
- 轻量级 RAG
- Provider 兼容层设计
- 面向业务流程的 AI 应用原型开发

## 项目结构

```text
enterprise_agent_mvp/
  app/
    agent/        # Agent 循环与工具执行
    db/           # SQLite 工单持久化
    providers/    # OpenAI兼容接口与Anthropic适配层
    rag/          # 轻量级检索器
    tools/        # 知识库与工单工具
    config.py     # 环境变量与配置加载
    main.py       # FastAPI 应用入口
  data/
    knowledge_base.txt
  tests/
  .env.example
  requirements.txt
```

## 环境准备

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

根据你要使用的模型提供方，修改 `.env`：

- `LLM_PROVIDER=openai_compatible`
- 或 `LLM_PROVIDER=anthropic`

程序启动时会自动读取本地 `.env` 文件。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 启动 API 服务

```bash
uvicorn app.main:app --reload
```

## 接口示例

### 健康检查

```bash
curl http://127.0.0.1:8000/health
```

### 单轮聊天

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"我现在登不上账号，该怎么办？\"}"
```

### 多轮聊天

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"那你帮我升级这个问题\",\"history\":[{\"role\":\"user\",\"content\":\"我现在登不上账号。\"},{\"role\":\"assistant\",\"content\":\"请先完成身份校验并尝试密码重置链接。\"}]}"
```

### 手动创建工单

```bash
curl -X POST http://127.0.0.1:8000/tickets ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"登录受阻\",\"issue\":\"用户在重置后仍无法登录\",\"priority\":\"high\",\"customer_email\":\"vip@example.com\"}"
```

## 设计说明

### 1. Provider 兼容层

后端定义了一套统一的 `LLMProvider` 接口，并实现了两个适配器：

- `OpenAICompatibleProvider`
- `AnthropicProvider`

这样做的好处是：  
Agent 主流程不需要关心不同模型接口的消息格式和工具调用差异，代码更清晰，也更适合在面试中讲解。

### 2. 检索策略

当前版本的检索器是**轻量级、可测试、可解释**的。  
它采用基于词项重叠的简单打分方式，而不是 embedding + 向量库。

这样做的原因：

- 项目更容易跑通
- 代码更容易理解
- 单元测试更稳定

如果以后要增强，可以把这一层替换成：

- embedding 检索
- 向量数据库
- 更正式的 RAG 评测流程

### 3. 工单工作流

当前工单状态流比较小，但足够展示业务协同：

- `open`
- `escalated`
- `closed`（后续预留）

这样项目就不只是“问答”，而是能把未解决的问题转化为结构化任务。

### 4. 错误处理

模型调用失败时，provider 层会把异常统一包装成应用级错误，API 层会将其返回为 `502`，方便定位：

- API key 配置错误
- Base URL 错误
- 网络超时
- 返回 JSON 非法
- Provider 返回结构不符合预期

## 面试时建议怎么讲

建议重点强调这几点：

1. 为什么需要 provider 抽象层
2. 为什么 Agent 应该先检索再回答
3. 工具调用如何把问答变成业务流程
4. 为什么这个项目适合作为 AI 应用开发 MVP
5. 如果继续扩展，你会优先补什么（评测、embedding、鉴权、日志等）
