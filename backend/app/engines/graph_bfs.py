import re
from collections import defaultdict, deque

_LINE_RE = re.compile(r"^[A-Za-z]+")


def line_of(code: str) -> str:
    """线路取站点编码的字母前缀（A1 -> A）；无字母前缀时退回整码。"""
    m = _LINE_RE.match(code or "")
    return m.group(0) if m else code


def build_graph(edges: list[tuple[str, str]]) -> dict[str, set[str]]:
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    return g


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """无向图 BFS 最短途经站序列；不可达返回 None。"""
    if start == end:
        return [start]
    g = build_graph(edges)
    if start not in g or end not in g:
        return None
    prev: dict[str, str | None] = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in sorted(g[cur]):
            if nxt in prev:
                continue
            prev[nxt] = cur
            if nxt == end:
                path = [end]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                path.reverse()
                return path
            q.append(nxt)
    return None


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else len(path) - 1


def count_transfers(path: list[str]) -> int:
    """在途经边上数换线次数：相邻两站线路前缀不同即该边为一次换线。"""
    return sum(1 for i in range(1, len(path)) if line_of(path[i - 1]) != line_of(path[i]))
