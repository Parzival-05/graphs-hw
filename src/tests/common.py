M1 = (
    [0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 6, 6],
    [1, 3, 4, 6, 5, 0, 2, 5, 2, 2, 3, 4],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
)


def compare_answers(output, expected):
    output = "".join(output.split())
    expected = "".join(expected.split())
    if output == expected:
        return
    print("Expected:\n" + expected)
    print("Got:\n" + output)
    assert False
