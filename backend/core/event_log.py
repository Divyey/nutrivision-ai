"""Human-readable event logs for operators and for AI log review.

One record, multiple lines. Event names are stable (`meals.create`). Emoji is
the visual prefix, not the identity. Do not log tokens, passwords, or raw
image bytes.
"""

from __future__ import annotations

import logging
import time
from typing import Any

LOGGER_NAME = "nutrivision"


def elapsed_ms(started: float) -> str:
    return f"{(time.perf_counter() - started) * 1000:.0f} ms"


def short_id(value: object, visible: int = 8) -> str:
    text = str(value)
    if len(text) <= visible:
        return text
    return f"{text[:visible]}..."


def format_event(emoji: str, title: str, event: str, fields: dict[str, Any]) -> str:
    lines = [f"{emoji}  {title}", f"   {event}"]
    pairs = list(fields.items())
    width = max((len(key) for key, _ in pairs), default=8)
    for index, (key, value) in enumerate(pairs):
        branch = "└─" if index == len(pairs) - 1 else "├─"
        lines.append(f"   {branch} {key:<{width}} : {value}")
    return "\n".join(lines)


def log_event(
    logger: logging.Logger,
    level: int,
    emoji: str,
    title: str,
    event: str,
    **fields: Any,
) -> None:
    logger.log(level, format_event(emoji, title, event, fields))
