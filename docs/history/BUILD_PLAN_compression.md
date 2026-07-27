# Build Plan — RAM/quality compression, gated by the MSAI gauge

*Synthesis from the compression session's 19-agent swarm (12 assumptions stress-tested).
Captured here so the plan survives independent of that session. Pairs with
`HANDOFF_compression-gauge.md` (how to run `compare()`); this is what to build and in
what order. Every expensive step is gated behind a cheap one.*

## Headline

Both frontier ideas survived — **but not in the form they were pitched.** The skeptics
killed the naive versions and found stronger ones sitting right next door. The
cross-domain analogies (residual coding, noise shaping) were directionally right; the
literature already had sharper forms of both.

## The two big corrections (the real value)

**① Delta-KV: the adjacent-token / Donkey-Kong-BRR framing is dead.**
AQUA-KV explicitly tested predict-from-previous-token and found ~zero predictive power;
DeltaKV showed >60% of similar tokens are 16+ positions away. The BRR analogy pointed at
the right *principle* (store the residual, not the value) but the wrong *axis*. **The win
is inter-layer prediction** — predict layer L's K/V from layer L−1's *reconstructed* K/V
at the same token position. ~2–2.5 bits/value at <1% perplexity loss, no training, no
retrieval. The sequence axis was a trap; the **layer axis is the gold.**

**② Dither-2bit: dither-as-the-lever is dead** (four independent verdicts).
Stochastic rounding is a *training* trick with no averaging horizon at one-shot
quantization — at 2-bit it's swamped by the 4-level grid. The real lever is the
**Hadamard incoherence rotation** (from QuIP#) plus GPTQ's *existing* Hessian
error-feedback, which already *is* the proven noise-shaper. And the honest reality:
uniform 2-bit cannot reach Q4 quality (best-known 2-bit ≈ 6.66 ppl vs Q4's 5.56). So it
**retargets to 3-bit (W3)**, which realistically passes the gauge for listings.

## The plan, in order — every expensive step gated behind a cheap one

| # | Do | Gate to pass before next | Effort |
|---|----|----|----|
| **1** | **Shakedown (runnable now).** One env (`pip install -e msai-eval` + `mlx mlx-lm`), freeze 20-photo manifest, 5-judge panel, run off-the-shelf {fp16, q8, q4, q2, q8-KV, +1 broken sentinel} through `reliability()` → `compare()`. | Gauge QUALIFIED (finite guard band — not frozen + balanced replicates; ndc is advisory only, NOT a gate — it is selection-sensitive on hand-picked configs) **and** q2+sentinel read "REAL drop" while q4 reads "within noise." If q2 doesn't separate, **stop and fix the gauge** before building anything. | 1–2 days |
| **2** | **Delta-KV day-1 kill-test (numpy, no kernel).** Dump real Qwen2.5-7B K/V; measure residual-vs-raw entropy across 3 axes: adjacent (control), inter-layer, strided-8/16. | Inter-layer or strided beats raw by >1.3× variance reduction. If not, **delta-KV is dead — stop.** | 0.5–1 day |
| **3** | Build inter-layer `DeltaKVCache` in pure MLX (dequant-to-fp16 path); compare {fp16, q4kv, deltaKV-inter-4bit/3bit}. | ≥1 config "within noise" vs fp16 **and resolvably better than KIVI-q4kv**. If it only ties q4kv, shelve it. | 3–5 days |
| **4** | Dither-2bit retargeted: pre-check an existing **VPTQ-2bit** checkpoint through `compare()` first; then fork GPTQModel + Hadamard + Fisher placement; compare W3/W2 arms (+ dither as control). | A W3 (or W2+Hadamard) arm lands "within noise" or beats mlx-q4; `dither_control` reads "no gain" as predicted. | 4–6 days |
| **5** | Faithful-packing check: round-trip the survivor through real MLX `QuantizedLinear`. | Packed artifact reproduces the fp16-proxy verdict (greedy-token match). | 1–2 days |
| **6** | **Kernel / speed — only for a validated survivor.** Fused Metal kernel (delta-KV) / near-zero (dither reuses affine matmul). | Kernel matches reference on `compare()` **and** ≥95% of fp16 tok/s. Abandon any kernel that can't beat plain fp16. | 2–4 wks each |

**Go/no-go on the whole delta-KV program lands in week one, for under two days of numpy.**
That's the decoupling working as designed.

## Stack verdict

**MLX on the 64GB M2 Ultra — single stack for prototype *and* deploy**, `msai-eval` in the
same env, the RTX 4080 demoted to **judge-host only.** Why it's clean:
- a custom KV cache is a `_BaseCache` subclass;
- a custom quant is **offline numpy** writing into `QuantizedLinear` — so the **entire
  quality phase needs zero kernel work**;
- the affine grid MLX accelerates is the *same* grid dither-2bit must stay on, so design
  and runtime agree.
- Tooling reality the swarm caught: neither `msai_eval` nor `mlx` imports from the default
  `python3` today — **step 0 is literally making one env.**

## The honest gut-check (hear this before spending a day)

There's a real chance **neither frontier config earns its complexity** — KIVI-4bit KV and
MLX-q4 weights are already <1% from fp16, so `compare()` may rank them and the fancy
schemes *both* "within noise" with no resolvable gap. The plan front-loads cheap checks
that would tell us to stop: the **day-1 numpy test** for delta-KV, and **"run VPTQ-2bit
through `compare()` first"** for dither (if SOTA vector-quant 2-bit fails the judge, no
scalar scheme will pass). **Proving the frontier isn't worth building — cheaply, in week
one — is a win, not a failure.** That's the gauge doing its job.

## Crossed off the bench (and why)

- **GGUF as the prototype lab** — its IQ2/Q2_K requantizes scales, so the fp16 proxy would
  *lie* about quality.
- **A CUDA port on the 4080** — no Metal→CUDA kernel reuse, and 16GB is too tight for the
  long-context regime where KV compression even pays.
- **Reading `%GRR`/`ndc` as the grade** — selection-sensitive on hand-picked configs; which
  is exactly why `compare()` exists.

## The hard rule baked into all of it

**Validate quality with a slow numpy reference through the gauge first; build the fast
kernel only if it survives.** You never sink kernel time into a scheme that doesn't hold
quality. The gauge (`reliability()` → `compare()`) gates every step.

— captured by the MSAI session as backstop; original synthesis by the compression
session's 19-agent swarm.
