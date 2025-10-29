import pytest


@pytest.fixture(autouse=True)
def use_temp_db(monkeypatch, tmp_path):
    db_file = tmp_path / "onepaisa_test.sqlite"
    monkeypatch.setenv("ONEPAISA_DB_PATH", str(db_file))
    yield