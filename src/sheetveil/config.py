from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_CONFIG_NAME = "sheetveil.json"


@dataclass
class Settings:
    formula_mode: str = "preserve"  # preserve | hash
    token_style: str = "typed"  # typed | opaque
    token_hex_length: int = 32
    include_headers: bool = True
    strip_comments: bool = True
    strip_hyperlinks: bool = True
    strip_metadata: bool = True
    strip_defined_names: bool = False
    include_hidden_sheets: bool = True
    write_reports: bool = True

    def validate(self) -> None:
        if not isinstance(self.formula_mode, str):
            raise TypeError("formula_mode must be a string.")
        if self.formula_mode not in {"preserve", "hash"}:
            raise ValueError("formula_mode must be 'preserve' or 'hash'.")
        if not isinstance(self.token_style, str):
            raise TypeError("token_style must be a string.")
        if self.token_style not in {"typed", "opaque"}:
            raise ValueError("token_style must be 'typed' or 'opaque'.")
        if isinstance(self.token_hex_length, bool) or not isinstance(self.token_hex_length, int):
            raise TypeError("token_hex_length must be an integer.")
        if not 16 <= self.token_hex_length <= 64:
            raise ValueError("token_hex_length must be between 16 and 64.")
        for field in ("include_headers", "strip_comments", "strip_hyperlinks", "strip_metadata",
                      "strip_defined_names", "include_hidden_sheets", "write_reports"):
            if not isinstance(getattr(self, field), bool):
                raise TypeError(f"{field} must be a boolean.")


def load_settings(path: str | Path | None) -> Settings:
    if path is None:
        settings = Settings()
    else:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object.")
        allowed = set(Settings.__dataclass_fields__)
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unknown configuration keys: {', '.join(sorted(unknown))}")
        settings = Settings(**data)
    settings.validate()
    return settings


def write_default(path: str | Path, overwrite: bool = False) -> Path:
    output = Path(path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Configuration already exists: {output}")
    output.write_text(json.dumps(asdict(Settings()), indent=2) + "\n", encoding="utf-8")
    return output
