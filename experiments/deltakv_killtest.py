"""BUILD_PLAN Step 2 — delta-KV entropy kill-test (pure numpy, no gauge).

Dump real Qwen2.5-7B K/V from one forward pass over a real context, then ask: does RESIDUAL
coding beat storing raw values, i.e. is the residual lower-variance (so it quantizes to fewer
bits at the same fidelity)? Across three axes:

  adjacent    V[t] - V[t-1]            control the swarm 'killed'; expected to fail for V (RoPE)
  strided-8   V[t] - V[t-8]            anchor-token style (CacheGen)
  inter-layer V[L] - V[L-1]            THE swarm hypothesis (predict layer L from L-1)

TWO metrics, because they answer different questions:
  POOLED      var(all raw) / var(all residual). OPTIMISTIC — conflates cross-channel scale,
              which per-channel/group affine quant already removes for free. Overstates delta.
  PER-CHANNEL geometric mean over (head,dim) channels of var(raw_c)/var(residual_c). HONEST —
              controls for what affine quant already captures; this is the INCREMENTAL benefit
              of delta coding over plain q4-KV.

GATE (affine-controlled): the best honest axis must beat raw by >1.3x, else delta-KV is dead
and we STOP before building any kernel (BUILD_PLAN Step 3).

    .venv/bin/python experiments/deltakv_killtest.py
"""
import json
import numpy as np
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

MODEL = "mlx-community/Qwen2.5-7B-Instruct-bf16"

CONTEXT = """Reselling has quietly become one of the most resilient corners of the
consumer economy. A single seller working from a spare bedroom can photograph a vintage
film camera in the morning, write a careful description noting the light seals and a small
dent on the baseplate, and have it listed across three marketplaces by lunch. What used to
require a storefront and a wholesale account now runs on a phone, a ring light, and a
willingness to answer buyer questions honestly. The economics reward patience: a lens that
sits unsold for six weeks at a stubborn price will often clear in two days once the seller
relists it with sharper photos and a title that names the mount and the era. Condition notes
matter more than adjectives. Buyers forgive a scratch they were warned about and punish a
surprise with a return. The sellers who last are the ones who treat disclosure as a feature,
not a liability, building a reputation that compounds across thousands of small transactions.
Shipping is its own discipline. A fragile vase double-boxed with two inches of crumpled paper
on every side arrives intact; the same vase wrapped in a single layer of bubble wrap arrives
in pieces and erases the margin twice over. The quiet truth of the trade is that the boring
parts, packing, measuring, replying within the hour, are exactly the parts that separate a
hobby from an income."""


def grab(c, attr):
    arr = getattr(c, attr)
    off = getattr(c, "offset", arr.shape[2])
    sliced = arr[:, :, :off, :].astype(mx.float32)   # numpy can't read mlx bf16 buffers
    mx.eval(sliced)
    return np.array(sliced)[0]  # [H, S, D]


def pooled(tensors, name):
    raw_var = float(np.concatenate([t.reshape(-1) for t in tensors]).var())
    adj   = np.concatenate([(t[:, 1:, :] - t[:, :-1, :]).reshape(-1) for t in tensors]).var()
    s8    = np.concatenate([(t[:, 8:, :] - t[:, :-8, :]).reshape(-1) for t in tensors if t.shape[1] > 8]).var()
    inter = np.concatenate([(tensors[l] - tensors[l - 1]).reshape(-1) for l in range(1, len(tensors))]).var()
    res_scaled = []
    for l in range(1, len(tensors)):
        a, b = tensors[l].reshape(-1), tensors[l - 1].reshape(-1)
        alpha = float(np.dot(a, b) / (np.dot(b, b) + 1e-8))
        res_scaled.append(a - alpha * b)
    inter_a = np.concatenate(res_scaled).var()
    r = lambda v: raw_var / (float(v) + 1e-12)
    out = {"adjacent": r(adj), "strided8": r(s8), "inter_layer": r(inter), "inter_layer_scaled": r(inter_a)}
    print(f"  {name}: adjacent {out['adjacent']:.2f}x  strided-8 {out['strided8']:.2f}x  "
          f"inter-layer {out['inter_layer']:.2f}x (scaled {out['inter_layer_scaled']:.2f}x)   [raw_var={raw_var:.3f}]")
    return out


