import json
from pathlib import Path

from agy_fleet_mcp.config import Settings
from agy_fleet_mcp.startup_probe import pipeline_liveness


def test_pipeline_liveness_ready(tmp_path: Path):
    source = tmp_path / "mcp.json"
    source.write_text(json.dumps({"mcpServers": {"one": {"command": "uv", "args": ["run", "one"]}}}), encoding="utf-8")
    target = tmp_path / "mcp_config.json"
    target.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")

    settings = Settings(
        cursor_mcp_path=source,
        gemini_mcp_path=target,
        fleet_registry_path=tmp_path / "registry.json",
    )
    (tmp_path / "registry.json").write_text("{}", encoding="utf-8")

    result = pipeline_liveness(settings)
    assert result["service"] == "agy-fleet-mcp"
    assert result["version"] == "0.2.0"
    assert result["checks"]["cursor_config"] is True
    assert result["checks"]["gemini_config"] is True
    assert result["checks"]["registry"] is True
    assert result["checks"]["budget"]["checked"] is True
    # Missing agy binary is a soft degradation, not a crash.
    assert result["status"] in ("ready", "degraded")


def test_pipeline_liveness_missing_configs(tmp_path: Path):
    settings = Settings(
        cursor_mcp_path=tmp_path / "nope.json",
        gemini_mcp_path=tmp_path / "nope_config.json",
        fleet_registry_path=tmp_path / "nope_registry.json",
    )
    result = pipeline_liveness(settings)
    assert result["checks"]["cursor_config"] is False
    assert result["checks"]["gemini_config"] is False
    assert result["checks"]["budget"]["checked"] is False
    assert "cursor config missing" in result["issues"]
