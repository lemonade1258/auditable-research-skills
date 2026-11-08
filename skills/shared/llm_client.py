"""Minimal OpenAI-compatible chat client used by the semantic adapters.

Design constraints:

- Dependency-free: standard library only, so the repository keeps working in a
  plain Python install.
- Provider-agnostic: any OpenAI-compatible ``/chat/completions`` endpoint works
  (DashScope compatible mode, OpenAI, DeepSeek, Moonshot, vLLM, Ollama...).
- Deterministic when it can be: temperature defaults to 0 and the adapter
  records the model, the request digest and the raw response next to the parsed
  result so a run can be re-checked later.

The client never decides what is true. It produces a proposal that the calling
adapter stores with an explicit verification status.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-max"

# Ordered list of (env var, base url, model) candidates. The first environment
# variable that is present wins, so a user with only one provider configured
# does not have to edit any file.
PROVIDERS: tuple[tuple[str, str, str], ...] = (
    ("DASHSCOPE_API_KEY", DEFAULT_BASE_URL, DEFAULT_MODEL),
    ("OPENAI_API_KEY", "https://api.openai.com/v1", "gpt-4o-mini"),
    ("DEEPSEEK_API_KEY", "https://api.deepseek.com/v1", "deepseek-chat"),
    ("MOONSHOT_API_KEY", "https://api.moonshot.cn/v1", "moonshot-v1-8k"),
    ("ZHIPUAI_API_KEY", "https://open.bigmodel.cn/api/paas/v4", "glm-4-flash"),
    ("LOCAL_OPENAI_API_KEY", "http://127.0.0.1:8000/v1", "local-model"),
)


class LLMUnavailable(RuntimeError):
    """Raised when no provider credential is configured."""


@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    timeout: float = 120.0
    retries: int = 3
    temperature: float = 0.0
    max_tokens: int = 4096

    @property
    def endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"


@dataclass
class LLMResult:
    model: str
    content: str
    prompt_digest: str
    usage: dict[str, Any] = field(default_factory=dict)
    attempts: int = 1
    latency_ms: int = 0


def resolve_config(overrides: dict[str, Any] | None = None) -> LLMConfig:
    """Pick a provider from the environment, with optional overrides."""
    overrides = overrides or {}
    explicit_key = overrides.get("api_key") or os.environ.get("LLM_API_KEY")
    if explicit_key:
        base = (
            overrides.get("base_url")
            or os.environ.get("LLM_BASE_URL")
            or DEFAULT_BASE_URL
        )
        model = overrides.get("model") or os.environ.get("LLM_MODEL") or DEFAULT_MODEL
        return LLMConfig(api_key=explicit_key, base_url=base, model=model)

    for env_var, base, model in PROVIDERS:
        key = os.environ.get(env_var)
        if key:
            return LLMConfig(
                api_key=key,
                base_url=overrides.get("base_url") or base,
                model=overrides.get("model") or model,
            )
    raise LLMUnavailable(
        "No LLM credential found. Set one of: "
        + ", ".join(env_var for env_var, _, _ in PROVIDERS)
        + " (or LLM_API_KEY/LLM_BASE_URL/LLM_MODEL)."
    )


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def chat(
    messages: Sequence[dict[str, Any]],
    config: LLMConfig | None = None,
    *,
    system: str | None = None,
) -> LLMResult:
    """Send one chat request and return the assistant text."""
    cfg = config or resolve_config()
    payload_messages = list(messages)
    if system:
        payload_messages = [{"role": "system", "content": system}] + payload_messages

    body = {
        "model": cfg.model,
        "messages": payload_messages,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
    }
    raw = json.dumps(payload_messages, ensure_ascii=False)
    request = urllib.request.Request(
        cfg.endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    last_error: Exception | None = None
    started = time.time()
    for attempt in range(1, cfg.retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=cfg.timeout) as response:  # noqa: S310
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return LLMResult(
                model=cfg.model,
                content=content if isinstance(content, str) else json.dumps(content, ensure_ascii=False),
                prompt_digest=_digest(raw),
                usage=data.get("usage", {}) or {},
                attempts=attempt,
                latency_ms=int((time.time() - started) * 1000),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, ValueError) as exc:
            last_error = exc
            if attempt < cfg.retries:
                time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"LLM request failed after {cfg.retries} attempts: {last_error}")


_JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def parse_json(result: LLMResult) -> Any:
    """Extract the JSON payload from a model reply, tolerating code fences."""
    text = result.content.strip()
    block = _JSON_BLOCK.search(text)
    if block:
        text = block.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost JSON array or object in the text.
    for opener, closer in (("[", "]"), ("{", "}")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Model reply did not contain parseable JSON: {result.content[:300]}")


def chat_json(
    messages: Sequence[dict[str, Any]],
    config: LLMConfig | None = None,
    *,
    system: str | None = None,
) -> tuple[Any, LLMResult]:
    """Send a chat request that must come back as JSON."""
    result = chat(messages, config, system=system)
    return parse_json(result), result


def write_receipt(
    path: Path,
    payload: Any,
    result: LLMResult,
    *,
    purpose: str,
    extra: dict[str, Any] | None = None,
) -> None:
    """Persist the raw model reply next to the parsed payload for auditing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "purpose": purpose,
        "model": result.model,
        "prompt_digest": result.prompt_digest,
        "attempts": result.attempts,
        "latency_ms": result.latency_ms,
        "usage": result.usage,
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_response": result.content,
    }
    if extra:
        receipt.update(extra)
    path.write_text(
        json.dumps({"receipt": receipt, "payload": payload}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
