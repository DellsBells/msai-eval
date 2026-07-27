def _match_points(scored, conceded):
    if scored > conceded:
        return 3
    if scored == conceded:
        return 1
    return 0


def league_table(teams, matches):
    stats = {
        t: {"points": 0, "goals_for": 0, "goals_against": 0}
        for t in teams
    }

    for home, away, hg, ag in matches:
        if home not in stats or away not in stats:
            continue
        stats[home]["points"] += _match_points(hg, ag)
        stats[home]["goals_for"] += hg
        stats[home]["goals_against"] += ag

        stats[away]["points"] += _match_points(ag, hg)
        stats[away]["goals_for"] += ag
        stats[away]["goals_against"] += hg

    def gd(t):
        return stats[t]["goals_for"] - stats[t]["goals_against"]

    ordered = sorted(
        teams,
        key=lambda t: (
            -stats[t]["points"],
            -gd(t),
            -stats[t]["goals_for"],
            t,
        ),
    )

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
