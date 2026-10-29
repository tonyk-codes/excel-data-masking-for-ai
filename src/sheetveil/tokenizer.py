from __future__ import annotations

import base64
import hashlib
import hmac
import math
import os
import secrets
import tempfile
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path


def generate_key() -> bytes:
    return secrets.token_bytes(32)


def save_key(path: str | Path, key: bytes) -> None:
    if len(key) < 32:
        raise ValueError("Key must contain at least 256 bits.")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = base64.urlsafe_b64encode(key) + b"\n"
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    try:
        if os.name != "nt":
            os.chmod(temporary_name, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, output)
        if os.name != "nt":
            os.chmod(output, 0o600)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def load_key(path: str | Path) -> bytes:
    raw = Path(path).read_text(encoding="ascii").strip()
    key = base64.urlsafe_b64decode(raw.encode("ascii"))
    if len(key) < 32:
        raise ValueError("Key must contain at least 256 bits.")
    return key


def _float_text(value: float) -> str:
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "+Infinity" if value > 0 else "-Infinity"
    return format(value, ".17g")


def canonicalize(value) -> tuple[str, str]:
    if value is None:
        return "BLANK", ""
    if isinstance(value, bool):
        return "BOOL", "TRUE" if value else "FALSE"
    if isinstance(value, datetime):
        return "DATETIME", value.isoformat(timespec="microseconds")
    if isinstance(value, date):
        return "DATE", value.isoformat()
    if isinstance(value, time):
        return "TIME", value.isoformat(timespec="microseconds")
    if isinstance(value, int):
        return "INT", str(value)
    if isinstance(value, float):
        return "DEC", _float_text(value)
    if isinstance(value, Decimal):
        return "DEC", format(value, "f")
    if isinstance(value, bytes):
        return "BYTES", base64.b64encode(value).decode("ascii")
    return "TEXT", str(value)


def token_for(value, key: bytes, token_style: str = "typed", hex_length: int = 32) -> str:
    kind, normalized = canonicalize(value)
    message = f"{kind}|{normalized}".encode()
    digest = hmac.new(key, message, hashlib.sha256).hexdigest()[:hex_length].upper()
    prefix = kind if token_style == "typed" else "VAL"
    return f"{prefix}_{digest}"
