"""
Configuration for Phase 2: The Reliable Brain

This module provides type-safe configuration dataclasses for:
- LLM settings (Claude, Gemini)
- LangGraph settings (max iterations, checkpointing)
- Verification settings (level, timeout)
- Activity settings (timeout, heartbeat)

Configuration is loaded from environment variables with sensible defaults.

Usage:
    from agents.config import llm_config, langgraph_config
    
    model = llm_config.primary_model
    max_iter = langgraph_config.max_iterations
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class LLMConfig:
    """Configuration for LLM providers (Claude, Gemini)."""
    
    primary_provider: Literal["claude", "gemini"]
    """Primary LLM provider (default: claude)"""
    
    primary_model: str
    """Primary model identifier"""
    
    fallback_provider: Literal["claude", "gemini"]
    """Fallback LLM provider (default: gemini)"""
    
    fallback_model: str
    """Fallback model identifier"""
    
    max_tokens: int
    """Maximum tokens for code generation"""
    
    temperature: float
    """Temperature for generation (low = deterministic)"""
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load LLM config from environment variables."""
        return cls(
            primary_provider=os.getenv("LLM_PRIMARY_PROVIDER", "claude"),
            primary_model=os.getenv(
                "LLM_PRIMARY_MODEL", 
                "claude-sonnet-4-20250514"
            ),
            fallback_provider=os.getenv("LLM_FALLBACK_PROVIDER", "gemini"),
            fallback_model=os.getenv(
                "LLM_FALLBACK_MODEL", 
                "gemini-2.0-flash"
            ),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        )


@dataclass
class LangGraphConfig:
    """Configuration for LangGraph reasoning loops."""
    
    max_iterations: int
    """Maximum iterations before returning partial result"""
    
    enable_checkpointing: bool
    """Enable LangGraph checkpointing (future feature)"""
    
    @classmethod
    def from_env(cls) -> "LangGraphConfig":
        """Load LangGraph config from environment variables."""
        return cls(
            max_iterations=int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "3")),
            enable_checkpointing=os.getenv(
                "LANGGRAPH_ENABLE_CHECKPOINTING", "false"
            ).lower() == "true"
        )


@dataclass
class VerificationConfig:
    """Configuration for code verification."""
    
    level: Literal["syntax", "types", "full"]
    """Verification level (Phase 2.0: syntax only)"""
    
    timeout_ms: int
    """Timeout for verification in milliseconds"""
    
    @classmethod
    def from_env(cls) -> "VerificationConfig":
        """Load verification config from environment variables."""
        return cls(
            level=os.getenv("VERIFICATION_LEVEL", "syntax"),
            timeout_ms=int(os.getenv("VERIFICATION_TIMEOUT_MS", "5000"))
        )


@dataclass
class ActivityConfig:
    """Configuration for Temporal activities."""
    
    timeout_seconds: int
    """Start-to-close timeout for activities"""
    
    heartbeat_seconds: int
    """Heartbeat interval for long-running activities"""
    
    @classmethod
    def from_env(cls) -> "ActivityConfig":
        """Load activity config from environment variables."""
        return cls(
            timeout_seconds=int(os.getenv("ACTIVITY_TIMEOUT_SECONDS", "120")),
            heartbeat_seconds=int(os.getenv("ACTIVITY_HEARTBEAT_SECONDS", "30"))
        )


# ========== SINGLETON INSTANCES ==========
# These are loaded once at module import time

llm_config = LLMConfig.from_env()
langgraph_config = LangGraphConfig.from_env()
verification_config = VerificationConfig.from_env()
activity_config = ActivityConfig.from_env()


def print_config_summary():
    """Print configuration summary for debugging."""
    print("=" * 50)
    print("Phase 2 Configuration Summary")
    print("=" * 50)
    print(f"LLM Primary: {llm_config.primary_provider}/{llm_config.primary_model}")
    print(f"LLM Fallback: {llm_config.fallback_provider}/{llm_config.fallback_model}")
    print(f"LLM Max Tokens: {llm_config.max_tokens}")
    print(f"LLM Temperature: {llm_config.temperature}")
    print("-" * 50)
    print(f"LangGraph Max Iterations: {langgraph_config.max_iterations}")
    print(f"LangGraph Checkpointing: {langgraph_config.enable_checkpointing}")
    print("-" * 50)
    print(f"Verification Level: {verification_config.level}")
    print(f"Verification Timeout: {verification_config.timeout_ms}ms")
    print("-" * 50)
    print(f"Activity Timeout: {activity_config.timeout_seconds}s")
    print(f"Activity Heartbeat: {activity_config.heartbeat_seconds}s")
    print("=" * 50)


if __name__ == "__main__":
    print_config_summary()
