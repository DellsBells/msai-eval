import solution


def test_simple_step_one_no_exhaustion():
    result = solution.pass_token(4, 3, 1, 99)
    assert result == {
        "holder": 3,
        "holds": [1, 1, 1, 1],
        "exhausted": [],
        "rounds_done": 3,
    }


def test_exhaustion_walks_the_ring():
    result = solution.pass_token(3, 5, 1, 2)
    assert result == {
        "holder": 2,
        "holds": [2, 2, 2],
        "exhausted": [0, 1, 2],
        "rounds_done": 5,
    }


def test_single_node_is_stuck_immediately():
    result = solution.pass_token(1, 4, 1, 5)
    assert result == {
        "holder": 0,
        "holds": [1],
        "exhausted": [],
        "rounds_done": 0,
    }


def test_zero_rounds():
    # No passes: only node 0's initial hold registered.
    result = solution.pass_token(5, 0, 2, 3)
    assert result == {
        "holder": 0,
        "holds": [1, 0, 0, 0, 0],
        "exhausted": [],
        "rounds_done": 0,
    }


def test_step_larger_than_one_wraps():
    # step 2 on a 3-ring, high quota: 0 -> 2 -> 1 -> 0 -> 2 -> ...
    result = solution.pass_token(3, 4, 2, 99)
    # start holder 0 holds=[1,0,0]
    # pass1: +2 -> land on 2 (holds[2]=1)
    # pass2: from 2 +2 -> 0? forward 2->0 (1), 0->1 (2) land on 1 (holds[1]=1)
    # pass3: from 1 +2 -> 1->2(1),2->0(2) land on 0 (holds[0]=2)
    # pass4: from 0 +2 -> 0->1(1),1->2(2) land on 2 (holds[2]=2)
    assert result["holder"] == 2
    assert result["holds"] == [2, 1, 2]
    assert result["rounds_done"] == 4
    assert result["exhausted"] == []


def test_quota_one_exhausts_node_zero_at_start():
    # quota 1: node 0 is exhausted the instant it holds at the start.
    result = solution.pass_token(3, 2, 1, 1)
    # holds[0]=1 -> exhausted immediately.
    # pass1: from 0 land on 1 (holds[1]=1 -> exhausted).
    # pass2: from 1, skip 0 (exhausted), land on 2 (holds[2]=1 -> exhausted).
    assert result["holder"] == 2
    assert result["holds"] == [1, 1, 1]
    assert result["exhausted"] == [0, 1, 2]
    assert result["rounds_done"] == 2


def test_gets_stuck_when_others_exhausted():
    # 2 nodes, quota 1: node 0 exhausted at start; pass 1 lands on node 1 which
    # then exhausts. Now everyone is exhausted -> stuck, no more passes.
    result = solution.pass_token(2, 5, 1, 1)
    assert result["holder"] == 1
    assert result["holds"] == [1, 1]
    assert result["exhausted"] == [0, 1]
    assert result["rounds_done"] == 1


def test_skip_over_exhausted_node():
    # 4 nodes, step 1, quota 1. Every landing exhausts. Passing skips exhausted.
    result = solution.pass_token(4, 3, 1, 1)
    # holds[0]=1 exhausted. p1: 0->1 (exhaust). p2: 1->2 (exhaust).
    # p3: from 2 skip 3? no, 2->3 (not exhausted) land on 3 (exhaust).
    assert result["holder"] == 3
    assert result["holds"] == [1, 1, 1, 1]
    assert result["exhausted"] == [0, 1, 2, 3]
    assert result["rounds_done"] == 3


def test_stuck_when_holder_is_last_non_exhausted():
    # Sole-survivor boundary: after the holder is the ONLY non-exhausted node,
    # the ring is stuck (the spec looks at "nodes other than the current
    # holder"). The token must NOT keep self-landing on the holder.
    # n=2, step=2, quota=2:
    #   start holder 0 holds=[1,0]
    #   pass1: step 2 from 0 -> 0->1(1),1->0(2) land 0, holds=[2,0]; node0 exhausts
    #   pass2: step 2 from 0 (0 exhausted) -> lands on 1, holds=[2,1]; holder=1
    #   pass3 would-be: only node 1 (the holder) is non-exhausted -> STUCK, stop.
    result = solution.pass_token(2, 3, 2, 2)
    assert result == {
        "holder": 1,
        "holds": [2, 1],
        "exhausted": [0],
        "rounds_done": 2,
    }


