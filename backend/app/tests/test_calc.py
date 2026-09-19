import json

import pytest

from app import db, seed
from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import count_transfers, line_of, shortest_hops, shortest_path
from app.engines.route_quote import quote_route
from app.services.metro_service import MetroService

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
EDGES3 = EDGES + [("B2", "C1")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_shortest_path():
    assert shortest_path(EDGES, "A1", "B2") == ["A1", "A2", "B1", "B2"]
    assert shortest_path(EDGES, "A1", "A1") == ["A1"]
    assert shortest_path(EDGES, "A1", "ZZ") is None


def test_line_of_and_transfers():
    assert line_of("A1") == "A"
    assert line_of("b12") == "b"
    assert count_transfers(["A1", "A2", "A3"]) == 0
    assert count_transfers(["A1", "A2", "B1", "B2"]) == 1
    assert count_transfers(["A1", "A2", "B1", "B2", "C1"]) == 2


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote_without_limit_backward_compatible():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["hops"] == 3 and q["fare"] == 4.0
    assert q["reachable"] and q["allowed"] and q["transfers"] == 1


def test_quote_rejected_over_limit_keeps_path_and_transfers():
    q = quote_route(EDGES3, "A1", "C1", RULES, max_transfers=1)
    # 超限：可达但整单拒绝，不得降级成不可达、不出票价，仍带回途经与实际次数
    assert q["reachable"] is True
    assert q["allowed"] is False
    assert q["reason"] == "too_many_transfers"
    assert q["hops"] == 4
    assert q["transfers"] == 2
    assert q["max_transfers"] == 1
    assert q["fare"] is None
    assert q["path"] == ["A1", "A2", "B1", "B2", "C1"]


def test_quote_relax_limit_allows_ticket():
    rejected = quote_route(EDGES3, "A1", "C1", RULES, max_transfers=1)
    allowed = quote_route(EDGES3, "A1", "C1", RULES, max_transfers=2)
    assert rejected["allowed"] is False
    assert allowed["allowed"] is True
    assert allowed["transfers"] == 2 and allowed["fare"] == 4.0


def test_quote_unreachable_shape():
    q = quote_route(EDGES, "A1", "ZZ", RULES, max_transfers=0)
    assert q["reachable"] is False and q["allowed"] is False
    assert q["hops"] is None and q["transfers"] is None and q["path"] is None


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    yield


def _history_count():
    with MetroService() as s:
        return len(s.history(200))


def test_default_setting_seeded(temp_db):
    with MetroService() as s:
        assert s.settings()["max_transfers"] == 1


def test_service_ticket_writes_transfers(temp_db):
    with MetroService() as s:
        q = s.quote("A1", "B2", persist=True)
    assert q["reachable"] and q["allowed"]
    assert q["transfers"] == 1 and q["run_id"] is not None
    with MetroService() as s:
        row = s.history(1)[0]
        saved = json.loads(row["result_json"])
        assert saved["transfers"] == 1 and saved["fare"] == 4.0


def test_service_same_line_allowed_at_zero(temp_db):
    with MetroService() as s:
        s.update_settings(max_transfers=0)
        q = s.quote("A1", "A3", persist=True)
    assert q["allowed"] and q["transfers"] == 0 and q["run_id"] is not None


def test_service_over_limit_not_persisted_then_relaxed(temp_db):
    # 拼出需要 2 次换线的 A1 -> C1
    conn = db.connect()
    conn.execute("INSERT INTO stations(code,name) VALUES ('C1','西岭')")
    conn.execute("INSERT INTO edges(a,b) VALUES ('B2','C1')")
    conn.commit()
    conn.close()

    before = _history_count()
    with MetroService() as s:
        s.update_settings(max_transfers=1)
        rejected = s.quote("A1", "C1", persist=True)
    assert rejected["reachable"] and not rejected["allowed"]
    assert rejected["transfers"] == 2 and rejected["max_transfers"] == 1
    assert rejected["run_id"] is None and rejected["fare"] is None
    assert _history_count() == before  # 超限不得落库

    # 放宽上限后同一起终点须能出票
    with MetroService() as s:
        s.update_settings(max_transfers=2)
        allowed = s.quote("A1", "C1", persist=True)
    assert allowed["allowed"] and allowed["run_id"] is not None
    assert _history_count() == before + 1


def test_history_snapshot_not_rewritten_by_later_setting(temp_db):
    with MetroService() as s:
        ok = s.quote("A1", "B2", persist=True)
    run_id = ok["run_id"]
    # 后来把上限收紧到 0
    with MetroService() as s:
        s.update_settings(max_transfers=0)
        again = s.quote("A1", "B2", persist=True)
    assert again["allowed"] is False and again["run_id"] is None
    with MetroService() as s:
        row = [r for r in s.history(200) if r["id"] == run_id][0]
    saved = json.loads(row["result_json"])
    # 已写入记录保留当时换线次数与判定，不被新上限改写
    assert saved["transfers"] == 1
    assert saved["allowed"] is True
    assert saved["max_transfers"] == 1
