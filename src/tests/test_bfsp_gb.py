import graphblas as gb

gb.init("suitesparse", blocking=True)

from common.gb_to_spla import convert_gb_to_spla  # noqa: E402

from bfs_parents_gb.bfs_parents import bfs_parents  # noqa: E402
from graphblas.core.matrix import Matrix  # noqa: E402
from graphblas.core.dtypes import INT32  # noqa: E402

from tests.common import M1, compare_answers  # noqa: E402


def test_1():
    A = Matrix.from_coo(
        *M1,
        dtype=INT32,
        nrows=7,
        ncols=7,
    )  # type: ignore
    answer = bfs_parents([0], A)
    answer = convert_gb_to_spla(answer)
    answer = str(answer)
    expected = """   
      0 1 2 3 4 5 6
    0|-1 0 3 0 1 2 1|  0
      0 1 2 3 4 5 6
      """
    compare_answers(answer, expected)


def test_2():
    A = Matrix.from_coo(
        *M1,
        dtype=INT32,
        nrows=7,
        ncols=7,
    )  # type: ignore
    answer = bfs_parents([0, 1, 2, 3], A)
    answer = convert_gb_to_spla(answer)
    answer = str(answer)
    expected = """   
      0 1 2 3 4 5 6
    0|-1 0 3 0 1 2 1|  0
    1| 3-1 6 6 1 4 1|  1
    2| . .-1 . . 2 .|  2
    3| 3 0 3-1 1 2 1|  3
        0 1 2 3 4 5 6"""
    compare_answers(answer, expected)
