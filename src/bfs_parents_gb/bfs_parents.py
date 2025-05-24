import graphblas as gb

gb.init("suitesparse", blocking=True)

from graphblas.core.scalar import Scalar  # noqa: E402
from graphblas import binary, semiring  # noqa: E402
from graphblas.core.vector import Vector  # noqa: E402
from graphblas.core.matrix import Matrix  # noqa: E402
from graphblas.core.dtypes import INT32  # noqa: E402


def first_minus_one(x: int, y: int) -> int:
    return x - 1


binary.register_new("first_minus_one", first_minus_one)


def bfs_parents(s: list[int], A: Matrix):
    if A.ncols != A.nrows:
        raise RuntimeError(
            f"Incorrect input. A must be a square matrix, but got {A.nrows}x{A.ncols}."
        )
    INIT_VERTEX_ANSWER = 0

    n = A.ncols

    n_indices = [i for i in range(n)]
    s_indices = [i for i in range(len(s))]

    front: Matrix = Matrix.from_coo(
        s_indices,
        s,
        [x + 1 for x in s],  # type: ignore
        nrows=len(s),
        ncols=n,
        dtype=INT32,
    )
    p: Matrix = Matrix.from_coo(
        s_indices,
        s,
        [INIT_VERTEX_ANSWER] * len(s),  # type: ignore
        nrows=front.nrows,
        ncols=front.ncols,
        dtype=INT32,
    )
    p_masked = Matrix(ncols=p.ncols, nrows=p.nrows, dtype=p.dtype)
    indices_matrix = Matrix.from_coo(
        [n_indices[i // n] for i in range(len(s) * n)],
        [n_indices[i % n] for i in range(len(s) * n)],
        [n_indices[i % n] + 1 for i in range(len(s) * n)],  # type: ignore
        nrows=p.nrows,
        ncols=p.ncols,
        dtype=p.dtype,
    )
    prev_found = Vector(size=len(s), dtype=INT32)
    cur_found = Vector(size=len(s), dtype=INT32)
    diff = Vector(size=len(s), dtype=INT32)
    found_count = 1
    found_count_scalar = Scalar.from_value(1)
    buffer = Matrix(nrows=p.nrows, ncols=p.ncols, dtype=p.dtype)
    while found_count > 0:
        p_masked = p.dup()
        p << semiring.min_first(front @ A)  # pyright: ignore[reportAttributeAccessIssue, reportUnusedExpression]
        buffer << binary.first(p_masked | p)  # pyright: ignore[reportUnusedExpression]
        p << binary.second(buffer | p_masked)  # pyright: ignore[reportUnusedExpression]
        front << binary.second(p & indices_matrix)  # pyright: ignore[reportUnusedExpression]
        buffer << binary.second(p_masked | p)  # pyright: ignore[reportUnusedExpression]
        p = buffer.dup()
        prev_found = cur_found.dup()
        cur_found << p.reduce_rowwise("plus")  # pyright: ignore[reportUnusedExpression]
        diff << binary.minus(cur_found | prev_found)  # pyright: ignore[reportUnusedExpression]

        found_count_scalar << diff.reduce("plus")  # pyright: ignore[reportUnusedExpression]
        found_count = int(found_count_scalar)
    buffer << binary.first_minus_one(p & p)  # pyright: ignore[reportUnusedExpression]
    return buffer
