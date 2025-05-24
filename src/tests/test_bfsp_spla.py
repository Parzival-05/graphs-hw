from pyspla import INT, Matrix

from bfs_parents_spla.bfs_parents import bfs_parents
from tests.common import M1, compare_answers


def test_1():
    A = Matrix.from_lists(*M1, shape=(7, 7), dtype=INT)
    answer = bfs_parents([0], A)
    answer = str(answer)
    expected = """   
      0 1 2 3 4 5 6
    0|-1 0 3 0 1 2 1|  0
      0 1 2 3 4 5 6
      """
    compare_answers(answer, expected)


def test_2():
    A = Matrix.from_lists(*M1, shape=(7, 7), dtype=INT)
    answer = bfs_parents([0, 1, 2, 3], A)
    answer = str(answer)
    expected = """   
      0 1 2 3 4 5 6
    0|-1 0 3 0 1 2 1|  0
    1| 3-1 6 6 1 4 1|  1
    2| . .-1 . . 2 .|  2
    3| 3 0 3-1 1 2 1|  3
        0 1 2 3 4 5 6"""
    compare_answers(answer, expected)
