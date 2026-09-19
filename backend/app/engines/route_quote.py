from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import count_transfers, shortest_path


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    max_transfers: int | None = None,
) -> dict:
    """询价。max_transfers 为允许的最大换线次数；超过上限整单拒绝：
    仍返回 hops/path/transfers，但 reachable=True、allowed=False、fare=None。
    只读询价与写库走同一判定，调用方只应在 allowed 时落库。
    """
    path = shortest_path(edges, start, end)
    if path is None:
        return {
            "start": start,
            "end": end,
            "hops": None,
            "fare": None,
            "reachable": False,
            "allowed": False,
            "transfers": None,
            "max_transfers": max_transfers,
            "path": None,
        }
    hops = len(path) - 1
    transfers = count_transfers(path)
    result = {
        "start": start,
        "end": end,
        "hops": hops,
        "fare": None,
        "reachable": True,
        "allowed": True,
        "transfers": transfers,
        "max_transfers": max_transfers,
        "path": path,
    }
    if max_transfers is not None and transfers > max_transfers:
        result["allowed"] = False
        result["reason"] = "too_many_transfers"
        result["message"] = f"换线 {transfers} 次，超过上限 {max_transfers} 次"
        return result
    result["fare"] = fare_for_hops(hops, rules)
    return result
