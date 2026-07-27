# Chicken-Run v2 — 4080 Setup Runbook (do this while the banks build on the Mac)

*2026-07-10, rev-lane. Target: the gaming PC (RTX 4080, 16GB VRAM, Windows). Goal: by
the time the prereg seals, this box can start training within the hour. Nothing here
trains anything — setup and downloads only, safe to do before the seal.*

## Subject models (ratified DOE: two lineages, 7–9B class)

- **Primary: Qwen2.5-7B** — the patient with the answering-when-it-shouldn't disease
  (v2 measured its PFA ~13% vs gemma's 0). Apache 2.0. Download BOTH:
  - `Qwen/Qwen2.5-7B` (base) and `Qwen/Qwen2.5-7B-Instruct` (~15GB each)
- **Cross-subject (later, as operator finds candidates): Gemma-class 9B** — the
  stored-phantom patient (the 7/8-seeds live-citation misapplication specimen).

## Steps

1. **Windows + driver:** update the NVIDIA driver (Game Ready or Studio, current).
   Reboot. `nvidia-smi` must show the 4080 and CUDA 12.x.
2. **Disk:** ≥ 100GB free on a fast drive (checkpoints + LoRA runs + merged outputs).
3. **Python env (WSL2 Ubuntu strongly preferred over native Windows for training):**
   - `wsl --install` if not present; inside WSL: Python 3.11, `python -m venv cr`
   - `pip install "unsloth[cu121] @ git+https://github.com/unslothai/unsloth"` —
     unsloth is the QLoRA path that comfortably fits 7B training in 16GB. Fallback
     stack if unsloth fights the box: `pip install torch transformers peft trl
     bitsandbytes datasets accelerate`.
4. **Hugging Face:** `pip install huggingface_hub`, `hf auth login` (free account),
   then pre-download: `hf download Qwen/Qwen2.5-7B` and `hf download
   Qwen/Qwen2.5-7B-Instruct`. This is the multi-hour part — start it early.
5. **Ollama on the 4080 (for smoke only):** install, `ollama pull qwen2.5:7b` — lets
   the box sanity-check GGUF conversions locally later.
6. **llama.cpp for GGUF conversion** (tuned LoRA → merged → GGUF → Ollama):
   `git clone https://github.com/ggerganov/llama.cpp && make` (in WSL), and
   `pip install gguf`.
7. **Smoke test (proves the whole path without touching study data):** run any
   unsloth 60-second QLoRA example on Qwen2.5-7B with 10 dummy rows, merge, convert
   to GGUF, load in Ollama, get one completion. If that round-trips, the box is ready.

## Instrument-identity rules (so the study stays clean)

- **Evaluation happens on the Mac's Ollama** with pinned GGUF hashes — before AND
  after models measured on the SAME instrument. The 4080 trains; it does not grade.
- Every checkpoint that leaves the 4080 travels with its sha256 and its training-config
  hash (the one-sealed-object rule extends to weights).
- No study data (banks, exemplars) goes to the 4080 until the prereg seals — the box
  gets the training split only, hash-verified against the seal at HEAD (scrub's
  payload-not-transport rule, applied to the optimizer's input).

## What the operator decides before the seal (nothing else blocks)

1. **λ (the wrong-answer penalty)** — sets break-even confidence λ/(1+λ) AND the
   certification cost ratio (one sealed quantity, REV #020 A1). λ=3 → 75% is the
   discussed default.
2. Subject confirmation: Qwen2.5-7B primary (recommended, above).
