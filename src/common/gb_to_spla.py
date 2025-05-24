from typing import Tuple
import graphblas as gb

gb.init("suitesparse", blocking=True)

from pyspla import INT, Matrix  # noqa: E402

from graphblas.core.matrix import Matrix as MatrixGB  # noqa: E402
from bfs_parents_spla.bfs_parents import ZERO_V  # noqa: E402


def convert_gb_to_spla(A: MatrixGB):
    I, J, V = extract_ijv_from_gb(A)  # noqa: E741
    return Matrix.from_lists(
        I, J, V, dtype=INT, shape=(A.nrows, A.ncols), zero_v=ZERO_V
    )


def extract_ijv_from_gb(A: MatrixGB) -> Tuple[list, list, list]:
    edges, V = A.to_edgelist()
    I, J = zip(*[(int(edge[0]), int(edge[1])) for edge in edges])  # noqa: E741
    return list(I), list(J), V.tolist()
