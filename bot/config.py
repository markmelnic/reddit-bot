"""Configuration management — supports YAML files, CLI args, and env vars."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class ProxyConfig:
    enabled: bool = False
    proxy_list_path: Optional[str] = None
    rotate_per_account: bool = True


@dataclass
class RateLimitConfig:
    min_action_delay: float = 2.0
    max_action_delay: float = 8.0
    min_account_delay: float = 5.0
    max_account_delay: float = 15.0
    daily_action_quota: int = 0  # 0 = unlimited


@dataclass
class WebhookConfig:
    enabled: bool = False
    url: Optional[str] = None
    on_completion: bool = True
    on_failure: bool = True


@dataclass
class BotConfig:
    # Input files
    accounts_path: Optional[str] = None
    links_path: Optional[str] = None

    # Modes
    verbose: bool = False
    headless: bool = False
    dry_run: bool = False

    # Anti-detection
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    rotate_user_agent: bool = False
    randomize_actions: bool = False
    human_mouse: bool = False
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    # Orchestration
    parallel_accounts: int = 1
    schedule_cron: Optional[str] = None
    session_persistence: bool = False
    session_dir: str = "sessions"

    # Reporting
    webhook: WebhookConfig = field(default_factory=WebhookConfig)

    # Database
    db_path: str = "reddit_bot.db"

    # Credentials
    encrypt_credentials: bool = False
    credentials_key_env: str = "REDDIT_BOT_KEY"

    # Screenshots
    screenshot_on_failure: bool = False
    screenshot_dir: str = "screenshots"

    @classmethod
    def from_yaml(cls, path: str) -> "BotConfig":
        """Load config from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return cls._from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotConfig":
        """Load config from a dictionary."""
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "BotConfig":
        config = cls()
        simple_fields = {
            "accounts_path", "links_path", "verbose", "headless", "dry_run",
            "rotate_user_agent", "randomize_actions", "human_mouse",
            "parallel_accounts", "schedule_cron", "session_persistence",
            "session_dir", "db_path", "encrypt_credentials",
            "credentials_key_env", "screenshot_on_failure", "screenshot_dir",
        }
        for key in simple_fields:
            if key in data:
                setattr(config, key, data[key])

        if "proxy" in data and isinstance(data["proxy"], dict):
            config.proxy = ProxyConfig(**data["proxy"])

        if "rate_limit" in data and isinstance(data["rate_limit"], dict):
            config.rate_limit = RateLimitConfig(**data["rate_limit"])

        if "webhook" in data and isinstance(data["webhook"], dict):
            config.webhook = WebhookConfig(**data["webhook"])

        return config

    def merge_cli_args(self, args: dict[str, Any]) -> None:
        """Override config values with CLI arguments (non-None values win)."""
        mapping = {
            "accounts": "accounts_path",
            "links": "links_path",
            "verbose": "verbose",
            "headless": "headless",
            "dry_run": "dry_run",
            "proxy_list": "proxy.proxy_list_path",
            "rotate_user_agent": "rotate_user_agent",
            "randomize_actions": "randomize_actions",
            "human_mouse": "human_mouse",
            "parallel": "parallel_accounts",
            "schedule": "schedule_cron",
            "session_persistence": "session_persistence",
            "screenshot_on_failure": "screenshot_on_failure",
            "encrypt_credentials": "encrypt_credentials",
            "webhook_url": "webhook.url",
        }
        for arg_key, config_key in mapping.items():
            value = args.get(arg_key)
            if value is None:
                continue
            if "." in config_key:
                obj_name, attr_name = config_key.split(".")
                obj = getattr(self, obj_name)
                setattr(obj, attr_name, value)
                if obj_name == "proxy" and attr_name == "proxy_list_path":
                    self.proxy.enabled = True
                if obj_name == "webhook" and attr_name == "url":
                    self.webhook.enabled = True
            else:
                setattr(self, config_key, value)

    def merge_env_vars(self) -> None:
        """Read configuration from environment variables."""
        env_map = {
            "REDDIT_BOT_ACCOUNTS": "accounts_path",
            "REDDIT_BOT_LINKS": "links_path",
            "REDDIT_BOT_HEADLESS": "headless",
            "REDDIT_BOT_DRY_RUN": "dry_run",
            "REDDIT_BOT_DB_PATH": "db_path",
            "REDDIT_BOT_WEBHOOK_URL": "webhook.url",
        }
        for env_key, config_key in env_map.items():
            value = os.environ.get(env_key)
            if value is None:
                continue
            if "." in config_key:
                obj_name, attr_name = config_key.split(".")
                obj = getattr(self, obj_name)
                setattr(obj, attr_name, value)
                if obj_name == "webhook":
                    self.webhook.enabled = True
            else:
                attr = getattr(self, config_key)
                if isinstance(attr, bool):
                    setattr(self, config_key, value.lower() in ("1", "true", "yes"))
                else:
                    setattr(self, config_key, value)
