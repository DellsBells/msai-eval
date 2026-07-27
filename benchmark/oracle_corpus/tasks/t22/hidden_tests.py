import solution


def test_one_cw_turn_rectangular():
    m = [[1, 2, 3],
         [4, 5, 6]]
    assert solution.rotate_quarters(m, 1) == [[4, 1],
                                              [5, 2],
                                              [6, 3]]


def test_two_turns_180():
    m = [[1, 2, 3],
         [4, 5, 6]]
    assert solution.rotate_quarters(m, 2) == [[6, 5, 4],
                                              [3, 2, 1]]


def test_three_turns():
    m = [[1, 2, 3],
         [4, 5, 6]]
    assert solution.rotate_quarters(m, 3) == [[3, 6],
                                              [2, 5],
                                              [1, 4]]


def test_negative_one_equals_three():
    m = [[1, 2, 3],
         [4, 5, 6]]
    assert solution.rotate_quarters(m, -1) == solution.rotate_quarters(m, 3)
    assert solution.rotate_quarters(m, -1) == [[3, 6],
                                               [2, 5],
                                               [1, 4]]


def test_negative_three_equals_one():
    m = [[1, 2], [3, 4]]
    assert solution.rotate_quarters(m, -3) == solution.rotate_quarters(m, 1)


def test_large_k_reduces_mod_four():
    m = [[1, 2], [3, 4]]
    assert solution.rotate_quarters(m, 5) == solution.rotate_quarters(m, 1)
    assert solution.rotate_quarters(m, 5) == [[3, 1], [4, 2]]
    assert solution.rotate_quarters(m, 6) == solution.rotate_quarters(m, 2)


def test_zero_and_multiples_of_four_identity():
    m = [[1, 2, 3], [4, 5, 6]]
    assert solution.rotate_quarters(m, 0) == m
    assert solution.rotate_quarters(m, 4) == m
    assert solution.rotate_quarters(m, 8) == m
    assert solution.rotate_quarters(m, -4) == m


def test_single_cell():
    assert solution.rotate_quarters([[42]], 1) == [[42]]
    assert solution.rotate_quarters([[42]], 3) == [[42]]


def test_empty_matrix():
    assert solution.rotate_quarters([], 0) == []
    assert solution.rotate_quarters([], 1) == []
    assert solution.rotate_quarters([], -7) == []


def test_does_not_mutate_input():
    m = [[1, 2], [3, 4]]
    snapshot = [row[:] for row in m]
    solution.rotate_quarters(m, 1)
    assert m == snapshot


def test_returns_new_object_on_identity():
    m = [[1, 2], [3, 4]]
    out = solution.rotate_quarters(m, 0)
    assert out == m
    assert out is not m
    assert out[0] is not m[0]


def test_single_column_input():
    m = [[1], [2], [3]]
    # One CW turn of a 3x1 becomes 1x3: top row becomes rightmost column.
    assert solution.rotate_quarters(m, 1) == [[3, 2, 1]]


def test_property_four_turns_restore():
    # Property: k and k+4 always agree; rotating four times returns original.
    import random
    rng = random.Random(9981)
    for _ in range(60):
        rows = rng.randint(0, 5)
        cols = rng.randint(1, 5) if rows > 0 else 0
        if rows == 0:
            m = []
        else:
            m = [[rng.randint(-50, 50) for _ in range(cols)] for _ in range(rows)]
        base = solution.rotate_quarters(m, 0)
        assert base == m
        for k in range(-6, 7):
            assert solution.rotate_quarters(m, k) == solution.rotate_quarters(m, k + 4)
        # Four single turns compose back to the original.
        step = [row[:] for row in m]
        for _ in range(4):
            step = solution.rotate_quarters(step, 1)
        assert step == m
