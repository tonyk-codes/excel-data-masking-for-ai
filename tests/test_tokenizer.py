import os

from sheetveil.tokenizer import (
    canonicalize,
    generate_key,
    load_key,
    save_key,
    token_for,
)


def test_stable_with_same_key():
    key = generate_key()
    assert token_for("example", key) == token_for("example", key)


def test_different_keys_produce_different_tokens():
    assert token_for("example", generate_key()) != token_for("example", generate_key())


def test_type_sensitive():
    key = generate_key()
    assert token_for("1", key) != token_for(1, key)
    assert canonicalize(True)[0] == "BOOL"


def test_saved_key_is_private_and_round_trips(tmp_path):
    path = tmp_path / "private.key"
    key = generate_key()
    save_key(path, key)
    assert load_key(path) == key
    if os.name != "nt":
        assert path.stat().st_mode & 0o777 == 0o600
