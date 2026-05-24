"""
ai_service.py
~~~~~~~~~~~~~
Unified interface for three AI providers:

  1. OpenRouter  (OpenAI-compatible streaming)
  2. Anthropic   (Claude)
  3. Google      (Gemini)

The chat_routes module calls get_ai_response(messages, model, provider)
and receives an iterator of plain text tokens.  This keeps the route
handler completely provider-agnostic.

Environment variables
---------------------
  OPENROUTER_API_KEY   - required for provider "openrouter"
  ANTHROPIC_API_KEY    - required for provider "anthropic"
  GOOGLE_API_KEY       - required for provider "google"
"""

from __future__ import annotations

import os
from typing import Iterable

# ---------------------------------------------------------------------------
# Provider imports (imported lazily so the package is optional if unused)
# ---------------------------------------------------------------------------
_openai_client = None
_anthropic_client = None
_google_client = None


def _get_openai_client():
    """Return a lazily-created OpenAI client pointed at OpenRouter."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            base_url="https://openrouter.ai/api/v1",
        )
    return _openai_client


def _get_anthropic_client():
    """Return a lazily-created Anthropic client."""
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", "")
        )
    return _anthropic_client


def _get_google_client():
    """Return a lazily-configured Google GenerativeAI client."""
    global _google_client
    if _google_client is None:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))
        _google_client = genai
    return _google_client


# ---------------------------------------------------------------------------
# Provider-specific stream functions
# ---------------------------------------------------------------------------

def _stream_openrouter(messages: list[dict], model: str) -> Iterable[str]:
    """Stream tokens from OpenRouter (OpenAI-compatible API)."""
    client = _get_openai_client()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2000,
        temperature=0.75,
        top_p=1.0,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        token = delta.content if (delta and delta.content) else None
        if token:
            yield token


def _stream_anthropic(messages: list[dict], model: str) -> Iterable[str]:
    """Stream tokens from Anthropic (Claude)."""
    import anthropic as _anthropic
    client = _get_anthropic_client()
    # Anthropic separates system message from content
    system_msg = None
    api_messages: list[dict] = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        elif m["role"] == "user":
            api_messages.append({"role": "user", "content": m["content"]})
        elif m["role"] == "assistant":
            api_messages.append({"role": "assistant", "content": m["content"]})

    with client.messages.stream(
        model=model,
        max_tokens=2000,
        temperature=0.75,
        messages=api_messages,
        system=system_msg,
    ) as stream:
        for text in stream.text_stream:
            yield text


def _stream_google(messages: list[dict], model: str) -> Iterable[str]:
    """Stream tokens from Google Gemini."""
    import google.generativeai as _genai
    client = _get_google_client()
    genai_model = client.GenerativeModel(model_name=model)

    # Gemini expects a single user prompt string (no multi-turn chat API
    # with streaming in the free tier).  We concatenate all user messages
    # and pass system instruction separately if present.
    system_parts: list[str] = []
    user_parts: list[str] = []

    for m in messages:
        if m["role"] == "system":
            system_parts.append(m["content"])
        elif m["role"] == "user":
            user_parts.append(m["content"])
        elif m["role"] == "assistant":
            # Pre-fill assistant response in user turn
            user_parts.append(f"Assistant response so far: {m['content']}")

    prompt = "\n\n".join(user_parts)
    config_parts: list[str] = []
    if system_parts:
        config_parts.append("System context:")
        config_parts.extend(system_parts)
        config_parts.append("")

    full_prompt = "\n".join(config_parts + [prompt]) if config_parts else prompt

    response = genai_model.generate_content(
        full_prompt,
        generation_config=client.types.GenerationConfig(
            temperature=0.75,
            max_output_tokens=8192,
        ),
        stream=True,
    )
    for chunk in response:
        text = chunk.text
        if text:
            yield text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

AVAILABLE_PROVIDERS = ("openrouter", "anthropic", "google")
DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "openai/gpt-4o-mini"

# Per-provider default model names
PROVIDER_DEFAULT_MODELS: dict[str, str] = {
    "openrouter": "openai/gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
    "google": "gemini-1.5-flash",
}


def get_ai_response(
    messages: list[dict],
    model: str | None = None,
    provider: str = DEFAULT_PROVIDER,
) -> Iterable[str]:
    """
    Unified entry point for streaming AI responses.

    Parameters
    ----------
    messages : list[dict]
        List of message dicts with keys ``"role"`` and ``"content"``.
        Roles are ``"system"``, ``"user"``, ``"assistant"``.
    model : str | None
        Provider-specific model identifier.  If ``None``, the default
        model for the chosen provider is used.
    provider : str
        One of ``"openrouter"``, ``"anthropic"``, ``"google"``.

    Returns
    -------
    Iterable[str]
        Yields text token strings.  Callers should join them or stream
        them to the client.

    Raises
    ------
    ValueError
        If an unknown provider is requested or the corresponding API key
        is not set.
    """
    if provider not in AVAILABLE_PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Choose from: {', '.join(AVAILABLE_PROVIDERS)}"
        )

    if model is None:
        model = PROVIDER_DEFAULT_MODELS[provider]

    # Basic validation that the API key is present
    key_env = {
        "openrouter": "OPENROUTER_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
    }[provider]
    if not os.getenv(key_env):
        raise ValueError(
            f"API key for {provider} ({key_env}) is not configured. "
            f"Add it to your .env file."
        )

    if provider == "openrouter":
        yield from _stream_openrouter(messages, model)
    elif provider == "anthropic":
        yield from _stream_anthropic(messages, model)
    elif provider == "google":
        yield from _stream_google(messages, model)
