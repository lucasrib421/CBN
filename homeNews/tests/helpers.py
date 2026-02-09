def assert_keys(payload: dict, expected: set[str]) -> None:
    assert set(payload.keys()) == expected
