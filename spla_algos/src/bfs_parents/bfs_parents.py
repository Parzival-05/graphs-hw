from pyspla import INT, Matrix, Vector

from common.spla_utils import copy_matrix, copy_vector

MAX_INT = 2**31 - 1


def bfs_parents(s: list[int], A: Matrix):
    if A.n_cols != A.n_rows:
        raise RuntimeError(
            f"Incorrect input. A must be a square matrix, but got {A.n_rows}x{A.n_cols}."
        )
    INIT_VERTEX_ANSWER = 0
    zero_v = MAX_INT

    n = A.n_rows
    n_indices = [i for i in range(n)]
    s_indices = [i for i in range(len(s))]

    front: Matrix = Matrix.from_lists(
        s_indices,
        s,
        [x + 1 for x in s],
        shape=(len(s), n),
        dtype=INT,
        zero_v=zero_v,
    )
    p: Matrix = Matrix.from_lists(
        s_indices,
        s,
        [INIT_VERTEX_ANSWER] * len(s),
        shape=front.shape,
        dtype=front.dtype,
        zero_v=front._zero_V,
    )
    p_masked = Matrix(shape=p.shape, dtype=p.dtype, zero_v=p._zero_V)
    indices_matrix = Matrix.from_lists(
        [n_indices[i // n] for i in range(len(s) * n)],
        [n_indices[i % n] for i in range(len(s) * n)],
        [n_indices[i % n] + 1 for i in range(len(s) * n)],
        shape=p.shape,
        dtype=p.dtype,
        zero_v=p._zero_V,
    )
    prev_found = Vector(shape=len(s), dtype=INT)
    cur_found = Vector(shape=len(s), dtype=INT)
    diff = Vector(shape=len(s), dtype=INT)
    found_count = 1

    def calc_found(out: Vector):
        p.reduce_by_row(INT.PLUS, out=out)

    def calc_diff():
        cur_found.eadd(op_add=INT.MINUS, v=prev_found, out=diff)

    def calc_found_count():
        return diff.reduce(op_reduce=INT.PLUS).get()

    buffer = Matrix(shape=p.shape, dtype=p.dtype, zero_v=p._zero_V)
    while found_count > 0:
        p_masked = copy_matrix(p)
        front.mxm(
            A,
            op_add=INT.MIN_NON_ZERO_INT,
            op_mult=INT.FIRST,
            out=p,
        )
        p_masked.eadd(op_add=INT.FIRST, M=p, out=buffer)
        buffer.eadd(op_add=INT.SECOND, M=p_masked, out=p)
        p.emult(op_mult=INT.SECOND, M=indices_matrix, out=front)
        p_masked.eadd(op_add=INT.SECOND, M=p, out=buffer)
        p = copy_matrix(buffer)
        prev_found = copy_vector(cur_found)
        calc_found(cur_found)
        calc_diff()
        found_count = calc_found_count()
    p.emult(op_mult=INT.FST_MINUS_ONE_INT, M=p, out=buffer)
    return buffer
