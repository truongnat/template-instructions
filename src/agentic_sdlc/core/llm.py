"""LLM Provider - Unified interface for multiple LLM backends.

Supports:
- **OpenAI** (GPT-4o, GPT-4o-mini, etc.)
- **Anthropic** (Claude 3.5/4 Sonnet, Haiku, Opus)
- **Google Gemini** (Gemini 2.0 Flash, Pro, etc.)
- **Ollama** (Free local models: Llama 3, Mistral, Phi, Qwen, etc.)
- **Custom** (Any OpenAI-compatible API endpoint)

All providers are **optional** — the framework gracefully degrades if a
provider's SDK is not installed. Providers are lazy-loaded to avoid
importing heavy dependencies at startup.

Usage:
    from agentic_sdlc.core.llm import LLMProvider, get_provider, LLMRouter

    # Single provider
    llm = get_provider("gemini")
    response = llm.complete("Explain REST APIs in 3 sentences")

    # Auto-routing across available providers
    router = LLMRouter()
    response = router.complete("Explain REST APIs")
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .logging import get_logger

logger = get_logger(__name__)


class LLMProviderType(Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class LLMMessage:
    """A message in a chat conversation.

    Attributes:
        role: Message role (system, user, assistant).
        content: Message text content.
    """
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider.

    Attributes:
        content: Response text.
        model: Model that generated the response.
        provider: Provider type.
        usage: Token usage stats (prompt_tokens, completion_tokens, total_tokens).
        metadata: Additional response metadata.
        finish_reason: Why the model stopped generating.
    """
    content: str
    model: str = ""
    provider: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider.

    Attributes:
        provider: Provider type.
        model: Model name/ID.
        api_key: API key (falls back to env var if not set).
        base_url: Base URL override (for custom endpoints or Ollama).
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        max_tokens: Maximum response tokens.
        timeout: Request timeout in seconds.
        extra: Additional provider-specific config.
    """
    provider: LLMProviderType = LLMProviderType.GEMINI
    model: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def effective_model(self) -> str:
        """Get model, falling back to provider default."""
        if self.model:
            return self.model
        defaults = {
            LLMProviderType.OPENAI: "gpt-4o-mini",
            LLMProviderType.ANTHROPIC: "claude-sonnet-4-20250514",
            LLMProviderType.GEMINI: "gemini-2.0-flash",
            LLMProviderType.OLLAMA: "llama3.2",
            LLMProviderType.CUSTOM: "gpt-4o-mini",
        }
        return defaults.get(self.provider, "gpt-4o-mini")


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    All providers implement `complete()` for single-turn and `chat()` for
    multi-turn conversations. Both are synchronous by default.
    """

    def __init__(self, config: LLMConfig):
        """Initialize the provider.

        Args:
            config: Provider configuration.
        """
        self.config = config
        self._client: Any = None

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a completion for a single prompt.

        Args:
            prompt: Input prompt text.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with generated text.
        """

    @abstractmethod
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate a response in a multi-turn conversation.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional arguments.

        Returns:
            LLMResponse with generated text.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider SDK is installed and configured.

        Returns:
            True if the provider can be used.
        """

    @property
    def provider_type(self) -> LLMProviderType:
        """Get the provider type."""
        return self.config.provider

    @property
    def model_name(self) -> str:
        """Get the active model name."""
        return self.config.effective_model


