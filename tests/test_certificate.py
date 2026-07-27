"""Certificate renderer — regression ledger for the cross-organ audit findings.

Pattern under test (KB session, 2026-07-02): THE VERIFY COMMAND IS ITSELF UNDER TEST —
a verification command that has never been executed in CI is decoration. These tests run
the certificate's documented verify path end-to-end on the shipped evidence.

Ledgered here: REV-006 (utf-8 + atomic write + --out arg parsing + repo-root relative
invocation), REV-011 (declared data date; k coverage basis printed), REV-016 (literal
NO ACCURACY CLAIMED printed), REV-020 (renderer version + results digest pinned).
"""
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(REPO, "benchmark")
SCORES = os.path.join(BENCH, "frontier_api_scores.json")
KNOWN_ID = "MSAI-8C06733F42F0"  # sha256 of the shipped frontier scores file

sys.path.insert(0, BENCH)

pytestmark = pytest.mark.skipif(
    not os.path.exists(SCORES), reason="shipped frontier scores not present")


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    import certificate
    out = tmp_path_factory.mktemp("cert") / "CERT_TEST.md"
    path, text = certificate.render(SCORES, str(out), data_date="2026-07-02")
    return path, text


def test_renders_and_is_utf8_on_disk(rendered):
    path, text = rendered
    with open(path, "rb") as f:
        raw = f.read()
    body = raw.decode("utf-8")                      # REV-006: explicit utf-8, any platform
    assert "Δ" in body and "ν" in body              # the chars that killed cp1252
    assert body == text.replace("\r\n", "\n") or body == text


def test_honesty_banner_literal(rendered):
    _, text = rendered
    assert "NO ACCURACY CLAIMED" in text            # REV-016: literal, not equivalent-in-meaning


def test_spec_required_fields(rendered):
    _, text = rendered
    assert "MSAI-GC/1.0-draft" in text              # spec §2 self-identification
    assert KNOWN_ID in text                          # hash binding reproduces
    assert "2026-07-02" in text                      # REV-011: declared data date, not mtime
    assert "Welch–Satterthwaite" in text and "coverage" in text  # REV-011: k basis stated
    assert "results-digest" in text                  # REV-020: verdict-table digest pinned


def test_verdict_states_present(rendered):
    _, text = rendered
    for state in ("RESOLVED", "AT-EDGE", "BELOW"):
        assert state in text


def test_failed_render_leaves_no_partial_file(tmp_path):
    import certificate
    out = tmp_path / "SHOULD_NOT_EXIST.md"
    with pytest.raises(Exception):
        certificate.render(str(tmp_path / "no_such_scores.json"), str(out))
    assert not out.exists()                          # REV-006: atomic — never truncate-then-die


def test_documented_verify_command_from_repo_root(tmp_path):
    """The skeptic's command, exactly as documented, exercised in CI (P-candidate:
    THE VERIFY COMMAND IS ITSELF UNDER TEST). Also pins the REV-006 --out bug: the
    --out value must be honored as a path, not swallowed as the scores positional."""
    out = tmp_path / "CERT_CLI.md"
    r = subprocess.run(
        [sys.executable, os.path.join("benchmark", "certificate.py"),
         "--out", str(out), "--data-date", "2026-07-02"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    assert out.exists() and out.stat().st_size > 4000
    body = out.read_bytes().decode("utf-8")
    assert KNOWN_ID in body and "NO ACCURACY CLAIMED" in body


def test_null_path_disclosed_never_coerced(rendered):
    """KB #018 exhibit (a): null scores are excluded AND disclosed — never coerced.
    The count printed on the certificate must equal the true null count in the evidence."""
    import json
    _, text = rendered
    with open(SCORES, encoding="utf-8") as f:
        true_nulls = sum(1 for s in json.load(f)["scores"] if s["score"] is None)
    assert f"({true_nulls} null-score rows excluded, disclosed)" in text
    assert "NULL PATH" in text and "never coercion" in text
