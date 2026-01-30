"""
Temporal Configuration Management
Loads environment-specific settings from .env file
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class TemporalConfig:
    """Temporal Server connection configuration"""
    
    host: str
    namespace: str
    task_queue: str
    
    @classmethod
    def from_env(cls) -> "TemporalConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("TEMPORAL_HOST", "localhost:7233"),
            namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
            task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "default"),
        )


@dataclass
class AppConfig:
    """Application configuration"""
    
    env: str
    log_level: str
    workflow_timeout_seconds: int
    chaos_test_sleep_seconds: int
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load application configuration from environment"""
        return cls(
            env=os.getenv("ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            workflow_timeout_seconds=int(
                os.getenv("DEFAULT_WORKFLOW_TIMEOUT_SECONDS", "86400")
            ),
            chaos_test_sleep_seconds=int(
                os.getenv("CHAOS_TEST_SLEEP_SECONDS", "5")
            ),
        )


# Global config instances
temporal_config = TemporalConfig.from_env()
app_config = AppConfig.from_env()
