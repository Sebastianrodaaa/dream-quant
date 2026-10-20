"""Regime search and new strategy tests."""

import copy
from pathlib import Path

import pandas as pd

from dream_quant.data.loader import get_universe_fixture_path, load_ohlcv
from dream_quant.data.universe import load_universe_config
from dream_quant.portfolio.regime_select import _rolling_sharpe, score_book_on_train, select_regime_book
from dream_quant.research.search import SearchResult, nested_walk_forward_search
from dream_quant.strategies.base import StrategySpec
from dream_quant.strategies.registry import STRATEGY_REGISTRY
from dream_quant.validation.walkforward import WalkForwardResult, FoldResult


def test_absolute_momentum_registered():
    assert "absolute_momentum" in STRATEGY_REGISTRY
    assert "safe_haven" in STRATEGY_REGISTRY


def test_regime_select_on_fixture():
    cfg = load_universe_config("configs/universe.yaml")
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=cfg["test_symbols"])
    dates = sorted(ohlcv.index.unique())
    train = ohlcv.loc[dates[: -min(60, len(dates) // 4)]]
    spec = STRATEGY_REGISTRY["absolute_momentum"].default_spec()
    pool: list[SearchResult] = []
    for sym in cfg["test_symbols"]:
        from dream_quant.data.symbols import extract_symbol

        sym_data = extract_symbol(train, sym)
        r = nested_walk_forward_search(sym_data, train, sym, spec, cfg)
        if r:
            pool.append(r)
    if len(pool) >= 2:
        best, trials = select_regime_book(train, pool[:4], cfg, holdout_bars=60)
        assert trials


def test_rolling_sharpe_helper():
    s = pd.Series([0.001] * 100)
    assert _rolling_sharpe(s, 30) > 0
