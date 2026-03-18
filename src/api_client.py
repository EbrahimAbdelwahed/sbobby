"""
Client LLM OpenAI-compatible con DeepSeek (default) e Kimi K2 (fallback).
"""

import os
import json
import urllib.request
import urllib.error

PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "deepseek-reasoner": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-reasoner",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "kimi": {
        "base_url": "https://api.moonshot.ai/v1",
        "model": "kimi-latest",
        "env_key": "KIMI_API_KEY",
    },
}

DEFAULT_PROVIDER = "deepseek"
FALLBACK_PROVIDER = "kimi"


def _get_api_key(provider: str) -> str:
    env_key = PROVIDERS[provider]["env_key"]
    key = os.environ.get(env_key)
    if not key:
        raise ValueError(f"API key mancante: imposta la variabile d'ambiente {env_key}")
    return key


def chat(
    messages: list[dict],
    provider: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 8192,
) -> str:
    """Invia una richiesta chat e restituisce il contenuto della risposta.

    Se il provider fallisce, tenta automaticamente il fallback (Kimi).
    """
    provider = provider or DEFAULT_PROVIDER

    try:
        return _call(messages, provider, temperature, max_tokens)
    except Exception as e:
        if provider != FALLBACK_PROVIDER:
            print(f"[api_client] {provider} fallito ({e}), tento {FALLBACK_PROVIDER}...")
            return _call(messages, FALLBACK_PROVIDER, temperature, max_tokens)
        raise


def _call(
    messages: list[dict],
    provider: str,
    temperature: float,
    max_tokens: int,
) -> str:
    cfg = PROVIDERS[provider]
    api_key = _get_api_key(provider)
    url = f"{cfg['base_url']}/chat/completions"

    payload = json.dumps({
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    # Reasoner ha bisogno di più tempo per il chain-of-thought
    timeout = 600 if provider == "deepseek-reasoner" else 300

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"[{provider}] HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"[{provider}] Errore di connessione: {e.reason}") from e
    except TimeoutError as e:
        raise RuntimeError(f"[{provider}] Timeout ({timeout}s)") from e

    return data["choices"][0]["message"]["content"]
