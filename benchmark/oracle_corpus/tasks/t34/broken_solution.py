def rank_contestants(contestants):
    ordered = sorted(
        contestants,
        key=lambda c: (-c["score"], c["penalty"], c["id"]),
    )

    result = []
    i = 0
    n = len(ordered)
    rank = 1
    while i < n:
        j = i + 1
        while (
            j < n
            and ordered[j]["score"] == ordered[i]["score"]
            and ordered[j]["penalty"] == ordered[i]["penalty"]
        ):
            j += 1
        for k in range(i, j):
            result.append((ordered[k]["id"], rank))
        rank += 1  # next group is just the next rank (no skipping)
        i = j

    return result
