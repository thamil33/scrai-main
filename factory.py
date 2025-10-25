import os
from typing import Any, Optional, cast

from dotenv import load_dotenv
from pydantic import SecretStr


def _to_float(env_value: Optional[str], default: float) -> float:
    try:
        return float(env_value) if env_value is not None else default
    except ValueError:
        return default


def get_chat_model_from_env(provider: Optional[str] = None) -> Any:
    """Return a LangChain ChatModel configured from environment variables.

    Supported providers (via LLM_PROVIDER):
    - lm_proxy (OpenAI-compatible)
    - lm_studio (OpenAI-compatible)
    - openrouter (OpenAI-compatible)
    - gemini (Google AI Studio)
    """

    # Load .env at import/use time
    load_dotenv(override=False)

    provider_str = cast(str, provider or os.getenv("LLM_PROVIDER", "lm_proxy"))
    provider = provider_str.strip().lower()

    # Common generation params
    temperature = _to_float(os.getenv("LLM_TEMPERATURE"), 0.7)
    max_tokens_env = os.getenv("LLM_MAX_TOKENS")
    max_tokens = int(max_tokens_env) if max_tokens_env and max_tokens_env.isdigit() else None

    if provider in {"lm_proxy", "lm_studio", "openrouter"}:
        try:
            from langchain_openai import ChatOpenAI
        except Exception as e:  # pragma: no cover - import error surfaced at runtime
            raise RuntimeError(
                "langchain-openai is required for OpenAI-compatible providers"
            ) from e

        if provider == "lm_proxy":
            base_url = os.getenv("LM_PROXY_BASE_URL", "http://localhost:4000/openai/v1")
            model = os.getenv("LM_PROXY_MODEL", "gpt-4o-mini")
            api_key = SecretStr(os.getenv("LM_PROXY_API_KEY", "not-needed"))
        elif provider == "lm_studio":
            base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
            model = os.getenv("LM_STUDIO_MODEL", "lmstudio-community/Phi-3-4k-mini")
            api_key = SecretStr(os.getenv("LM_STUDIO_API_KEY", "lm-studio"))
        else:  # openrouter
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
            api_key_env = os.getenv("OPENROUTER_API_KEY")
            if not api_key_env:
                raise RuntimeError("OPENROUTER_API_KEY is required for provider=openrouter")
            api_key = SecretStr(api_key_env)

        # Prepare kwargs with safe handling for optional args
        openai_kwargs: dict[str, Any] = {
            "model": model,
            "base_url": base_url,
            "api_key": api_key,
            "temperature": temperature,
            # Disable streaming due to structured output + tools compatibility issues
            # TODO: Re-enable when OpenAI/Azure add proper structured output + tools support
            "streaming": False,
        }
        if max_tokens is not None:
            # Some providers/lib versions use "max_tokens"; set if available
            openai_kwargs["max_tokens"] = max_tokens

        return ChatOpenAI(**openai_kwargs)

    if provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "langchain-google-genai is required for provider=gemini"
            ) from e

        api_key_env = os.getenv("GEMINI_API_KEY")
        if not api_key_env:
            raise RuntimeError("GEMINI_API_KEY is required for provider=gemini")
        api_key = SecretStr(api_key_env)
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

        # Prepare kwargs; some versions may not accept streaming param
        gemini_kwargs: dict[str, Any] = {
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        # Best-effort: enable streaming if the wrapper supports it
        try:
            gemini_kwargs["streaming"] = True  # type: ignore[assignment]
        except Exception:
            pass

        return ChatGoogleGenerativeAI(**gemini_kwargs)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def get_memory_chat_model_from_env(provider: Optional[str] = None) -> Any:
    """Return a LangChain ChatModel configured for memory processing.

    This function checks for memory-specific environment variables first:
    - MEMORY_PROVIDER: Specific provider for memory tasks
    - MEMORY_MODEL: Specific model for memory tasks

    Falls back to regular LLM_PROVIDER/LLM_MODEL if memory-specific vars not set.

    Supported providers (via MEMORY_PROVIDER or LLM_PROVIDER):
    - lm_proxy (OpenAI-compatible)
    - lm_studio (OpenAI-compatible)
    - openrouter (OpenAI-compatible)
    - gemini (Google AI Studio)
    """

    # Load .env at import/use time
    load_dotenv(override=False)

    # Check for memory-specific provider first
    memory_provider = os.getenv("MEMORY_PROVIDER")
    if memory_provider and not provider:
        provider = memory_provider.strip().lower()

    # Fall back to regular provider if no memory-specific or explicit provider
    if not provider:
        provider_str = os.getenv("LLM_PROVIDER", "lm_proxy")
        provider = provider_str.strip().lower()

    # Use explicit provider if passed as parameter
    if provider:
        provider = provider.strip().lower()

    # Common generation params
    temperature = _to_float(os.getenv("LLM_TEMPERATURE"), 0.7)
    max_tokens_env = os.getenv("LLM_MAX_TOKENS")
    max_tokens = int(max_tokens_env) if max_tokens_env and max_tokens_env.isdigit() else None

    if provider in {"lm_proxy", "lm_studio", "openrouter"}:
        try:
            from langchain_openai import ChatOpenAI
        except Exception as e:  # pragma: no cover - import error surfaced at runtime
            raise RuntimeError(
                "langchain-openai is required for OpenAI-compatible providers"
            ) from e

        if provider == "lm_proxy":
            base_url = os.getenv("LM_PROXY_BASE_URL", "http://localhost:4000/openai/v1")
            # Check for memory-specific model first, then fall back to regular model
            memory_model = os.getenv("MEMORY_MODEL")
            if memory_model and provider == os.getenv("MEMORY_PROVIDER", "").strip().lower():
                model = memory_model
            else:
                model = os.getenv("LM_PROXY_MODEL", "gpt-4o-mini")
            api_key = SecretStr(os.getenv("LM_PROXY_API_KEY", "not-needed"))
        elif provider == "lm_studio":
            base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
            # Check for memory-specific model first, then fall back to regular model
            memory_model = os.getenv("MEMORY_MODEL")
            if memory_model and provider == os.getenv("MEMORY_PROVIDER", "").strip().lower():
                model = memory_model
            else:
                model = os.getenv("LM_STUDIO_MODEL", "lmstudio-community/Phi-3-4k-mini")
            api_key = SecretStr(os.getenv("LM_STUDIO_API_KEY", "lm-studio"))
        else:  # openrouter
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            # Check for memory-specific model first, then fall back to regular model
            memory_model = os.getenv("MEMORY_MODEL")
            if memory_model and provider == os.getenv("MEMORY_PROVIDER", "").strip().lower():
                model = memory_model
            else:
                model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
            api_key_env = os.getenv("OPENROUTER_API_KEY")
            if not api_key_env:
                raise RuntimeError("OPENROUTER_API_KEY is required for provider=openrouter")
            api_key = SecretStr(api_key_env)

        # Prepare kwargs with safe handling for optional args
        openai_kwargs: dict[str, Any] = {
            "model": model,
            "base_url": base_url,
            "api_key": api_key,
            "temperature": temperature,
            # Disable streaming due to structured output + tools compatibility issues
            # TODO: Re-enable when OpenAI/Azure add proper structured output + tools support
            "streaming": False,
        }
        if max_tokens is not None:
            # Some providers/lib versions use "max_tokens"; set if available
            openai_kwargs["max_tokens"] = max_tokens

        return ChatOpenAI(**openai_kwargs)

    if provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "langchain-google-genai is required for provider=gemini"
            ) from e

        api_key_env = os.getenv("GEMINI_API_KEY")
        if not api_key_env:
            raise RuntimeError("GEMINI_API_KEY is required for provider=gemini")
        api_key = SecretStr(api_key_env)
        # Check for memory-specific model first, then fall back to regular model
        memory_model = os.getenv("MEMORY_MODEL")
        if memory_model and provider == os.getenv("MEMORY_PROVIDER", "").strip().lower():
            model = memory_model
        else:
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

        # Prepare kwargs; some versions may not accept streaming param
        gemini_kwargs: dict[str, Any] = {
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        # Best-effort: enable streaming if the wrapper supports it
        try:
            gemini_kwargs["streaming"] = True  # type: ignore[assignment]
        except Exception:
            pass

        return ChatGoogleGenerativeAI(**gemini_kwargs)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
