def rank_contestants(contestants):
    if not contestants:
        return []

    # Sort contestants by score descending, then penalty ascending
    sorted_contestants = sorted(
        contestants,
        key=lambda x: (-x['score'], x['penalty'])
    )

    ranked_list = []
    rank = 1
    i = 0
    n = len(sorted_contestants)

    while i < n:
        # Count the number of tied contestants starting at index i
        tie_count = 1
        while i + tie_count < n and (
            sorted_contestants[i]['score'] == sorted_contestants[i + tie_count]['score'] and
            sorted_contestants[i]['penalty'] == sorted_contestants[i + tie_count]['penalty']
        ):
            tie_count += 1

        # Collect all tied contestants, sort them by id, and assign the current rank
        tied_group = sorted(
            sorted_contestants[i:i + tie_count],
            key=lambda x: x['id']
        )
        for contestant in tied_group:
            ranked_list.append((contestant['id'], rank))

        # Move to the next group of contestants
        rank += tie_count
        i += tie_count

    return ranked_list