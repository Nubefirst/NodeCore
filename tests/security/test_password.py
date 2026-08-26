from backend.app.security.password import hash_password, verify_password


def test_hash_password():
    password = "my_password"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2")


def test_hashes_are_different():
    password = "my_password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_verify_correct_password():
    password = "my_password"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_wrong_password():
    password = "my_password"
    password_hash = hash_password(password)

    assert verify_password("wrong_password", password_hash) is False