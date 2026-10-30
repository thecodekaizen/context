"""Shared Meta Model API transport for the hackathon engine."""

import os
from dataclasses import dataclass, field

import httpx


@dataclass(frozen=True)
class MetaSettings:
    provider: str = "meta"
    api_key: str = field(default="", repr=False)
    video_model: str = "muse-spark-1.2"
    search_model: str = "muse-spark-1.3"


def settings():
    return MetaSettings(api_key=os.getenv("MODEL_API_KEY", ""))


def configured():
    return bool(settings().api_key)


def public_settings():
    config = settings()
    return {
        "provider": "meta",
        "video_model": config.video_model,
        "search_model": config.search_model,
        "configured": bool(config.api_key),
        "capabilities": {"audio": True, "web_search": True},
        "media_destination": "Meta Model API",
    }


async def request(inputs, *, model=None, search=False, transport=None):
    config = settings()
    if not config.api_key:
        raise ValueError("MODEL_API_KEY is not configured")
    selected = (
        config.search_model
        if search or model == config.search_model
        else config.video_model
    )
    body = {"model": selected, "input": inputs}
    if search:
        body.update(tools=[{"type": "web_search"}], include=["web_search_call.results"])
    async with httpx.AsyncClient(
        timeout=150, transport=transport, follow_redirects=False
    ) as client:
        response = await client.post(
            "https://api.meta.ai/v1/responses",
            headers={"Authorization": "Bearer " + config.api_key},
            json=body,
        )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") not in (None, "completed"):
        raise ValueError("Meta returned an incomplete response")
    return payload