def test_no_self_landing_after_others_exhaust():
    # Larger sole-survivor case: once every node except the holder is exhausted,
    # rounds_done must freeze even though rounds remain and the holder is not
    # itself exhausted. holds[holder] must not keep incrementing.
    # n=3, step=1, quota=1:
    #   holds[0]=1 -> node0 exhausts immediately
    #   pass1: 0->1 holds=[1,1,0]; node1 exhausts
    #   pass2: from 1 skip exhausted 0, land 2 holds=[1,1,1]; node2 exhausts
    #   now all exhausted -> stuck.
    result = solution.pass_token(3, 10, 1, 1)
    assert result["holder"] == 2
    assert result["holds"] == [1, 1, 1]
    assert result["exhausted"] == [0, 1, 2]
    assert result["rounds_done"] == 2

    # And a case where the holder alone survives non-exhausted with big step.
    # n=2, step=3, quota=2:
    #   start holder 0 holds=[1,0]
    #   pass1: step3 from 0 -> 0->1(1),1->0(2),0->1(3) land 1 holds=[1,1]; holder1
    #   pass2: step3 from 1 -> 1->0(1),0->1(2),1->0(3) land 0 holds=[2,1]; node0 ex
    #   pass3: step3 from 0 (exhausted) -> only node1 -> land 1 holds=[2,2]; node1 ex
    #   pass4: everyone exhausted -> stuck.
    result = solution.pass_token(2, 6, 3, 2)
    assert result["holder"] == 1
    assert result["holds"] == [2, 2]
    assert result["exhausted"] == [0, 1]
    assert result["rounds_done"] == 3


def test_property_matches_independent_oracle():
    # Cross-check the solution against a fully independent re-implementation of
    # the spec over many deterministic configs. Because the oracle stops exactly
    # when only the holder remains non-exhausted, this pins holds/rounds_done for
    # sole-survivor states an invariant-only check would miss.
    def oracle(n, rounds, step, quota):
        holds = [0] * n
        exhausted = [False] * n
        holder = 0
        holds[0] += 1
        if holds[0] >= quota:
            exhausted[0] = True
        done = 0
        for _ in range(rounds):
            # Stuck if no node OTHER THAN the holder is available.
            if not any((i != holder) and (not exhausted[i]) for i in range(n)):
                break
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
            done += 1
        return {
            "holder": holder,
            "holds": holds,
            "exhausted": [i for i in range(n) if exhausted[i]],
            "rounds_done": done,
        }

    seed = 20259
    for _ in range(500):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        n = 1 + (seed % 5)
        rounds = (seed >> 3) % 14
        step = 1 + ((seed >> 6) % 5)
        quota = 1 + ((seed >> 9) % 4)
        assert solution.pass_token(n, rounds, step, quota) == oracle(
            n, rounds, step, quota
        )


def test_property_invariants():
    # Property/invariant checks over many deterministic configurations:
    #   sum(holds) == 1 + rounds_done   (initial hold plus one per pass)
    #   exhausted list is exactly the sorted nodes with holds[i] >= quota
    #   holder is a valid index; rounds_done <= rounds
    #   holds has length n and all entries >= 0
    seed = 4242
    for _ in range(400):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        n = 1 + (seed % 6)
        rounds = (seed >> 3) % 12
        step = 1 + ((seed >> 6) % 4)
        quota = 1 + ((seed >> 9) % 4)
        res = solution.pass_token(n, rounds, step, quota)
        holds = res["holds"]
        assert len(holds) == n
        assert all(h >= 0 for h in holds)
        assert sum(holds) == 1 + res["rounds_done"]
        assert 0 <= res["holder"] < n
        assert res["rounds_done"] <= rounds
        expected_exhausted = sorted(i for i in range(n) if holds[i] >= quota)
        assert res["exhausted"] == expected_exhausted


def test_property_no_exhaustion_high_quota():
    # With a very high quota no node ever exhausts, and step-1 passing simply
    # advances one position each pass (never stuck for n >= 2).
    seed = 77
    for _ in range(200):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        n = 2 + (seed % 5)
        rounds = (seed >> 4) % 15
        res = solution.pass_token(n, rounds, 1, 10**9)
        assert res["exhausted"] == []
        assert res["rounds_done"] == rounds
        assert res["holder"] == rounds % n
