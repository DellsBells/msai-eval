# FAQ — the hostile questions first

**"You used AI to audit AI. Isn't that circular?"**
Partly, and the design says so out loud. AI sessions authored tasks, ran studies, and
cross-reviewed each other adversarially — but the ground truth in the flagship study is
**hidden test suites**, not any model's opinion. The oracle corpus was sealed (hash
committed) before any candidate solution existed, and the certificate ID is literally
the sha256 of the scores file. The parts that ARE circular (AI-written prose, AI-run
review lanes) are labeled, and the repo ships everything a human needs to re-run the
studies without trusting any of it. Check it — that is the point.

**"Your panel FAILED. Why publish a failure?"**
Because a measurement system that can't say "I can't resolve this" will happily say
something worse. The failure is the product: the instrument caught its own panel's
noise band exceeding every gap under test, *before* that panel's verdicts got used
for anything. If your eval stack has never failed a qualification, it has never been
qualified.

**"n=3 judges, 55 tasks, one lab. Why should anyone care?"**
You shouldn't — yet. You should care that the *method* transfers: two-band gates,
guard-banded verdicts, En scores, and per-instrument charts caught a stuck needle,
a missing mid-scale, and a consensus-wrong failure mode that averaging hides. Run it
on your own judges; the repo is the reproduction kit.

**"Consensus of frontier models is the industry standard. You claim it's wrong?"**
No. We measured one specific, small thing: in 44 scoreable pairs, the panel's
consensus was wrong 3 times (6.8%, interval [2.0%, 17.1%]) — and 2 of those 3 were
*shared* errors, the kind consensus structurally cannot catch. That is not "consensus
is wrong"; it is "consensus needs an answer key sometimes, and here is a cheap way
to build one."

**"Isn't Gage R&R for factory floors, not language models?"**
The math doesn't know what the gauge is made of. Repeatability, reproducibility, and
resolution are properties of any measurement process, including one made of weights.
Where the transfer genuinely breaks (ndc, for example), we say so and demote the
metric rather than force it.

**"Who paid for this?"**
The operator, personally. No grants, no employer sponsorship, no vendor money. Total
frontier-API spend on the certificate-1 study: $2.23. The point survives poverty.

**"Why is some data withheld?"**
Three withheld sets, three named reasons: the entropy-arm bank embeds near-verbatim
paid-standards text (copyright — hashes published, auditors can request it); two
companion-study artifacts ship with a later release (marked † on the site); and no
record-level production data from anyone's business ships, ever — aggregates only.
Nothing is withheld because it hurts the story. The least flattering numbers on the
site are receipted in this repo.

**"What would change your mind?"**
A replication showing the two-band gate passes panels that then produce wrong
decisions downstream, or that the guard-band arithmetic mis-covers at stated
confidence. The prereg discipline cuts both ways: the acceptance rules were sealed
before the data, so a failed replication is a finding about the instrument, and we
would publish it the same way we published the panel's failure.
