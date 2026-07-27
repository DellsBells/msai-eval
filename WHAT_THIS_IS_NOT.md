# What this is not

Honest scope, stated before anyone asks. The companion piece to every claim in this repo.

**This is not proof that LLM judges work.** Our flagship result is the opposite: a
panel of three local judges **failed qualification honestly** — its noise band
(U ≈ 2.5 on a 4-point scale) was wider than every gap it was asked to resolve. The
instrument's job was to say so before anyone trusted the panel. It did.

**This is not a benchmark or a leaderboard.** Nothing here ranks models by quality.
MSAI measures the *measurement system* — whether a judge panel can resolve the
differences a decision rides on. A judge can score high on a leaderboard and still
be a stuck needle here (one of ours answered "4" on 73% of its ratings).

**This is not a claim that anyone's published numbers are wrong.** The only claim
class this instrument can emit about an external eval is "the published instrument
cannot resolve the published deltas at the stated confidence" — a statement about
resolution, not about truth. We have not yet issued such a statement about any
third-party eval, and per our pre-registered rails we would notify owners well
before any such study went public.

**This is not finished metrology.** Three certificates exist; each carries its own
deviations log. Known open items: consensus-wrong events are few (3 of 44 — a smoke
signal, not a structure estimate); one pinned judge died mid-study and is
excluded-disclosed, not replaced; ndc — a standard MSA figure of merit — failed its
audition on AI judges and was demoted to advisory here, which is itself a finding
that needs replication by people who are not us.

**This is not independent yet.** The studies were designed, run, and audited by a
small number of humans and AI sessions working closely together, with adversarial
review between lanes but no outside replication. The repo ships everything needed
for a stranger to re-run the sealed studies (`docs/PUBLIC_CLAIMS_LEDGER.md` maps
every public number to its artifact). Until strangers do, treat every result as
n=1 lab work with receipts.

**This is not a product.** No warranty, no support contract, no assertion that the
code is fit for gating your deployment. It is an argument, with evidence, that
evaluation instruments should have to earn trust the way physical gauges do —
by blind comparison against references, with uncertainty stated.

**Two numbers on the results site are marked with a dagger (†).** Their row-level
artifacts live in a companion lane's private archive and ship with a later release.
Every other number has its receipt in this repository today.
