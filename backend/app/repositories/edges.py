import sqlite3


def list_edges(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    q = "SELECT a, b, line FROM edges"
    return [(r["a"], r["b"], r["line"] or "") for r in conn.execute(q).fetchall()]
