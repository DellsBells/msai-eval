# League Table with Head-to-Head Tie-Breaking

Compute the final ordered standings of a round-robin-style league from a list of
played matches, applying a strict tie-breaking cascade that includes a
head-to-head rule.

Implement a single function:

```python
def league_table(teams, matches):
    ...
```

## Inputs

- `teams`: a list of distinct team-name strings. This is the full set of teams;
  a team may have played zero matches.
- `matches`: a list of tuples `(home, away, home_goals, away_goals)` where
  `home` and `away` are team names (both present in `teams`, and `home != away`)
  and `home_goals`, `away_goals` are non-negative integers. Each tuple is one
  played match. Two teams may meet more than once; every listed match counts.

## Per-team aggregate stats

For each team, accumulate over all its matches (whether it played home or away):

- **points**: a win is worth `3`, a draw `1`, a loss `0`. A match is a win for
  the team if it scored strictly more goals than the opponent in that match, a
  draw if equal, a loss otherwise.
- **goals_for**: total goals the team scored.
- **goals_against**: total goals scored against the team.
- **goal_diff**: `goals_for - goals_against`.

A team with no matches has `points = 0`, `goals_for = 0`, `goals_against = 0`,
`goal_diff = 0`.

## Ordering (best team first)

Sort teams from best to worst using this cascade. Apply each rule in order; only
move to the next rule when the current one does not separate the two teams.

1. **Points**, higher is better.
2. **Goal difference**, higher is better.
3. **Goals for**, higher is better.
4. **Head-to-head points** between exactly the two teams being compared, higher
   is better (defined below).
5. **Team name**, ascending by ordinary string comparison (this is a total
   tie-break, so the final order is always fully determined and deterministic).

### Head-to-head points (rule 4)

The head-to-head comparison between two teams **A** and **B** looks *only* at the
matches played directly between A and B (in either home/away arrangement, and
counting every such match if they met multiple times). Compute each team's
points earned in *just those matches* (same 3/1/0 scheme). The team with more
head-to-head points is ranked higher. If they earned equal head-to-head points,
or if A and B never played each other, rule 4 does not separate them and you
proceed to rule 5.

Head-to-head is only ever evaluated **pairwise** between the two teams currently
being compared. Do not try to build a mini-league among three or more tied
teams — rule 4 is strictly a function of the two teams in the comparison.

## Return value

Return a list of dictionaries, one per team, in the computed order (best first).
Each dictionary has exactly these keys:

- `"team"`: the team name.
- `"points"`: int.
- `"goals_for"`: int.
- `"goals_against"`: int.
- `"goal_diff"`: int.

Every team in `teams` appears exactly once. Do not mutate the inputs. For an
empty `teams` list, return an empty list (regardless of `matches`).

## Worked examples

Example 1 — head-to-head decides a tie:

```python
teams = ["A", "B", "C"]
matches = [
    ("A", "B", 2, 0),   # A beats B
    ("B", "A", 1, 1),   # A vs B again, draw
    ("C", "A", 0, 3),   # A beats C
    ("C", "B", 0, 3),   # B beats C
]
league_table(teams, matches)
```

Aggregates:
- A: matches vs B (win 2-0, draw 1-1) and vs C (win 3-0). points = 3+1+3 = 7,
  goals_for = 2+1+3 = 6, goals_against = 0+1+0 = 1, goal_diff = 5.
- B: vs A (loss 0-2, draw 1-1) and vs C (win 3-0). points = 0+1+3 = 4,
  goals_for = 0+1+3 = 4, goals_against = 2+1+0 = 3, goal_diff = 1.
- C: two losses. points = 0, goals_for = 0, goals_against = 6, goal_diff = -6.

Order: A (7) > B (4) > C (0). Result:

```python
[
    {"team": "A", "points": 7, "goals_for": 6, "goals_against": 1, "goal_diff": 5},
    {"team": "B", "points": 4, "goals_for": 4, "goals_against": 3, "goal_diff": 1},
    {"team": "C", "points": 0, "goals_for": 0, "goals_against": 6, "goal_diff": -6},
]
```

Example 2 — points, goal diff, goals-for all tie; head-to-head breaks it:

```python
teams = ["X", "Y"]
matches = [
    ("X", "Y", 2, 1),   # X wins
    ("Y", "X", 1, 0),   # Y wins
]
league_table(teams, matches)
```

Both teams: 1 win + 1 loss = 3 points; X scored 2 total, conceded 2
(goal_diff 0, goals_for... let's check): X: 2 (home) + 0 (away) = 2 for, 1 + 1 =
2 against, diff 0. Y: 1 + 1 = 2 for, 2 + 0 = 2 against, diff 0. Points, goal_diff
and goals_for all equal. Head-to-head between X and Y across both their matches:
X earned 3 (win) + 0 (loss) = 3; Y earned 0 + 3 = 3 — also equal. So rule 4 does
not separate them, and rule 5 (name ascending) puts X before Y.

```python
[
    {"team": "X", "points": 3, "goals_for": 2, "goals_against": 2, "goal_diff": 0},
    {"team": "Y", "points": 3, "goals_for": 2, "goals_against": 2, "goal_diff": 0},
]
```

Example 3 — head-to-head overrides name order:

```python
teams = ["P", "Q"]
matches = [
    ("Q", "P", 0, 1),   # P beats Q
]
league_table(teams, matches)
```

P: 3 points, gf 1, ga 0, diff 1. Q: 0 points, gf 0, ga 1, diff -1. P is clearly
ahead on points, so P is first. (If instead they had equal points/diff/goals-for
but P won head-to-head, P would come before Q even though "P" < "Q" already; the
head-to-head rule only matters when it changes the order relative to name.)

## Constraints

- Python 3, standard library only.
- The function must be deterministic and total (the final order never depends on
  input list order because rule 5 fully breaks remaining ties).
- Up to a few hundred teams and a few thousand matches.
