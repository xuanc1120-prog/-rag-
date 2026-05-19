from __future__ import annotations

from app.config import Settings


def create_chat_model(settings: Settings):
    """按 provider 类型创建 LangChain 聊天模型。

    这里保留两条线：
    - ChatOpenAI: 适合 OpenAI 风格兼容接口
    - ChatAnthropic: 适合 Anthropic 风格兼容接口
    """
    if settings.provider_name == "anthropic":
        from langchain_anthropic import ChatAnthropic

        # 对 Anthropic 风格 SDK 来说，很多兼容服务会要求把 base_url 指到
        # 根前缀（例如 .../anthropic），SDK 自己再补 /v1/messages。
        # 因此这里主动兼容“已写到 /v1” 的配置，避免出现重复路径导致的 404。
        base_url = settings.base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]

        model_kwargs = {
            "model": settings.model,
            "api_key": settings.api_key,
            "temperature": 0,
            "max_tokens": 1000,
        }
        if base_url:
            model_kwargs["base_url"] = base_url
        return ChatAnthropic(**model_kwargs)

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0,
        max_tokens=1000,
    )
