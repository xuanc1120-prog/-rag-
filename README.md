# Enterprise Agent RAG Projects

这个仓库包含两个围绕企业支持场景构建的 AI Agent 项目：

## 1. `enterprise_agent_mvp`

手写实现版本，重点在于理解：

- 自定义 provider 适配层
- 自定义 agent loop
- 轻量知识库检索
- 工单创建、查询、升级
- FastAPI 接口与简单前端控制台

## 2. `enterprise_agent_langchain`

LangChain 技术栈版本，重点在于理解：

- `ChatOpenAI` / `ChatAnthropic`
- LangChain tools
- `create_agent(...)`
- 与手写版本的差异化设计

## 目录说明

```text
enterprise_agent_mvp/         原始手写版本
enterprise_agent_langchain/   LangChain 版本
```

## 使用建议

如果你是为了学习，推荐顺序：

1. 先看 `enterprise_agent_mvp`
2. 再看 `enterprise_agent_langchain`
3. 最后对比两版在模型接入、工具调用、消息轨迹和工程组织上的差异