def per_channel(tensors, lag):
    """Geometric mean over (head,dim) channels of var(raw_c)/var(lag-residual_c).
    Per-channel => controls for cross-channel scale and constant offsets that per-channel
    affine quant already removes. This is the INCREMENTAL benefit of delta over plain q4-KV."""
    ratios = []
    for t in tensors:                     # [H, S, D]
        if t.shape[1] <= lag:
            continue
        raw_v = t.var(axis=1)             # [H, D]  variance over positions, per channel
        res_v = (t[:, lag:, :] - t[:, :-lag, :]).var(axis=1)
        m = raw_v > 1e-6
        ratios.append(raw_v[m] / (res_v[m] + 1e-12))
    allr = np.concatenate([r.reshape(-1) for r in ratios])
    return float(np.exp(np.mean(np.log(allr + 1e-12))))   # geometric mean


def per_channel_interlayer(tensors):
    """The ACTUAL AQUA-KV hypothesis: per-channel learned scale V[L,c] ~= a_c * V[L-1,c]
    (affine already handles the per-channel offset, so scale-only is the fair predictor).
    Geomean over (layer-pair, head, dim) of var(raw_c) / var(residual_c)."""
    ratios = []
    for l in range(1, len(tensors)):
        cur = tensors[l].transpose(0, 2, 1).reshape(-1, tensors[l].shape[1])      # [H*D, S]
        prev = tensors[l - 1].transpose(0, 2, 1).reshape(-1, tensors[l - 1].shape[1])
        a = ((cur * prev).sum(1) / ((prev * prev).sum(1) + 1e-8))[:, None]
        res = cur - a * prev
        raw_v, res_v = cur.var(1), res.var(1) + 1e-12
        m = raw_v > 1e-6
        ratios.append(raw_v[m] / res_v[m])
    allr = np.concatenate(ratios)
    return float(np.exp(np.mean(np.log(allr + 1e-12))))


def main():
    print(f"loading {MODEL} ...")
    model, tok = load(MODEL)
    ids = tok.encode(CONTEXT)
    cache = make_prompt_cache(model)
    mx.eval(model(mx.array(ids)[None], cache=cache))
    Ks = [grab(c, "keys") for c in cache]
    Vs = [grab(c, "values") for c in cache]
    print(f"context tokens={len(ids)}  layers={len(Vs)}  per-layer (H,S,D)={Vs[0].shape}")

    print("\nPOOLED reduction (optimistic — conflates cross-channel scale affine already handles):")
    Vp = pooled(Vs, "V (no RoPE)  ")
    Kp = pooled(Ks, "K (post-RoPE)")

    print("\nPER-CHANNEL geomean reduction (HONEST — affine-controlled, incremental over q4-KV):")
    pc = {"V_adjacent": per_channel(Vs, 1), "V_strided8": per_channel(Vs, 8),
          "K_adjacent": per_channel(Ks, 1), "K_strided8": per_channel(Ks, 8),
          "V_interlayer_learned": per_channel_interlayer(Vs),
          "K_interlayer_learned": per_channel_interlayer(Ks)}
    print(f"  V: adjacent {pc['V_adjacent']:.2f}x  strided-8 {pc['V_strided8']:.2f}x  inter-layer(learned) {pc['V_interlayer_learned']:.2f}x")
    print(f"  K: adjacent {pc['K_adjacent']:.2f}x  strided-8 {pc['K_strided8']:.2f}x  inter-layer(learned) {pc['K_interlayer_learned']:.2f}x")

    interlayer_best = max(pc["V_interlayer_learned"], pc["K_interlayer_learned"])
    honest_best = max(pc.values())
    alive = honest_best > 1.3
    print("\n" + "=" * 64 + "\nKILL-TEST GATE (affine-controlled, BUILD_PLAN Step 2)\n" + "=" * 64)
    print(f"  inter-layer (the swarm hypothesis), pooled+scaled = {interlayer_best:.2f}x  -> "
          f"{'alive' if interlayer_best > 1.3 else 'DEAD'}")
    print(f"  best honest (per-channel) adjacent/strided axis   = {honest_best:.2f}x  -> "
          f"{'alive' if alive else 'DEAD'}")
    if alive:
        live = max(pc, key=pc.get)
        print(f"  >>> delta-KV has a LIVE axis: {live} = {pc[live]:.2f}x. Proceed to Step 3 on THAT axis,\n"
              f"      but first confirm it beats plain q4-KV through the gauge, not just on variance.")
    else:
        print("  >>> delta-KV is DEAD across every axis once affine quant is controlled for.\n"
              "      The inter-layer hypothesis fails outright; the adjacent-K 'win' was cross-channel\n"
              "      scale that q4-KV already captures. STOP — do not build a delta-KV kernel.")
    json.dump({"pooled_V": Vp, "pooled_K": Kp, "per_channel": pc,
               "interlayer_best": interlayer_best, "honest_best": honest_best, "alive": alive,
               "context_tokens": len(ids), "layers": len(Vs)},
              open("experiments/killtest_result.json", "w"), indent=2)


if __name__ == "__main__":
    main()
