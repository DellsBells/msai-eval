def rank_contestants(contestants):
    # Order best -> worst. Within a tie (same score and penalty), by id ascending.
    # Better means: higher score, then lower penalty.
    ordered = sorted(
        contestants,
        key=lambda c: (-c["score"], c["penalty"], c["id"]),
    )

    result = []
    i = 0
    n = len(ordered)
    while i < n:
        # Find the extent of the tie group (same score AND penalty).
        j = i + 1
        while (
            j < n
            and ordered[j]["score"] == ordered[i]["score"]
            and ordered[j]["penalty"] == ordered[i]["penalty"]
        ):
            j += 1
        rank = i + 1  # standard competition ranking: rank = index-of-first + 1
        for k in range(i, j):
            result.append((ordered[k]["id"], rank))
        i = j

    return result
