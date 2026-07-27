# External reviews — record & provenance

*Preserved audit trail of cross-lineage reviews of the MSAI work. Provenance is labeled:
**[verbatim, this session]** = held verbatim in the gauge lane's transcript; **[logged summary]** =
only a summary reached this lane (verbatim held in another lane or the KB). Nothing here is
reconstructed as fake verbatim — where the exact words are not held, that is stated.*

## Standing conflict-of-interest disclosure

The Anthropic model that reviews this work ("Fable" / Claude, `claude-opus-4-8`) is **also a judge
in the frontier panel**. Its reviews of the panel therefore carry a conflict of interest — disclosed
here and to be repeated on any external publication. The structural mitigation is cross-lineage
diversity: the panel also runs Gemini, Grok, DeepSeek, and GPT; the module audit ran Gemma, Qwen, and
Liquid (LFM2). Agreement *across* independent lineages is the evidence; agreement *within* one is not.

## 1. Fable / Claude (in-panel — see COI above)

**Metric adjudication — the four-state decision** — [verbatim, this session]. Fable's ruling on the
resolution metric: adopt a four-state verdict (WITHIN-NOISE / BELOW / AT-EDGE / RESOLVED) where the edge
zone is U's own confidence interval derived from the Welch-Satterthwaite effective dof, not an ad-hoc
margin; run the metric change *before* adding DeepSeek (so a 5th judge doesn't just re-roll a binary
threshold); treat the definitional-uncertainty reading as a **finding, not a concession**; log the
tie-tier pre-registration deviation and the honest cell-refill (real re-calls, not imputation). The
gauge lane implemented it and ratified **WS νeff** for the contract with a provisional-J<5 flag. *(Full
text in the gauge lane transcript, 2026-07-02.)*

**Certificate assessment** — [verbatim, this session]. Reviewed `certificate.py` as presentation-layer
only over the validated `compare()`+`four_state()` path; and flagged the "world's first / turns MSAI into
an audit practice / the pitch deck" framing in the pivot brief as **running ahead of a pilot**. The gauge
lane concurred and kept the caveat with the claim (pilot-scale, precision-only until the thunderclap run
on a real safety eval).

**Thunderclap manners** — [logged summary, from `MANIFEST.md`]. Public pre-registration of predictions and
the band-edge rule before scoring; notify eval owners before publication; self-caveats louder than the
target eval's own; the "a safety case is theater if the noise floor is wider than the threshold it gates
on" line used as a warning, not a taunt.

## 2. Gemini — [logged summary]

Read of the MSAI safety framing, **with the correction the gauge lane logged**: *MSAI catches
**irreproducibility, not deception**; shared bias passes by construction* — a panel that agrees *wrongly*
reads steady, so precision is not accuracy, and the accuracy anchor (a judge-independent reference) is the
named successor, not a solved problem. Verbatim text not held in this lane.

## 3. Earlier module-audit reviews — [see VALIDATION.md §2–§3]

Gemma, Qwen, and Liquid (LFM2) independently reviewed the modules and agreed the "measurement standard for
AI safety" framing overclaimed (now the README's "What this is NOT"); they split on an ICC-denominator /
Krippendorff-ordinal formula question, which was settled by **published reference values** (Shrout-Fleiss
0.290, Krippendorff 0.815) — not by majority vote. The full record and that adjudication are in
`VALIDATION.md` §2–§3 and the strict-xfail ledgers.

---

*House rule: the caveat travels with the claim, and a reviewer who is in the panel discloses it.*