# =============================================================================
# OpenAI Provider
# =============================================================================


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4o, GPT-4o-mini, o1, etc.)."""

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config or LLMConfig(provider=LLMProviderType.OPENAI))

    def _ensure_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                kwargs: Dict[str, Any] = {}
                if self.config.api_key:
                    kwargs["api_key"] = self.config.api_key
                if self.config.base_url:
                    kwargs["base_url"] = self.config.base_url
                kwargs["timeout"] = self.config.timeout
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "openai package required. Install: pip install openai"
                )

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        return self.chat([LLMMessage(role="user", content=prompt)], **kwargs)

    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        self._ensure_client()
        response = self._client.chat.completions.create(
            model=self.config.effective_model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            **{k: v for k, v in kwargs.items() if k not in ("temperature", "max_tokens")},
        )
        choice = response.choices[0]
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            provider="openai",
            usage=usage,
            finish_reason=choice.finish_reason or "stop",
        )

    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401
            return True
        except ImportError:
            return False


# =============================================================================
# Anthropic Provider
# =============================================================================


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (Claude 3.5/4 Sonnet, Haiku, Opus)."""

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config or LLMConfig(provider=LLMProviderType.ANTHROPIC))

    def _ensure_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
                kwargs: Dict[str, Any] = {}
                if self.config.api_key:
                    kwargs["api_key"] = self.config.api_key
                kwargs["timeout"] = self.config.timeout
                self._client = Anthropic(**kwargs)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install: pip install anthropic"
                )

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        return self.chat([LLMMessage(role="user", content=prompt)], **kwargs)

    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        self._ensure_client()

        # Anthropic requires system message to be separate
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_msg += m.content + "\n"
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        create_kwargs: Dict[str, Any] = {
            "model": self.config.effective_model,
            "messages": chat_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        if system_msg.strip():
            create_kwargs["system"] = system_msg.strip()

        response = self._client.messages.create(**create_kwargs)
        content = ""
        if response.content:
            content = response.content[0].text if hasattr(response.content[0], "text") else str(response.content[0])

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
        return LLMResponse(
            content=content,
            model=response.model,
            provider="anthropic",
            usage=usage,
            finish_reason=response.stop_reason or "stop",
        )

    def is_available(self) -> bool:
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False


# =============================================================================
# Google Gemini Provider
# =============================================================================


class GeminiProvider(LLMProvider):
    """Google Gemini API provider (Gemini 2.0 Flash, Pro, etc.)."""

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config or LLMConfig(provider=LLMProviderType.GEMINI))

    def _ensure_client(self):
        if self._client is None:
            try:
                from google import genai
                kwargs: Dict[str, Any] = {}
                if self.config.api_key:
                    kwargs["api_key"] = self.config.api_key
                self._client = genai.Client(**kwargs)
            except ImportError:
                raise ImportError(
                    "google-genai package required. Install: pip install google-genai"
                )

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        return self.chat([LLMMessage(role="user", content=prompt)], **kwargs)

    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        self._ensure_client()
        from google.genai import types

        # Build contents for Gemini
        contents = []
        system_instruction = None
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m.content)],
                ))

        config = types.GenerateContentConfig(
            temperature=kwargs.get("temperature", self.config.temperature),
            max_output_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = self._client.models.generate_content(
            model=self.config.effective_model,
            contents=contents,
            config=config,
        )

        content = response.text or ""
        usage = {}
        if response.usage_metadata:
            usage = {
                "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
                "total_tokens": getattr(response.usage_metadata, "total_token_count", 0),
            }
        return LLMResponse(
            content=content,
            model=self.config.effective_model,
            provider="gemini",
            usage=usage,
            finish_reason="stop",
        )

    def is_available(self) -> bool:
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False


# =============================================================================
# Ollama Provider (Free local models)
# =============================================================================


class OllamaProvider(LLMProvider):
    """Ollama provider for free local models (Llama 3, Mistral, Phi, Qwen, etc.).

    Ollama uses an OpenAI-compatible API, so we leverage the OpenAI SDK
    pointed at localhost:11434.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig(
                provider=LLMProviderType.OLLAMA,
                base_url="http://localhost:11434/v1",
                model="llama3.2",
            )
        if not config.base_url:
            config.base_url = "http://localhost:11434/v1"
        super().__init__(config)

    def _ensure_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    base_url=self.config.base_url,
                    api_key="ollama",  # Ollama doesn't need a real key
                    timeout=self.config.timeout,
                )
            except ImportError:
                raise ImportError(
                    "openai package required for Ollama (OpenAI-compatible). "
                    "Install: pip install openai"
                )

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        return self.chat([LLMMessage(role="user", content=prompt)], **kwargs)

    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        self._ensure_client()
        try:
            response = self._client.chat.completions.create(
                model=self.config.effective_model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )
            choice = response.choices[0]
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens or 0,
                    "completion_tokens": response.usage.completion_tokens or 0,
                    "total_tokens": response.usage.total_tokens or 0,
                }
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model or self.config.effective_model,
                provider="ollama",
                usage=usage,
                finish_reason=choice.finish_reason or "stop",
            )
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return LLMResponse(
                content=f"[Ollama error: {e}. Is Ollama running on {self.config.base_url}?]",
                model=self.config.effective_model,
                provider="ollama",
                finish_reason="error",
            )

    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401
            # Also check if Ollama is running
            import urllib.request
            url = (self.config.base_url or "http://localhost:11434/v1").replace("/v1", "")
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            return False


# =============================================================================
# LLM Router — Auto-select best available provider
# =============================================================================


class LLMRouter:
    """Routes LLM requests to the best available provider.

    Tries providers in priority order based on availability and
    configuration. Falls back gracefully if preferred provider is
    unavailable.

    Priority order (configurable):
    1. Gemini (free tier available)
    2. OpenAI
    3. Anthropic
    4. Ollama (free local)

    Example:
        >>> router = LLMRouter()
        >>> response = router.complete("Explain REST APIs")
        >>> print(f"Answered by: {response.provider} ({response.model})")
    """

    # Default priority: Gemini first (free), then OpenAI/Anthropic, then Ollama
    DEFAULT_PRIORITY = [
        LLMProviderType.GEMINI,
        LLMProviderType.OPENAI,
        LLMProviderType.ANTHROPIC,
        LLMProviderType.OLLAMA,
    ]

    def __init__(
        self,
        providers: Optional[Dict[LLMProviderType, LLMConfig]] = None,
        priority: Optional[List[LLMProviderType]] = None,
        preferred: Optional[LLMProviderType] = None,
    ):
        """Initialize the router.

        Args:
            providers: Optional dict of provider configs.
            priority: Provider priority order.
            preferred: Preferred provider (tried first).
        """
        self._configs = providers or {}
        self._priority = priority or self.DEFAULT_PRIORITY
        self._preferred = preferred
        self._providers: Dict[LLMProviderType, LLMProvider] = {}
        self._active_provider: Optional[LLMProvider] = None

    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a completion using the best available provider.

        Args:
            prompt: Input prompt.
            **kwargs: Additional arguments.

        Returns:
            LLMResponse from the first available provider.
        """
        provider = self._get_provider(**kwargs)
        if not provider:
            return LLMResponse(
                content="[No LLM provider available. Install one of: "
                        "google-genai, openai, anthropic, or start Ollama]",
                provider="none",
                finish_reason="error",
            )
        return provider.complete(prompt, **kwargs)

    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate a chat response using the best available provider.

        Args:
            messages: Conversation messages.
            **kwargs: Additional arguments.

        Returns:
            LLMResponse from the first available provider.
        """
        provider = self._get_provider(**kwargs)
        if not provider:
            return LLMResponse(
                content="[No LLM provider available]",
                provider="none",
                finish_reason="error",
            )
        return provider.chat(messages, **kwargs)

    def get_available_providers(self) -> List[LLMProviderType]:
        """Get list of available (installed + configured) providers.

        Returns:
            List of available provider types.
        """
        available = []
        for ptype in self._priority:
            provider = self._create_provider(ptype)
            if provider and provider.is_available():
                available.append(ptype)
        return available

    def use_provider(self, provider_type: LLMProviderType) -> Optional[LLMProvider]:
        """Force use of a specific provider.

        Args:
            provider_type: Provider to use.

        Returns:
            The provider instance, or None if unavailable.
        """
        provider = self._create_provider(provider_type)
        if provider and provider.is_available():
            self._active_provider = provider
            return provider
        return None

    def _get_provider(self, **kwargs) -> Optional[LLMProvider]:
        """Get the best available provider.

        Args:
            **kwargs: May contain 'provider' to force selection.

        Returns:
            LLMProvider instance or None.
        """
        # Check for explicit provider request
        requested = kwargs.pop("provider", None)
        if requested:
            if isinstance(requested, str):
                requested = LLMProviderType(requested)
            provider = self._create_provider(requested)
            if provider and provider.is_available():
                return provider

        # Use cached active provider
        if self._active_provider:
            return self._active_provider

        # Try preferred first
        if self._preferred:
            provider = self._create_provider(self._preferred)
            if provider and provider.is_available():
                self._active_provider = provider
                logger.info(f"Using preferred LLM: {self._preferred.value}")
                return provider

        # Try in priority order
        for ptype in self._priority:
            provider = self._create_provider(ptype)
            if provider and provider.is_available():
                self._active_provider = provider
                logger.info(f"Auto-selected LLM: {ptype.value}")
                return provider

        logger.warning("No LLM provider available")
        return None

    def _create_provider(self, ptype: LLMProviderType) -> Optional[LLMProvider]:
        """Create or retrieve a cached provider instance."""
        if ptype in self._providers:
            return self._providers[ptype]

        config = self._configs.get(ptype, LLMConfig(provider=ptype))
        factories = {
            LLMProviderType.OPENAI: OpenAIProvider,
            LLMProviderType.ANTHROPIC: AnthropicProvider,
            LLMProviderType.GEMINI: GeminiProvider,
            LLMProviderType.OLLAMA: OllamaProvider,
        }
        factory = factories.get(ptype)
        if not factory:
            return None

        try:
            provider = factory(config)
            self._providers[ptype] = provider
            return provider
        except Exception as e:
            logger.debug(f"Failed to create {ptype.value} provider: {e}")
            return None


# =============================================================================
# Factory functions
# =============================================================================


def get_provider(
    provider: str = "gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> LLMProvider:
    """Factory function to create an LLM provider.

    Args:
        provider: Provider name ('gemini', 'openai', 'anthropic', 'ollama').
        model: Optional model override.
        api_key: Optional API key.
        base_url: Optional base URL override.
        **kwargs: Additional config.

    Returns:
        Configured LLMProvider instance.
    """
    ptype = LLMProviderType(provider.lower())
    config = LLMConfig(
        provider=ptype,
        model=model or "",
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )

    factories = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
        LLMProviderType.GEMINI: GeminiProvider,
        LLMProviderType.OLLAMA: OllamaProvider,
    }
    factory = factories.get(ptype, GeminiProvider)
    return factory(config)


def get_router(
    preferred: Optional[str] = None,
    configs: Optional[Dict[str, Dict[str, Any]]] = None,
) -> LLMRouter:
    """Factory function to create an LLM router.

    Args:
        preferred: Preferred provider name.
        configs: Dict of provider configs keyed by provider name.

    Returns:
        Configured LLMRouter.
    """
    provider_configs = {}
    if configs:
        for name, cfg in configs.items():
            ptype = LLMProviderType(name.lower())
            provider_configs[ptype] = LLMConfig(provider=ptype, **cfg)

    pref = LLMProviderType(preferred.lower()) if preferred else None
    return LLMRouter(providers=provider_configs, preferred=pref)
