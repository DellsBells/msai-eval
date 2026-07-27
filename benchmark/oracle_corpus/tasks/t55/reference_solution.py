def pass_token(n, rounds, step, quota):
    holds = [0] * n
    exhausted = [False] * n
    holder = 0
    # Initial hold by node 0.
    holds[0] += 1
    if holds[0] >= quota:
        exhausted[0] = True

    rounds_done = 0
    for _ in range(rounds):
        # Stuck check: is there any other non-exhausted node to move to?
        can_move = any(
            (i != holder) and (not exhausted[i]) for i in range(n)
        )
        if not can_move:
            break

        # Advance forward, counting only non-exhausted landings.
        pos = holder
        landed = 0
        while landed < step:
            pos = (pos + 1) % n
            if not exhausted[pos]:
                landed += 1
        holder = pos
        holds[holder] += 1
        if holds[holder] >= quota:
            exhausted[holder] = True
        rounds_done += 1

    exhausted_list = [i for i in range(n) if exhausted[i]]
    return {
        "holder": holder,
        "holds": holds,
        "exhausted": exhausted_list,
        "rounds_done": rounds_done,
    }
