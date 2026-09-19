from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_hops, shortest_path
from app.engines.route_quote import quote_route

EDGES = [("A1", "A2", "A"), ("A2", "A3", "A"), ("A2", "B1", "B"), ("B1", "B2", "B")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_transfers_same_line():
    assert shortest_path(EDGES, "A1", "A3") == {"hops": 2, "transfers": 0}


def test_transfers_across_lines():
    assert shortest_path(EDGES, "A1", "B2") == {"hops": 3, "transfers": 1}


def test_transfers_tiebreak_prefers_fewer():
    # two 2-hop paths X->Y; the one staying on L1 must win
    edges = [("X", "M", "L1"), ("M", "Y", "L1"), ("X", "N", "L1"), ("N", "Y", "L2")]
    assert shortest_path(edges, "X", "Y") == {"hops": 2, "transfers": 0}


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote():
    q = quote_route(EDGES, "A1", "B2", RULES, 2)
    assert q["hops"] == 3 and q["fare"] == 4.0
    assert q["accepted"] is True and q["transfers"] == 1 and q["max_transfers"] == 2


def test_quote_over_limit_rejected_not_unreachable():
    q = quote_route(EDGES, "A1", "B2", RULES, 0)
    assert q["accepted"] is False and q["reason"] == "transfers_exceeded"
    assert q["fare"] is None
    # must not degrade to unreachable: real counts stay in the response
    assert q["reachable"] is True and q["hops"] == 3
    assert q["transfers"] == 1 and q["max_transfers"] == 0


def test_quote_at_limit_accepted():
    q = quote_route(EDGES, "A1", "B2", RULES, 1)
    assert q["accepted"] is True and q["fare"] == 4.0


def test_quote_relaxed_limit_issues_again():
    assert quote_route(EDGES, "A1", "B2", RULES, 0)["accepted"] is False
    assert quote_route(EDGES, "A1", "B2", RULES, 1)["accepted"] is True


def test_quote_unreachable():
    q = quote_route(EDGES, "A1", "ZZ", RULES, 2)
    assert q["reachable"] is False and q["accepted"] is False and q["reason"] == "unreachable"
