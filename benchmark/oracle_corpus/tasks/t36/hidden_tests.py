import random

import solution


def _by_name(table):
    return {row["team"]: row for row in table}


def test_example_1():
    teams = ["A", "B", "C"]
    matches = [
        ("A", "B", 2, 0),
        ("B", "A", 1, 1),
        ("C", "A", 0, 3),
        ("C", "B", 0, 3),
    ]
    out = solution.league_table(teams, matches)
    assert [r["team"] for r in out] == ["A", "B", "C"]
    d = _by_name(out)
    assert d["A"] == {"team": "A", "points": 7, "goals_for": 6, "goals_against": 1, "goal_diff": 5}
    assert d["B"] == {"team": "B", "points": 4, "goals_for": 4, "goals_against": 3, "goal_diff": 1}
    assert d["C"] == {"team": "C", "points": 0, "goals_for": 0, "goals_against": 6, "goal_diff": -6}


def test_example_2_full_tie_name_order():
    teams = ["X", "Y"]
    matches = [("X", "Y", 2, 1), ("Y", "X", 1, 0)]
    out = solution.league_table(teams, matches)
    assert [r["team"] for r in out] == ["X", "Y"]
    d = _by_name(out)
    assert d["X"]["points"] == 3 and d["Y"]["points"] == 3
    assert d["X"]["goal_diff"] == 0 and d["Y"]["goal_diff"] == 0
    assert d["X"]["goals_for"] == 2 and d["Y"]["goals_for"] == 2


def test_example_3_points_dominate():
    teams = ["P", "Q"]
    matches = [("Q", "P", 0, 1)]
    out = solution.league_table(teams, matches)
    assert [r["team"] for r in out] == ["P", "Q"]


def test_empty_teams():
    assert solution.league_table([], []) == []
    assert solution.league_table([], [("A", "B", 1, 0)]) == []


def test_team_with_no_matches():
    teams = ["Solo"]
    out = solution.league_table(teams, [])
    assert out == [
        {"team": "Solo", "points": 0, "goals_for": 0, "goals_against": 0, "goal_diff": 0}
    ]


def test_head_to_head_overrides_name():
    # A and B tie on points, goal_diff, goals_for; B won the head-to-head, so B
    # ranks above A even though "A" < "B". D is clearly first, C clearly last.
    teams = ["A", "B", "C", "D"]
    matches = [("B", "A", 2, 0), ("A", "C", 3, 1), ("D", "B", 3, 1)]
    out = solution.league_table(teams, matches)
    assert [r["team"] for r in out] == ["D", "B", "A", "C"]
    d = _by_name(out)
    # Confirm A and B really are tied on the first three keys.
    assert d["A"]["points"] == d["B"]["points"] == 3
    assert d["A"]["goal_diff"] == d["B"]["goal_diff"] == 0
    assert d["A"]["goals_for"] == d["B"]["goals_for"] == 3


def test_head_to_head_uses_points_not_margin():
    # A and B tie on points, goal_diff, goals_for AND on head-to-head points
    # (each won one of their two mutual matches: 3-3). Because head-to-head is
    # decided by POINTS (not goal margin / goals scored in those matches), rule 4
    # does NOT separate them, so rule 5 (name, ascending) puts A before B.
    #
    # A implementation that (wrongly) used head-to-head goal difference or
    # head-to-head goals-for would rank B above A here: in their mutual matches A
    # scored 1 and conceded 2 while B scored 2 and conceded 1.
    teams = ["A", "B", "C"]
    matches = [
        ("A", "B", 1, 0),   # A beats B 1-0
        ("B", "A", 2, 0),   # B beats A 2-0
        ("A", "C", 1, 2),   # C beats A
        ("B", "C", 0, 3),   # C beats B
    ]
    out = solution.league_table(teams, matches)
    d = _by_name(out)
    # Confirm the tie really goes all the way to rule 4/5.
    assert d["A"]["points"] == d["B"]["points"] == 3
    assert d["A"]["goal_diff"] == d["B"]["goal_diff"] == -2
    assert d["A"]["goals_for"] == d["B"]["goals_for"] == 2
    # Head-to-head points tie 3-3, so name decides: A before B. C is first.
    assert [r["team"] for r in out] == ["C", "A", "B"]


def test_head_to_head_points_over_goals_single_meeting():
    # A and B meet once and DRAW that match, so head-to-head points tie (1-1)
    # even though the shared match had goals. They also tie on all aggregate
    # keys. A head-to-head-goals-for tie-break would still tie here (both scored
    # 2 in the meeting), but this pins the "draw => equal h2h points" behaviour
    # and the name tie-break direction.
    teams = ["A", "B"]
    matches = [("A", "B", 2, 2)]
    out = solution.league_table(teams, matches)
    d = _by_name(out)
    assert d["A"]["points"] == d["B"]["points"] == 1
    assert d["A"]["goal_diff"] == d["B"]["goal_diff"] == 0
    assert [r["team"] for r in out] == ["A", "B"]


