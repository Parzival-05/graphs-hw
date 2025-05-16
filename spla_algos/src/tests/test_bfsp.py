from pyspla import INT, Matrix

from bfs_parents.bfs_parents import bfs_parents


def compare_answers(output, expected):
    output = "".join(output.split())
    expected = "".join(expected.split())
    if output == expected:
        return
    print("Expected:\n" + expected)
    print("Got:\n" + output)
    assert False


def test_1():
    I = [0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 6, 6]  # noqa: E741
    J = [1, 3, 4, 6, 5, 0, 2, 5, 2, 2, 3, 4]
    V = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    A = Matrix.from_lists(I, J, V, shape=(7, 7), dtype=INT)
    answer = bfs_parents([0], A)
    answer = str(answer)
    expected = """   
      0 1 2 3 4 5 6
    0|-1 0 3 0 1 2 1|  0
      0 1 2 3 4 5 6
      """
    compare_answers(answer, expected)


def test_2():
    I = [0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 6, 6]  # noqa: E741
    J = [1, 3, 4, 6, 5, 0, 2, 5, 2, 2, 3, 4]
    V = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    A = Matrix.from_lists(I, J, V, shape=(7, 7), dtype=INT)
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


if __name__ == "__main__":
    test_1()
    test_2()
