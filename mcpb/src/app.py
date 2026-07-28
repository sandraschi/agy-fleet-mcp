"""FastAPI app with MCP mounted at /mcp."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from agy_fleet_mcp.config import load_settings
from agy_fleet_mcp.server import mcp
from agy_fleet_mcp.startup_probe import run_startup_probes

mcp_http = mcp.http_app(path="/")


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    settings = load_settings()
    await run_startup_probes(settings)
    async with mcp_http.lifespan(app):
        yield


app = FastAPI(title="agy-fleet-mcp", version="0.1.0", lifespan=app_lifespan)
app.mount("/mcp", mcp_http)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agy-fleet-mcp"}