def test_goal_diff_breaks_points_tie():
    teams = ["L", "M"]
    matches = [
        ("L", "M", 5, 0),  # L wins big
        ("M", "L", 1, 0),  # M wins small
    ]
    out = solution.league_table(teams, matches)
    # Both 3 points. L: gf5 ga1 gd4 ; M: gf1 ga5 gd-4. L first on goal diff.
    assert [r["team"] for r in out] == ["L", "M"]


def test_full_tie_head_to_head_equal_name_order():
    # Same points and same goal_diff and same goals_for; head-to-head also equal
    # (both draws) -> rule 5 (name) puts H before K.
    teams = ["H", "K"]
    matches = [
        ("H", "K", 1, 1),  # draw
        ("K", "H", 3, 3),  # draw, more goals
    ]
    out = solution.league_table(teams, matches)
    d = _by_name(out)
    # Both: 2 draws => 2 points, gd 0. H gf = 1+3 = 4, K gf = 1+3 = 4 -> also equal.
    assert d["H"]["points"] == 2 and d["K"]["points"] == 2
    assert d["H"]["goals_for"] == 4 and d["K"]["goals_for"] == 4
    assert [r["team"] for r in out] == ["H", "K"]


def test_goals_for_breaks_goal_diff_tie():
    # Two teams, same points and same goal_diff, but different goals_for.
    # They never play each other, so head-to-head is irrelevant; goals_for decides.
    teams = ["Lo", "Hi", "Opp1", "Opp2"]
    matches = [
        ("Lo", "Opp1", 1, 0),   # Lo: win, gf1 ga0 gd+1, pts3
        ("Hi", "Opp2", 4, 3),   # Hi: win, gf4 ga3 gd+1, pts3
    ]
    out = solution.league_table(teams, matches)
    order = [r["team"] for r in out]
    d = _by_name(out)
    assert d["Lo"]["points"] == 3 and d["Hi"]["points"] == 3
    assert d["Lo"]["goal_diff"] == 1 and d["Hi"]["goal_diff"] == 1
    # Hi has more goals_for (4 > 1) so Hi ranks above Lo despite name "Hi" > ...
    assert order.index("Hi") < order.index("Lo")


def test_repeated_matches_accumulate():
    teams = ["Z", "W"]
    matches = [
        ("Z", "W", 1, 0),
        ("Z", "W", 1, 0),
        ("Z", "W", 1, 0),
    ]
    out = solution.league_table(teams, matches)
    d = _by_name(out)
    assert d["Z"]["points"] == 9
    assert d["Z"]["goals_for"] == 3 and d["Z"]["goals_against"] == 0
    assert d["W"]["points"] == 0
    assert [r["team"] for r in out] == ["Z", "W"]


def test_input_not_mutated():
    teams = ["A", "B"]
    matches = [("A", "B", 2, 1)]
    teams_copy = list(teams)
    matches_copy = list(matches)
    solution.league_table(teams, matches)
    assert teams == teams_copy
    assert matches == matches_copy


def test_property_aggregates_and_partial_order():
    rng = random.Random(4242)
    for _ in range(150):
        names = ["A", "B", "C", "D", "E"]
        k = rng.randint(0, 5)
        teams = names[:k]
        matches = []
        for _ in range(rng.randint(0, 12)):
            if len(teams) < 2:
                break
            a, b = rng.sample(teams, 2)
            matches.append((a, b, rng.randint(0, 4), rng.randint(0, 4)))

        out = solution.league_table(teams, matches)

        # Every team present exactly once, with the exact key set.
        assert sorted(r["team"] for r in out) == sorted(teams)
        for r in out:
            assert set(r.keys()) == {
                "team",
                "points",
                "goals_for",
                "goals_against",
                "goal_diff",
            }
            assert r["goal_diff"] == r["goals_for"] - r["goals_against"]

        # Recompute aggregates independently and check.
        exp = {
            t: {"points": 0, "gf": 0, "ga": 0} for t in teams
        }
        for home, away, hg, ag in matches:
            exp[home]["gf"] += hg
            exp[home]["ga"] += ag
            exp[away]["gf"] += ag
            exp[away]["ga"] += hg
            if hg > ag:
                exp[home]["points"] += 3
            elif hg == ag:
                exp[home]["points"] += 1
                exp[away]["points"] += 1
            else:
                exp[away]["points"] += 3
        d = _by_name(out)
        for t in teams:
            assert d[t]["points"] == exp[t]["points"]
            assert d[t]["goals_for"] == exp[t]["gf"]
            assert d[t]["goals_against"] == exp[t]["ga"]

        # Rules 1-3 are transitive: every adjacent pair must be non-increasing on
        # (points, goal_diff, goals_for) OR tie there (then rule 4/5 decide).
        for x, y in zip(out, out[1:]):
            kx = (x["points"], x["goal_diff"], x["goals_for"])
            ky = (y["points"], y["goal_diff"], y["goals_for"])
            assert kx >= ky
