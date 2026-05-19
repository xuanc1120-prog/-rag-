from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv_file(path: Path) -> None:
    """从本地 .env 文件读取配置，并只在环境变量缺失时补进去。"""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(slots=True)
class Settings:
    """项目运行期配置。"""
    provider_name: str
    model: str
    api_key: str
    base_url: str
    db_path: Path
    knowledge_base_path: Path
    system_prompt: str
    max_turns: int = 4

    @classmethod
    def from_env(cls, root_dir: Path) -> "Settings":
        """根据根目录下的 .env 和当前环境变量生成 Settings。"""
        # 先尝试读取项目目录下的 .env，方便本地开发直接启动。
        load_dotenv_file(root_dir / ".env")
        provider_name = os.getenv("LLM_PROVIDER", "openai_compatible")
        # 根据 provider 类型选择对应的一组配置字段。
        if provider_name == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        return cls(
            provider_name=provider_name,
            model=model,
            api_key=api_key,
            base_url=base_url,
            db_path=Path(os.getenv("TICKET_DB_PATH", root_dir / "data" / "tickets.db")),
            knowledge_base_path=Path(os.getenv("KNOWLEDGE_BASE_PATH", root_dir / "data" / "knowledge_base.txt")),
            system_prompt=os.getenv(
                "SYSTEM_PROMPT",
                (
                    "You are an enterprise support agent. Always search the knowledge base before answering "
                    "support questions. If the issue is unresolved, create or escalate a ticket."
                ),
            ),
            max_turns=int(os.getenv("MAX_AGENT_TURNS", "4")),
        )
