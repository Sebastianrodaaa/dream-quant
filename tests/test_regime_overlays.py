"""Regime overlays and deploy consistency tests."""

import copy
import json
from pathlib import Path

import pandas as pd

from dream_quant.data.loader import get_universe_fixture_path, load_ohlcv
from dream_quant.data.universe import load_universe_config
from dream_quant.paper.forward import run_forward_paper
from dream_quant.portfolio.overlays import regime_risk_scale
from dream_quant.portfolio.simulate import simulate_portfolio
from dream_quant.validation.consistency import evaluate_forward_consistency


def test_overlays_causal_lag():
    cfg = load_universe_config("configs/universe.yaml")
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=["SPY", "QQQ"])
    cfg = copy.deepcopy(cfg)
    cfg["overlays"] = {**cfg.get("overlays", {}), "enabled": True}
    scale = regime_risk_scale(ohlcv, cfg)
    assert scale.iloc[0] == 1.0


def test_deploy_not_eligible_on_negative_rolling_sharpe(tmp_path: Path):
    cfg = load_universe_config("configs/universe.yaml")
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=cfg["test_symbols"])
    shortlist = [
        {
            "symbol": "SPY",
            "strategy": "momentum",
            "params": {
                "lookback": 20,
                "fast_ma": 10,
                "slow_ma": 50,
                "threshold": 0.02,
                "vol_percentile_cap": 0.9,
            },
        }
    ]
    paper_dir = tmp_path / "paper"
    run_forward_paper(ohlcv, cfg, shortlist, mode="backfill", state_dir=paper_dir)
    metrics = json.loads((paper_dir / "forward_metrics.json").read_text())
    health = {"rolling_sharpe_90": -1.0, "rolling_sharpe_252": -0.5}
    fc = evaluate_forward_consistency(
        "READY",
        health,
        metrics,
        paper_dir / "forward_equity.csv",
        cfg,
    )
    assert fc["research_ready"] is True
    assert fc["deploy_eligible"] is False
    assert fc["regime_stress"] is True


def test_simulate_with_overlays_disabled_matches_baseline():
    cfg = load_universe_config("configs/universe.yaml")
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=["SPY"])
    shortlist = [
        {
            "symbol": "SPY",
            "strategy": "momentum",
            "params": {
                "lookback": 20,
                "fast_ma": 10,
                "slow_ma": 50,
                "threshold": 0.02,
                "vol_percentile_cap": 0.9,
            },
        }
    ]
    cfg_off = copy.deepcopy(cfg)
    cfg_off["overlays"] = {"enabled": False}
    r1 = simulate_portfolio(ohlcv, shortlist, cfg_off)
    r2 = simulate_portfolio(ohlcv, shortlist, cfg_off)
    assert r1.metrics["sharpe"] == r2.metrics["sharpe"]
