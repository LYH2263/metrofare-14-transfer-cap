from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_path


def quote_route(
    edges: list[tuple[str, str, str]],
    start: str,
    end: str,
    rules: list[dict],
    max_transfers: int | None = None,
) -> dict:
    path = shortest_path(edges, start, end)
    if path is None:
        return {
            "start": start,
            "end": end,
            "hops": None,
            "transfers": None,
            "max_transfers": max_transfers,
            "fare": None,
            "reachable": False,
            "accepted": False,
            "reason": "unreachable",
        }
    base = {
        "start": start,
        "end": end,
        "hops": path["hops"],
        "transfers": path["transfers"],
        "max_transfers": max_transfers,
        "reachable": True,
    }
    if max_transfers is not None and path["transfers"] > max_transfers:
        # Whole order rejected: report the real transfer count and the limit,
        # never degrade to "unreachable" and never price it.
        return {**base, "fare": None, "accepted": False, "reason": "transfers_exceeded"}
    return {**base, "fare": fare_for_hops(path["hops"], rules), "accepted": True, "reason": None}
