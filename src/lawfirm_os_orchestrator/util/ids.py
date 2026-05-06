from __future__ import annotations

import uuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def new_trace_id() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]
