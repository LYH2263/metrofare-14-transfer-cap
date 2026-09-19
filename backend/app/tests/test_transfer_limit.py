import json

import app.db as db
from app import seed
from app.services.metro_service import MetroService


def _fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()


def _run_count():
    with db.connect() as conn:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]


def test_over_limit_not_persisted_then_relax_allows_issue(tmp_path, monkeypatch):
    _fresh_db(tmp_path, monkeypatch)
    with MetroService() as s:
        s.update_settings({"max_transfers": 0})
        before = _run_count()
        rejected = s.quote("A1", "B2", True)
        assert rejected["accepted"] is False
        assert rejected["reason"] == "transfers_exceeded"
        assert rejected["transfers"] == 1 and rejected["max_transfers"] == 0
        assert rejected["run_id"] is None
        assert _run_count() == before  # over-limit must not be stored

        s.update_settings({"max_transfers": 1})
        ok = s.quote("A1", "B2", True)  # same origin/destination after relaxing
        assert ok["accepted"] is True and ok["run_id"] is not None
        assert ok["transfers"] == 1 and ok["fare"] == 4.0


def test_read_and_write_share_the_same_judgment(tmp_path, monkeypatch):
    _fresh_db(tmp_path, monkeypatch)
    with MetroService() as s:
        s.update_settings({"max_transfers": 0})
        trial = s.quote("A1", "B2", False)
        order = s.quote("A1", "B2", True)
        for r in (trial, order):
            assert r["accepted"] is False and r["reason"] == "transfers_exceeded"
        assert _run_count() == 1  # only the seeded run; neither attempt persisted


def test_history_keeps_transfer_count_from_write_time(tmp_path, monkeypatch):
    _fresh_db(tmp_path, monkeypatch)
    with MetroService() as s:
        assert s.settings()["max_transfers"] == "2"
        issued = s.quote("A1", "B2", True)
        assert issued["accepted"] and issued["transfers"] == 1

        s.update_settings({"max_transfers": 0})  # later tightening must not rewrite history
        records = [h for h in s.history() if json.loads(h["input_json"]) == {"start": "A1", "end": "B2"}]
        assert len(records) == 1
        stored = json.loads(records[0]["result_json"])
        assert stored["transfers"] == 1 and stored["max_transfers"] == 2
