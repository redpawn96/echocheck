import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.mark.unit
def test_password_hash_and_verify() -> None:
    password = "StrongPass123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


@pytest.mark.unit
def test_create_and_decode_access_token() -> None:
    user_id = "user-123"
    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert decode_access_token(token) == user_id
