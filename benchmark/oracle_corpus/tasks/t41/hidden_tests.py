import solution


def _brute(readings, threshold):
    # Independent O(n^2) reference used by property tests.
    best_len = 0
    best_start = -1
    n = len(readings)
    i = 0
    while i < n:
        if readings[i] > threshold:
            j = i
            while j < n and readings[j] > threshold:
                j += 1
            run_len = j - i
            if run_len > best_len:
                best_len = run_len
                best_start = i
            i = j
        else:
            i += 1
    return (best_len, best_start)


def test_basic_example():
    assert solution.longest_above_run([1, 5, 6, 2, 7, 8, 9, 3], 4) == (3, 4)


def test_nothing_above_threshold():
    assert solution.longest_above_run([10, 10, 3, 10, 10], 10) == (0, -1)


def test_tie_breaks_earliest():
    assert solution.longest_above_run([9, 9, 1, 8, 8], 5) == (2, 0)


def test_empty_input():
    assert solution.longest_above_run([], 0) == (0, -1)


def test_single_element_qualifies():
    assert solution.longest_above_run([7], 3) == (1, 0)


def test_single_element_does_not_qualify():
    assert solution.longest_above_run([3], 3) == (0, -1)


def test_all_qualify():
    assert solution.longest_above_run([2, 3, 4, 5], 1) == (4, 0)


def test_equal_to_threshold_breaks_run():
    # The 5 equals the threshold and must break the run.
    assert solution.longest_above_run([6, 6, 5, 6, 6, 6], 5) == (3, 3)


def test_float_and_negative_values():
    assert solution.longest_above_run([-1.5, -0.5, -3.0, 0.5, 0.6], -1.0) == (2, 3)


def test_does_not_mutate_input():
    data = [4, 8, 2, 9, 9]
    snapshot = list(data)
    solution.longest_above_run(data, 5)
    assert data == snapshot


def test_run_at_end():
    assert solution.longest_above_run([1, 1, 2, 3], 1) == (2, 2)


def test_property_matches_brute_force():
    # Deterministic seeded generation compared against an independent brute force.
    import random
    rng = random.Random(20240704)
    for _ in range(300):
        n = rng.randint(0, 25)
        readings = [rng.randint(-5, 5) for _ in range(n)]
        threshold = rng.randint(-5, 5)
        assert solution.longest_above_run(readings, threshold) == _brute(readings, threshold)
