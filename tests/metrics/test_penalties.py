"""Unit tests for anti-dark-pattern penalties and core metrics."""

from harness.metrics import (
    bm_score,
    fake_cite_penalty,
    hype_inflation_penalty,
    mae,
    sci_fi_collapse_penalty,
    set_f1,
    t1_score_from_mae,
    total_penalties,
)


def test_fake_cite_without_url():
    text = "According to Smith et al., 2023 the system is ready [1]."
    assert fake_cite_penalty(text) > 0.5


def test_fake_cite_with_url_ok():
    text = "According to Smith et al., 2023 (https://example.com/paper) it is partial."
    assert fake_cite_penalty(text) == 0.0


def test_sci_fi_collapse():
    text = "Mind uploading has been solved and we have digital consciousness."
    assert sci_fi_collapse_penalty(text, gold_thesis_poss=10) > 0.5


def test_hype_inflation():
    assert hype_inflation_penalty(90, 40) > 0.0
    assert hype_inflation_penalty(50, 40) == 0.0


def test_total_penalties_bundle():
    text = "Cookies are already real. Smith et al., 2024 proved consciousness is solved."
    p = total_penalties(text, pred_thesis_poss=95, gold_thesis_poss=15)
    assert p["total"] > 0.3


def test_set_f1():
    assert set_f1({"a", "b"}, {"a", "b"}) == 1.0
    assert set_f1({"a", "b"}, {"a"}) == 2 / 3
    assert set_f1(set(), set()) == 1.0


def test_mae():
    assert mae([1, 2, 3], [1, 2, 3]) == 0.0
    assert mae([0, 10], [10, 0]) == 10.0


def test_t1_and_bm_score():
    assert t1_score_from_mae(0) == 1.0
    assert t1_score_from_mae(100) == 0.0
    s = bm_score({"T1": 1, "T2": 1, "T3": 1, "T4": 1, "T5": 1}, 0)
    assert abs(s - 1.0) < 1e-9
    s2 = bm_score({"T1": 1, "T2": 1, "T3": 1, "T4": 1, "T5": 1}, 0.2)
    assert abs(s2 - 0.8) < 1e-9
