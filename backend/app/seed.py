import json
import re

from app.db import connect
from app.engines.route_quote import quote_route
from app.repositories import settings as settings_repo

EDGES = [("A1", "A2", "A"), ("A2", "A3", "A"), ("A2", "B1", "B"), ("B1", "B2", "B")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]


def _line_prefix(code: str) -> str:
    m = re.match(r"[A-Za-z]+", code or "")
    return m.group(0) if m else (code or "")


def _default_line(a: str, b: str) -> str:
    pa, pb = _line_prefix(a), _line_prefix(b)
    return pa if pa == pb else pb


def _migrate(conn):
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(edges)").fetchall()]
    if "line" not in cols:
        conn.execute("ALTER TABLE edges ADD COLUMN line TEXT")
        for r in conn.execute("SELECT rowid, a, b FROM edges").fetchall():
            conn.execute("UPDATE edges SET line = ? WHERE rowid = ?", (_default_line(r["a"], r["b"]), r["rowid"]))
    settings_repo.ensure_defaults(conn)
    conn.commit()


def init_db():
    conn = connect()
    conn.executescript(
        """
    CREATE TABLE IF NOT EXISTS stations(id INTEGER PRIMARY KEY, code TEXT, name TEXT);
    CREATE TABLE IF NOT EXISTS edges(a TEXT, b TEXT, line TEXT);
    CREATE TABLE IF NOT EXISTS fare_rules(id INTEGER PRIMARY KEY, max_hops INTEGER, price REAL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(
        id INTEGER PRIMARY KEY, kind TEXT, input_json TEXT, result_json TEXT, created_at TEXT);
    """
    )
    _migrate(conn)
    if conn.execute("SELECT COUNT(*) c FROM stations").fetchone()["c"] == 0:
        for code, name in [
            ("A1", "城站"),
            ("A2", "市心"),
            ("A3", "东湾"),
            ("B1", "北苑"),
            ("B2", "机场(种子绕远)"),
        ]:
            conn.execute("INSERT INTO stations(code, name) VALUES (?,?)", (code, name))
        for a, b, line in EDGES:
            conn.execute("INSERT INTO edges(a,b,line) VALUES (?,?,?)", (a, b, line))
        conn.executemany(
            "INSERT INTO fare_rules(max_hops, price) VALUES (?,?)",
            [(2, 3.0), (4, 4.0), (None, 6.0)],
        )
        conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('currency','CNY')")
        max_transfers = int(settings_repo.DEFAULTS["max_transfers"])
        q1 = quote_route(EDGES, "A1", "A3", RULES, max_transfers)
        conn.execute(
            "INSERT INTO calc_runs(kind,input_json,result_json,created_at) VALUES (?,?,?,datetime('now'))",
            ("quote", json.dumps({"start": "A1", "end": "A3"}), json.dumps(q1, ensure_ascii=False)),
        )
        conn.commit()
    conn.close()
