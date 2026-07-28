"""Runtime settings for agy-fleet-mcp."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGY_FLEET_MCP_",
        env_file=".env",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 10825
    gemini_home: Path = Path.home() / ".gemini"
    cursor_mcp_path: Path = Path.home() / ".cursor" / "mcp.json"
    gemini_mcp_path: Path = Path.home() / ".gemini" / "config" / "mcp_config.json"
    antigravity_cli_mcp_path: Path = Path.home() / ".gemini" / "antigravity-cli" / "mcp_config.json"
    antigravity_ide_mcp_path: Path = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
    fleet_registry_path: Path = Path("D:/Dev/repos/mcp-central-docs/operations/fleet-registry.json")
    default_source: str = "cursor"
    default_target: str = "gemini"
    max_enabled_servers: int = 50
    backup_on_write: bool = True


def load_settings() -> Settings:
    return Settings()
