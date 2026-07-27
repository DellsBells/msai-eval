import functools


def _match_points(scored, conceded):
    if scored > conceded:
        return 3
    if scored == conceded:
        return 1
    return 0


def league_table(teams, matches):
    # Aggregate per-team stats.
    stats = {
        t: {"points": 0, "goals_for": 0, "goals_against": 0}
        for t in teams
    }

    # Head-to-head points: h2h[(a, b)] = points team a earned in matches vs b.
    h2h = {}

    for home, away, hg, ag in matches:
        if home not in stats or away not in stats:
            # Match references a team not in the roster; ignore it.
            continue
        stats[home]["points"] += _match_points(hg, ag)
        stats[home]["goals_for"] += hg
        stats[home]["goals_against"] += ag

        stats[away]["points"] += _match_points(ag, hg)
        stats[away]["goals_for"] += ag
        stats[away]["goals_against"] += hg

        h2h[(home, away)] = h2h.get((home, away), 0) + _match_points(hg, ag)
        h2h[(away, home)] = h2h.get((away, home), 0) + _match_points(ag, hg)

    def gd(t):
        return stats[t]["goals_for"] - stats[t]["goals_against"]

    def compare(a, b):
        # Rule 1: points, higher first.
        if stats[a]["points"] != stats[b]["points"]:
            return -1 if stats[a]["points"] > stats[b]["points"] else 1
        # Rule 2: goal difference, higher first.
        if gd(a) != gd(b):
            return -1 if gd(a) > gd(b) else 1
        # Rule 3: goals for, higher first.
        if stats[a]["goals_for"] != stats[b]["goals_for"]:
            return -1 if stats[a]["goals_for"] > stats[b]["goals_for"] else 1
        # Rule 4: head-to-head points between exactly a and b.
        ha = h2h.get((a, b), 0)
        hb = h2h.get((b, a), 0)
        if ha != hb:
            return -1 if ha > hb else 1
        # Rule 5: name ascending (total tie-break).
        if a != b:
            return -1 if a < b else 1
        return 0

    ordered = sorted(teams, key=functools.cmp_to_key(compare))

    return [
        {
            "team": t,
            "points": stats[t]["points"],
            "goals_for": stats[t]["goals_for"],
            "goals_against": stats[t]["goals_against"],
            "goal_diff": gd(t),
        }
        for t in ordered
    ]
