import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate(system: str, messages: list[dict]) -> tuple[str, str]:
    """Call DeepSeek. Raises on failure.

    Returns:
        (response_text, provider_name)

    Raises:
        Exception: if DeepSeek fails.
    """
    text = _call_deepseek(system, messages)
    return text, "deepseek"


def generate_json(system: str, messages: list[dict]) -> tuple[str, str]:
    """Like generate(), but appends a JSON-only reminder to the system prompt."""
    json_system = system + "\n\n重要：只输出 JSON 对象本身，不要有任何前缀、后缀或 Markdown。"
    text = _call_deepseek(json_system, messages)
    return text, "deepseek"


def _call_claude(system: str, messages: list[dict]) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def _call_deepseek(system: str, messages: list[dict]) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )
    all_messages = [{"role": "system", "content": system}] + messages
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=all_messages,
        max_tokens=2048,
    )
    return response.choices[0].message.content
