from collections import defaultdict
import heapq
import itertools


def shortest_path(edges: list[tuple[str, str, str]], start: str, end: str) -> dict | None:
    """Undirected graph search over (a, b, line) edges.

    Returns {"hops": int, "transfers": int} for the path with the fewest
    hops; ties are broken by fewest line transfers. None if unreachable.
    """
    if start == end:
        return {"hops": 0, "transfers": 0}
    g: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for a, b, line in edges:
        g[a].append((b, line))
        g[b].append((a, line))
    if start not in g or end not in g:
        return None
    # Dijkstra over lexicographic (hops, transfers); state includes the
    # line used to arrive, since a transfer is counted on line change.
    counter = itertools.count()
    pq = [((0, 0), next(counter), start, None)]
    best: dict[tuple[str, str | None], tuple[int, int]] = {}
    while pq:
        cost, _, cur, line = heapq.heappop(pq)
        state = (cur, line)
        if state in best and best[state] <= cost:
            continue
        best[state] = cost
        if cur == end:
            return {"hops": cost[0], "transfers": cost[1]}
        hops, transfers = cost
        for nxt, nxt_line in g[cur]:
            nt = transfers + (0 if line is None or nxt_line == line else 1)
            heapq.heappush(pq, ((hops + 1, nt), next(counter), nxt, nxt_line))
    return None


def shortest_hops(edges: list[tuple[str, str, str]], start: str, end: str) -> int | None:
    """Undirected graph hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else path["hops"]
