def pass_token(n, rounds, step, quota):
    holds = [0] * n
    exhausted = set()
    holder = 0
    holds[holder] += 1

    rounds_done = 0

    for _ in range(rounds):
        if len(exhausted) == n - 1:
            break

        current_position = holder
        steps_taken = 0

        while steps_taken < step:
            current_position = (current_position + 1) % n
            if current_position not in exhausted:
                steps_taken += 1

        new_holder = current_position
        holds[new_holder] += 1
        if holds[new_holder] == quota:
            exhausted.add(new_holder)

        holder = new_holder
        rounds_done += 1

    return {
        "holder": holder,
        "holds": holds,
        "exhausted": sorted(exhausted),
        "rounds_done": rounds_done
    }