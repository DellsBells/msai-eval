"""env_check.py — verify every frontier-judge API key authenticates BEFORE the real run.

For each provider: (1) list models (authenticates the key + discovers exact model IDs),
(2) a tiny inference ping (~5 tokens). Prints OK/FAIL per provider and never prints the key.
OpenAI-compatible judges (xAI, Gemini, OpenAI, DeepSeek) go through the openai SDK with a
per-provider base_url; Claude goes through the Anthropic SDK. Costs ~nothing."""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env(path=os.path.join(HERE, ".env")):
    if not os.path.exists(path):
        print(f"no .env at {path}"); raise SystemExit(1)
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


load_env()

# OpenAI-compatible providers: (label, env var, base_url or None for default, model preference list)
OAI = [
    ("openai", "OPENAI_API_KEY", None,
     ["gpt-5.5", "gpt-5.4", "gpt-5"]),
    ("xai",    "XAI_API_KEY", "https://api.x.ai/v1",
     ["grok-4", "grok-4-latest", "grok-3", "grok-beta"]),
    ("gemini", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/",
     ["gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro"]),
    ("deepseek", "DEEPSEEK_API_KEY", "https://api.deepseek.com",
     ["deepseek-chat", "deepseek-reasoner"]),
]


def pick(preference, available):
    ids = [m for m in available]
    for p in preference:                     # exact match first
        if p in ids:
            return p
    for p in preference:                     # then substring (handles "models/gemini-..." etc.)
        for m in ids:
            if p in m:
                return m
    return ids[0] if ids else None


def short(e):
    s = str(e).replace("\n", " ")
    return s[:180]


rows = []

# ---- OpenAI-compatible providers -------------------------------------------------
try:
    from openai import OpenAI
except Exception as e:
    print("openai SDK missing:", e); raise SystemExit(1)

for label, var, base, pref in OAI:
    key = os.environ.get(var)
    if not key:
        rows.append((label, "-", "SKIP", "no key in .env", "", 0)); continue
    try:
        client = OpenAI(api_key=key, base_url=base) if base else OpenAI(api_key=key)
        models = [m.id for m in client.models.list().data]
        auth = "OK"
    except Exception as e:
        rows.append((label, "-", "FAIL", short(e), "", 0)); continue
    model = pick(pref, models)
    infer = "SKIP"; note = ""
    try:
        r = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": "ping"}], max_completion_tokens=5)
        infer = "OK"
    except Exception as e1:
        try:  # older param name
            r = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": "ping"}], max_tokens=5)
            infer = "OK"
        except Exception as e2:
            infer = "auth-only"; note = short(e2)
    rows.append((label, model or "?", f"{auth}/{infer}", note, ",".join(sorted(models)[:6]), len(models)))

# ---- Anthropic (Claude) ----------------------------------------------------------
akey = os.environ.get("ANTHROPIC_API_KEY")
if not akey:
    rows.append(("claude", "-", "SKIP", "no key in .env", "", 0))
else:
    try:
        import anthropic
        ac = anthropic.Anthropic(api_key=akey)
        models = [m.id for m in ac.models.list().data]
        auth = "OK"
        infer = "SKIP"; note = ""
        try:
            ac.messages.create(model="claude-opus-4-8", max_tokens=5,
                               messages=[{"role": "user", "content": "ping"}])
            infer = "OK"
        except Exception as e:
            infer = "auth-only"; note = short(e)
        rows.append(("claude", "claude-opus-4-8", f"{auth}/{infer}", note,
                     ",".join(sorted(models)[:6]), len(models)))
    except Exception as e:
        rows.append(("claude", "-", "FAIL", short(e), "", 0))

# ---- report ----------------------------------------------------------------------
print("\nFRONTIER JUDGE ENV CHECK\n" + "=" * 70)
print(f"{'judge':9s} {'status':14s} {'model':22s} note / models")
print("-" * 70)
ok = 0
for label, model, status, note, sample, n in rows:
    flag = "OK" in status
    ok += flag
    print(f"{label:9s} {status:14s} {(model or '-'):22s} {note or (str(n)+' models: '+sample)}")
print("-" * 70)
print(f"{ok}/{len(rows)} providers authenticated. "
      + ("ALL GOOD — ready for the run." if ok >= 4 else "fix the FAIL/SKIP rows before the run."))
