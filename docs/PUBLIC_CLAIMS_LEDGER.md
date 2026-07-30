# Public claims ledger — every number on the results site, and where its receipt lives

*Generated from an adversarial audit of the published results page
(https://dellsbells.github.io/msai-results/) against this repository. Statuses:
**RECEIPTED** — the exact number appears in (or recomputes byte-for-byte from) a committed
artifact here. **PARTIAL** — derivable from committed artifacts, not printed verbatim.
**MISSING** — the artifact lives outside this repo; the site marks these two numbers with
a dagger (&#8224;) and says so. Claims are not receipts; this table is the map between them.*

Two identities anchor the chain:
- Certificate ID `MSAI-3E19DD3B0061` **is** the sha256 prefix of
  `benchmark/oracle_run/oracle_study_scores.json` — recompute it yourself.
- The prereg seal `19bdfc44…14cd5` **is** the sha256 of `docs/CODE_ORACLE_PREREG.md`,
  sealed before any candidate solution existed.

| claim (as shown on the site) | status | receipt |
|---|---|---|
| Cert ID MSAI-3E19DD3B0061 IS the sha256 of oracle_study_scores.json (site: '$ shasum -a 256 oracle_study_scores.json / 3E19DD3B0061… ← the certificate number IS this hash') | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json (+ cert header benchmark/oracle_run/CERTIFICATE_MSAI-3E19DD3B0061.md)` |
| 'prereg sealed before any solution existed' — seal hash 19bdfc44…14cd5 | RECEIPTED | `docs/CODE_ORACLE_PREREG.md` |
| 92% / 91.7% — panel sign agreement, '33 of 36 resolvable pairs' | RECEIPTED | `benchmark/oracle_run/analysis_results.json → H1: {agree: 33, n: 36, rate: 0.9167, jeffreys95: [0.794, 0.976], frozen_prediction: '>=0.90', pass: true}` |
| Consensus-wrong rate 6.8%, interval [2.0%, 17.1%] | RECEIPTED | `benchmark/oracle_run/analysis_results.json → H3.pooled: {consensus_wrong: 3, n: 44, rate: 0.0682, jeffreys95: [0.0196, 0.1709]}` |
| En / conformance dial values 45.7, 23.9, 13.0 (LFM2 46%, gemma4 24%, minicpm 13%) | RECEIPTED | `benchmark/oracle_run/analysis_results.json → H4 conformance_rate: LFM2 0.457, gemma4:12b 0.239, minicpm-v:latest 0.130` |
| minicpm-v histogram [1,10,49,202,9] — '202 of 271 answers were the same "4"' | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json` |
| LFM2 histogram [20,45,39,63,109] (SVG wave, not a printed array) | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json` |
| gemma4 histogram [34,145,12,16,60] (SVG wave) | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json` |
| '828 real ratings' / '828 ratings' | RECEIPTED | `benchmark/oracle_run/analysis_results.json → ingest.rows: 828; CERTIFICATE_MSAI-3E19DD3B0061.md §7 denominator map row '828 ratings / all (task, config, judge, rep) rows'` |
| The three judge-fingerprint waves depict 'All 828 real ratings' | PARTIAL | `benchmark/oracle_run/analysis_results.json → ingest.nulls_excluded_disclosed: 14` |
| '44 pairs · 3 shared misses' (chart tile subtitle) | PARTIAL | `benchmark/oracle_run/analysis_results.json → H3 events: t01 shared=false, t35 shared=true, t48 shared=true` |
| Uncertainty budget between-judge shares 44.2 / 49.8 / 48.5 % (resolve / subtle / tie) | RECEIPTED | `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md §4` |
| Budget repeatability/quantization shares 37.1/18.7, 33.0/17.2, 30.1/21.4 % | PARTIAL | `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md §4 (u components: resolve 0.408/0.445/0.289; subtle 0.400/0.492/0.289; tie 0.342/0.434/0.289)` |
| Panel noise band U ≈ 2.5 on a 4-point scale ('±2.5 of a 4-point scale') | RECEIPTED | `benchmark/oracle_run/analysis_results.json → tiers.resolve.resolution_verdict.U: 2.502615` |
| Measured gaps Δ +1.10 (big), +0.78 (subtle), −0.17 (tie), all inside the band | RECEIPTED | `benchmark/oracle_run/analysis_results.json → tiers.*.delta: 1.1034, 0.7778, −0.1667` |
| Verdicts 'BELOW · BELOW · WITHIN-NOISE'; panel FAILED qualification | RECEIPTED | `benchmark/oracle_run/analysis_results.json → resolution_verdict.state per tier: BELOW, BELOW, WITHIN-NOISE` |
| By-part chart: all ten oracle gaps (t01 1.00, t35 .67, t48 −.06, t10 1.00, t33 0, t34 .82, t26 −.50, t45 0, t05 .25, t25 .42) | RECEIPTED | `benchmark/oracle_run/study_manifest.json → tasks[*].g` |
| By-part chart: all ten panel deltas (−.04, −.17, .11, .31, −.22, .56, −.03, .14, .17, .45), declared as 'panel_norm/4' | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json` |
| 't33, where it invented a 0.9-point winner on a true tie' | RECEIPTED | `benchmark/oracle_run/oracle_study_scores.json + study_manifest.json (t33 g=0.0, tier=tie)` |
| 'Ten tasks from the attended review' | PARTIAL | `benchmark/oracle_run/ATTENDED_REVIEW_PACK.md line 8` |
| Waffle chart 'resolve · 2/36' and 'subtle · 1/8' | RECEIPTED | `benchmark/oracle_run/analysis_results.json → H3.resolve {consensus_wrong: 2, n: 36}, H3.subtle {consensus_wrong: 1, n: 8}` |
| minicpm 'answered "4" on 73% of its 276 ratings' | RECEIPTED | `CERTIFICATE_MSAI-3E19DD3B0061.md §1 and §7 denominator map ('276 ratings / minicpm's rows (73% constant-4 denominator)')` |
| Act I: '900 blind ratings, $2.23' on a 5-lineage frontier panel | RECEIPTED | `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md (header '900 blind ratings'; line 128 '$2.23 total measurement cost')` |
| Act I verdicts: RESOLVED (obvious gap) / AT-EDGE (subtle) / BELOW (tie) | RECEIPTED | `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md §3 verdict table` |
| '55 coding tasks with hidden test suites' | RECEIPTED | `benchmark/oracle_corpus/CORPUS_MANIFEST.md line 8 ('Ledger-PASS (feed oracle): 55')` |
| S7: 'zero wrong bindings in 512 attempts' (0/512) | RECEIPTED | `benchmark/entropy_arm/v2_rows_rescored.jsonl` |
| S7: 'false abstentions: 2/512' | RECEIPTED | `benchmark/entropy_arm/v2_results.json → classes.FALSE_ABSTENTION: 2; cells PFR_supported 1/128 + 1/128 + 0/128 + 0/128` |
| Hallucination arc bar 3: 'Evidence + abstain button ~3%' fabricated share | PARTIAL | `benchmark/entropy_arm/v2_results.json (classes: FABRICATED_ANSWER 22, n_rows 768) / v2_rows_rescored.jsonl (17 of 768)` |
| Hallucination arc bar 1: 'From memory recall alone ~100%' fabricated | RECEIPTED | `benchmark/entropy_arm/entropy_pilot_results.json → per_model correct: 0 for both qwen2.5vl:7b and gemma4:12b (wrong 25 and 73)` |
| Hallucination arc bar 2: 'Grounded prose evidence, no exit ~51%' | MISSING | `— none found —` |
| S5 PHANTOM-KNOB: '87% noise, 13% stored phantoms' over R=3 seeded reps | MISSING | `— none found —` |
| '7 studies run · 3 certificates issued · 1 flagship sealed & staged' | PARTIAL | `docs/TRANSFER_LEDGER.md:26 ('3 certificates; 2 seals surviving crashes'); docs/TRANSFER_LEDGER.md:30 ('cert #3 omits ndc entirely'); benchmark/chicken_run/CHICKEN_RUN_PREREG.md` |
| S2: '18/20 blind agreement' across rival AI lineages | RECEIPTED | `docs/ONE_THESIS.md:100 ('18/20 exact between-lineage agreement, identical 16/20 strict totals')` |
| S3: '~80% of false findings refused' on real calibration records | RECEIPTED | `docs/ONE_THESIS.md:91 ('killed roughly 80% of the drift findings the naive analysis emitted'); docs/ADAPTER_DESIGN_NOTES.md:28` |
| 'What's next' scoring economy: +1 correct, −3 wrong, 0 honest refusal | RECEIPTED | `benchmark/chicken_run/CHICKEN_RUN_PREREG.md §3 lines 49–50 ('correct +1 · wrong −λ · abstain 0 … default λ=3 → break-even confidence λ/(1+λ) = 75%')` |
| M8: 'ndc … failed its audition on AI judges and was demoted to advisory' | RECEIPTED | `docs/TRANSFER_LEDGER.md:30 (row 13, verdict 'DEMOTED (evidence-driven)')` |
| M2: between-judge disagreement is '~half the variance in every study' / 'dominant lever in every tier' | RECEIPTED | `benchmark/CERTIFICATE_MSAI-8C06733F42F0.md §4 (44.2%, 49.8%, 48.5% of u_c² — reproducibility named dominant lever in all three tiers)` |

## Amendments — post-CDX #013 (cross-lineage adversarial review, 2026-07-28)

Codex's publish-gate review (verdict: FAIL for RC1, fixes enumerated) drove these
changes; rows above are preserved as generated, corrections recorded here append-only:

1. **By-part chart values corrected on the site.** Three of ten plotted panel deltas
   (t01, t10, t25) were computed with a pooled-mean draft method instead of the
   pipeline's per-judge-mean method and drifted from the committed analysis. All ten
   now recompute exactly from `oracle_study_scores.json` via the per-judge method and
   match the H3 event anchors in `analysis_results.json` (e.g. t01 = −0.056 raw).
2. **Entropy v2 aggregate regenerated from rescored rows.** The committed
   `v2_results.json` predated the bracket-artifact rescore (msai-eval 3c6271b): it
   carried FABRICATED_ANSWER = 22 (5 were scorer artifacts) and the dead P2 AUC 0.844.
   Now: FABRICATED = 17, `pooled.fab_on_supported = 0/512` and
   `pooled.false_abstention_supported = 2/512` are direct public receipts for the site's
   claims, and both AUCs are explicitly UNMEASURABLE with notes. Site bar updated ~3% → ~2%.
3. **Certificate 3 wording corrected (Revision R1, appended to the certificate):**
   "statistically real differences on every tier" overstated the tie tier
   (`tiers.tie.sig: false` — the correct reading of a true tie). No number changed.
4. **Site overclaims reworded:** "Every number checkable" → "Receipts published for
   every headline number" (two † numbers and the withheld bank make "every" false);
   "flagship sealed & staged" / "Now running … sealed before training" → prereg
   drafted, seal pending; "the exit did the work" causal phrasing → correlational,
   with the no-chute ablation named as the next preregistered study.
5. **Second legacy stratum removed:** internal fine-tune (resale-vlm) result files and
   Open Beauty Facts / commercial-UPC-API record-level artifacts (`phase4_*`,
   `tier2_result.json`, `real_lever_result.json`, `stageA_validation.py`) — sources
   are still named and credited in `VALIDATION.md` prose; records are not redistributed.
