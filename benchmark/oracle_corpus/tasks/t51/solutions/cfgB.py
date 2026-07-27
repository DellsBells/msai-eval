def capped_keystroke_distance(a: str, b: str, cap: int) -> int:
    if len(a) + len(b) == 0:
        return -1

    cost = [float('inf')] * (len(b) + 1)
    cost[0] = 0
    for i in range(1, len(a) + 1):
        new_cost = float('inf')
        for j in range(len(b) + 1):
            if a[i - 1] == b[j - 1]:
                new_cost = min(new_cost, cost[j])
            else:
                new_cost = min(new_cost, cost[j - 1] + 1)
        for k in range(len(cost)):
            cost[k] = min(cost[k], new_cost)

    return min(cost[len(b)], cap) if cost[len(b)] <= cap else -1