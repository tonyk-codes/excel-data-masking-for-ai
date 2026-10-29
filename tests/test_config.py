import json

import pytest

from sheetveil.config import load_settings


@pytest.mark.parametrize(
    ("key", "value", "error"),
    [
        ("include_headers", "false", TypeError),
        ("token_hex_length", "32", TypeError),
    ],
)
def test_rejects_wrong_config_types(tmp_path, key, value, error):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({key: value}), encoding="utf-8")
    with pytest.raises(error):
        load_settings(path)


def test_rejects_non_object_config(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_settings(path)