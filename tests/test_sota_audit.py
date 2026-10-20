"""SOTA audit math tests (offline fixtures)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dream_quant.data.loader import get_universe_fixture_path, load_ohlcv
from dream_quant.data.universe import load_universe_config
import pandas as pd

from dream_quant.validation.sota_audit import (
    cpcv_path_sharpes,
    deflated_sharpe_ratio,
    probabilistic_sharpe_ratio,
    compute_pbo_cscv,
    compute_pbo_neighbors_only,
    permutation_test,
    purged_embargo_train_mask,
    run_sota_audit,
    evaluate_sota_gates,
    sharpe_of_returns,
)


def test_sharpe_positive_drift():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.001, 0.01, 500))
    assert sharpe_of_returns(r) > 0


def test_psr_high_for_strong_sharpe():
    psr = probabilistic_sharpe_ratio(2.0, 500, skew=0, kurtosis=3)
    assert psr > 0.95


def test_dsr_penalizes_many_trials():
    from dream_quant.validation.sota_audit import expected_max_sharpe

    assert expected_max_sharpe(500) > expected_max_sharpe(5)
    moderate = deflated_sharpe_ratio(0.5, 500, n_trials=500, skew=0, kurtosis=3)
    assert moderate < deflated_sharpe_ratio(0.5, 500, n_trials=5, skew=0, kurtosis=3)


def test_cpcv_paths_count():
    r = pd.Series(np.random.default_rng(1).normal(0.0005, 0.01, 600))
    out = cpcv_path_sharpes(r, n_groups=6, n_test_groups=3)
    assert out["n_paths"] == 20
    assert len(out["sharpes"]) == 20


def test_pbo_random_variants_high():
    rng = np.random.default_rng(2)
    n = 400
    variants = {f"v{i}": pd.Series(rng.normal(0, 0.01, n)) for i in range(8)}
    pbo = compute_pbo_cscv(variants, n_splits=8)
    assert 0 <= pbo["pbo"] <= 1


def test_permutation_block_bootstrap_runs():
    r = pd.Series(
        np.random.default_rng(3).normal(0.0005, 0.01, 300),
        index=pd.date_range("2020-01-01", periods=300, freq="B"),
    )
    perm = permutation_test(r, n_perm=50, seed=3, method="block_21d", block_size=21)
    assert "block_bootstrap" in perm["method"] or "sign_flip" in perm["method"]
    assert 0 <= perm["p_value"] <= 1
    assert "observed_total_return" in perm
    assert "observed_percentile" in perm
    assert perm.get("block_size") == 21


def test_pbo_fixed_neighbors_low_when_stable():
    rng = np.random.default_rng(0)
    n = 400
    base = rng.normal(0.001, 0.01, n)
    variants = {
        "selected": pd.Series(base),
        "n1": pd.Series(base + rng.normal(0, 0.0005, n)),
        "n2": pd.Series(base + rng.normal(0, 0.0005, n)),
    }
    pbo = compute_pbo_cscv(variants, n_splits=8)
    assert 0 <= pbo["pbo"] <= 1


def test_purged_embargo_mask():
    test_idx = np.array([50, 51, 52])
    mask = purged_embargo_train_mask(200, test_idx, embargo_bars=5)
    assert not mask[50]
    assert not mask[45]


def test_run_sota_audit_fixture(tmp_path: Path):
    cfg = load_universe_config("configs/universe.yaml")
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=cfg["test_symbols"])
    book = [
        {
            "symbol": "SPY",
            "strategy": "momentum",
            "params": {"lookback": 20, "fast_ma": 10, "slow_ma": 50, "threshold": 0.02, "vol_percentile_cap": 0.9},
        }
    ]
    art = tmp_path / "artifacts"
    audit = run_sota_audit(ohlcv, book, cfg, artifacts_dir=art, n_perm=50, holdout_bars=60)
    assert "verified_profitable_no_overfit" in audit
    assert (art / "sota_audit" / "VERDICT.json").exists()
    verdict = json.loads((art / "sota_audit" / "VERDICT.json").read_text())
    assert "failed_gates" in verdict


def test_evaluate_sota_gates_structure():
    audit = {
        "cpcv": {"median_sharpe": 0.5, "pct_positive": 0.5},
        "pbo": {"pbo": 0.6},
        "dsr": 0.5,
        "psr": 0.5,
        "permutation": {"p_value": 0.5, "gate_passed": False},
        "baselines": {"buy_hold_spy_cpcv_median": 0.3, "static_60_40_cpcv_median": 0.3},
        "holdout": {"sharpe": 0.2, "max_drawdown": -0.2},
        "cost_stress_10bps_cpcv_median": 0.3,
        "plateau": {"fraction_positive": 0.3},
    }
    gates = evaluate_sota_gates(audit)
    assert len(gates) == 12
    assert not all(g.passed for g in gates)
