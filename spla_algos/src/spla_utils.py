from pyspla import Matrix, Vector


def copy_matrix(matrix: Matrix):
    out = Matrix(shape=matrix.shape, dtype=matrix.dtype, zero_v=matrix._zero_V)
    matrix.eadd(op_add=matrix.dtype.FIRST, M=out, out=out)
    return out


def copy_vector(vector: Vector):
    out = Vector(shape=vector.shape[0], dtype=vector.dtype, zero_v=vector._zero_V)
    vector.eadd(op_add=vector.dtype.FIRST, v=out, out=out)
    return out
