from graphblas.core.matrix import Matrix


def copy_matrix(A: Matrix) -> Matrix:
    return A.dup()
