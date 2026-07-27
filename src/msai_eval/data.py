"""Input normalization for msai_eval.

Accepts the messy shapes real LLM-as-judge data comes in and produces one
canonical internal structure. The whole point of msai_eval is honesty about what
your measurement system can support, so this module is deliberately explicit
about what is missing, unbalanced, or degenerate rather than silently coercing.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Sequence
import numpy as np


@dataclass
class Dataset:
    items: list                      # ordered item ids (the "parts")
    judges: list                     # ordered judge ids (the "appraisers")
    # rater x unit matrix (judges x items) of cell means, np.nan where missing.
    # This orientation matches Krippendorff reliability data.
    matrix: np.ndarray
    # cube[item, judge] -> list of trial scores (variable length, may be empty)
    cells: list                      # list[list[list[float]]] indexed [i][j]
    n_trials_max: int
    complete: bool                   # every item judged by every judge at least once
    balanced_replicates: bool        # every cell has the same trial count >= 2
    flags: list = field(default_factory=list)
    label_map: dict = field(default_factory=dict)   # string nominal label -> numeric code (empty if numeric)

    @property
    def n_items(self) -> int:
        return len(self.items)

    @property
    def n_judges(self) -> int:
        return len(self.judges)


def _label_key(v):
    """Canonical key for a nominal category, so '1', 1, and 1.0 collapse to ONE category and a string
    reference '1' matches a numeric label 1 (the digit-string-label bug the review caught). EDGE: two
    distinct numeric-looking string labels that equal the same float ('1' and '1.0', '1e5' and '100000')
    merge — intended numeric canonicalization; use non-numeric labels if you need them kept distinct."""
    try:
        return repr(float(v))      # numeric or numeric-string -> canonical "1.0"
    except (TypeError, ValueError):
        return str(v)              # genuine string label -> as-is


def _from_records(records: Sequence[dict], level=None, label_map=None) -> tuple[list, list, dict, dict]:
    items, judges = [], []
    seen_i, seen_j = set(), set()
    cell_map: dict[tuple, list] = {}
    label_map = {} if label_map is None else label_map   # nominal category -> stable numeric code
    is_nominal = (level == "nominal")

    def _code(v):
        kk = _label_key(v)
        if kk not in label_map:
            label_map[kk] = float(len(label_map))
        return label_map[kk]

    for r in records:
        it = r["item"]
        jg = r["judge"]
        raw = r["score"]
        try:
            _fv = float(raw)
        except (TypeError, ValueError):
            _fv = None
        if _fv is not None and _fv != _fv:      # NaN: never a nominal category, never a numeric-matrix poison (REV-008)
            raise ValueError(
                f"NaN score at item={it!r} judge={jg!r}: NaN is not a valid score or category. Omit missing "
                f"(item, judge) cells from the records — a missing cell is handled by the crossed design — "
                f"rather than passing NaN.")
        if is_nominal:
            sc = _code(raw)        # NOMINAL: every value is a category code (string OR numeric)
        else:
            try:
                sc = float(raw)
            except (TypeError, ValueError):
                raise ValueError(
                    f"non-numeric score {raw!r} for item={it!r} judge={jg!r}. Scores must be numeric "
                    f"for level='ordinal'/'interval'; use level='nominal' for category labels."
                ) from None
        if it not in seen_i:
            seen_i.add(it); items.append(it)
        if jg not in seen_j:
            seen_j.add(jg); judges.append(jg)
        cell_map.setdefault((it, jg), []).append(sc)
    return items, judges, cell_map, label_map


def normalize(data: Any, level=None) -> Dataset:
    """Turn user input into a Dataset. `level='nominal'` encodes category labels (string OR numeric)
    to stable codes; other levels require numeric scores.

    Supported inputs:
      * list of dicts with keys item, judge, score  (trial optional, ignored for keying)
      * pandas DataFrame with columns item, judge, score
      * dict {item_id: {judge_id: score_or_list_of_scores}}
      * 2D array-like (items x judges), one score per cell, single trial
      * a Dataset (returned as-is) — lets a caller that already normalized reuse it
    """
    if isinstance(data, Dataset):          # already normalized -> passthrough (skip the recompute)
        return data
    if data is None or (isinstance(data, (list, tuple, dict)) and len(data) == 0):
        raise ValueError("no data: need at least one item/judge/score record.")

    # pandas DataFrame -> records
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        cols = {c.lower(): c for c in data.columns}
        need = {"item", "judge", "score"}
        if not need.issubset(cols):
            raise ValueError(f"DataFrame must have columns {need}; got {list(data.columns)}")
        records = [
            {"item": row[cols["item"]], "judge": row[cols["judge"]], "score": row[cols["score"]]}
            for _, row in data.iterrows()
        ]
        items, judges, cell_map, label_map = _from_records(records, level=level)

    elif isinstance(data, dict):
        records = []
        for it, jmap in data.items():
            for jg, sc in jmap.items():
                if isinstance(sc, (list, tuple, np.ndarray)):
                    for s in sc:
                        records.append({"item": it, "judge": jg, "score": s})
                else:
                    records.append({"item": it, "judge": jg, "score": sc})
        items, judges, cell_map, label_map = _from_records(records, level=level)

    elif isinstance(data, (list, tuple)) and len(data) and isinstance(data[0], dict):
        items, judges, cell_map, label_map = _from_records(data, level=level)

    else:  # assume 2D array-like items x judges
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 2:
            raise ValueError("Array input must be 2D (items x judges).")
        items = list(range(arr.shape[0]))
        judges = list(range(arr.shape[1]))
        cell_map = {}
        label_map = {}                       # numeric array -> no string labels
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if not np.isnan(arr[i, j]):
                    cell_map[(items[i], judges[j])] = [float(arr[i, j])]

    n_i, n_j = len(items), len(judges)
    if n_i == 0 or n_j == 0:
        raise ValueError(
            "no data: need at least one item/judge/score record. "
            "Check that your input is non-empty and has the expected columns."
        )
    ii = {it: i for i, it in enumerate(items)}
    jj = {jg: j for j, jg in enumerate(judges)}

    cells = [[[] for _ in range(n_j)] for _ in range(n_i)]
    for (it, jg), scs in cell_map.items():
        cells[ii[it]][jj[jg]].extend(scs)

    matrix = np.full((n_j, n_i), np.nan)   # judges x items
    for i in range(n_i):
        for j in range(n_j):
            if cells[i][j]:
                matrix[j, i] = float(np.mean(cells[i][j]))

    trial_counts = [len(cells[i][j]) for i in range(n_i) for j in range(n_j)]
    n_trials_max = max(trial_counts) if trial_counts else 0
    complete = all(len(cells[i][j]) >= 1 for i in range(n_i) for j in range(n_j))
    nonzero = [c for c in trial_counts if c > 0]
    balanced_replicates = (
        complete and len(set(nonzero)) == 1 and (nonzero[0] >= 2 if nonzero else False)
    )

    flags = []
    if n_j < 2:
        flags.append("single_judge: reproducibility (between-judge agreement) cannot be measured with one judge.")
    if n_i < 10:
        flags.append(f"few_items (n={n_i}): agreement estimates and their confidence intervals will be wide and unstable.")
    if not complete:
        flags.append("incomplete_matrix: some item-judge pairs are missing; ICC and variance components use complete cases / are skipped. Krippendorff alpha still applies.")
    if n_trials_max >= 2 and not balanced_replicates:
        flags.append("unbalanced_replicates: trial counts differ across cells; full Gage R&R needs a balanced design. Reporting agreement stats instead.")

    return Dataset(items=items, judges=judges, matrix=matrix, cells=cells,
                   n_trials_max=n_trials_max, complete=complete,
                   balanced_replicates=balanced_replicates, flags=flags, label_map=label_map)


def safe_print(text: str) -> None:
    """Print, surviving a non-UTF-8 console (Windows cp1252) — the summaries contain Δ/σ/×/→ and
    must never raise UnicodeEncodeError just from being displayed."""
    try:
        print(text)
    except UnicodeEncodeError:
        import sys
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(enc, "replace").decode(enc))
