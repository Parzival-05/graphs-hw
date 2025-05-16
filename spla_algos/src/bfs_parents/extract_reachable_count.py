from pyspla import Matrix

from bfs_parents import bfs_parents


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def extract_reachable_count(
    A: Matrix,
    nodes: list[int],
    chunk_size: int,
):
    if A.n_cols != A.n_rows:
        raise RuntimeError(
            f"Incorrect input. A must be a square matrix, but got {A.n_rows}x{A.n_cols}."
        )
    n = A.n_cols
    for i in range(0, len(nodes), chunk_size):
        chunk = nodes[i : min(i + chunk_size, n)]
        reachable_count: dict[int, int] = {}
        res_bfsp = bfs_parents.bfs_parents(chunk, A)
        for i, node in enumerate(chunk):
            col = res_bfsp.extract_row(i)
            res_count = len(col.to_list()) - 1  # -1 for the root node
            reachable_count[node] = res_count
        yield reachable_count
