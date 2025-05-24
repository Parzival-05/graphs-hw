from enum import StrEnum


class Algo(StrEnum):
    SPLA = "spla"
    GRAPHBLAS = "graphblas"

    def __repr__(self):
        return self.value
