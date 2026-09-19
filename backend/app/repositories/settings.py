import sqlite3

MAX_TRANSFERS_KEY = "max_transfers"
DEFAULT_MAX_TRANSFERS = 1


def get_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def get_int(conn: sqlite3.Connection, key: str, default: int) -> int:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    if row is None or row["value"] is None or row["value"] == "":
        return default
    try:
        return int(row["value"])
    except (TypeError, ValueError):
        return default


def get_max_transfers(conn: sqlite3.Connection) -> int:
    return get_int(conn, MAX_TRANSFERS_KEY, DEFAULT_MAX_TRANSFERS)


def upsert(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings(key,value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()


def set_max_transfers(conn: sqlite3.Connection, value: int) -> None:
    upsert(conn, MAX_TRANSFERS_KEY, str(int(value)))
