"""Stability and diversification tests."""

from dream_quant.data.loader import get_universe_fixture_path, load_ohlcv
from dream_quant.data.universe import load_universe_config
from dream_quant.portfolio.diversify import build_diversified_book, _concentration_score
from dream_quant.research.search import SearchResult
from dream_quant.validation.stability import param_neighbor_sensitivity
from dream_quant.validation.walkforward import WalkForwardResult, FoldResult
from dream_quant.strategies.base import StrategySpec


def _fake_result(symbol: str, sharpe: float, passed: bool) -> SearchResult:
    wf = WalkForwardResult(
        symbol=symbol,
        strategy="dual_momentum",
        params={"lookback": 126},
        folds=[FoldResult(1, 100, 50, 0.5, sharpe, 0.01, -0.05, 15, 1.0)],
        mean_test_sharpe=sharpe,
        folds_sharpe_pass=1 if sharpe >= 0.8 else 0,
    )
    return SearchResult(symbol=symbol, strategy="dual_momentum", params={}, walk_forward=wf, gate_passed=passed, objective=sharpe)


def test_diversified_book_prefers_unique_symbols():
    cfg = load_universe_config("configs/universe.yaml")
    results = [
        _fake_result("QQQ", 0.95, True),
        _fake_result("HYG", 0.85, False),
        _fake_result("TLT", 0.75, False),
        _fake_result("SPY", 0.70, False),
    ]
    book, conc = build_diversified_book(results, cfg)
    symbols = [b["symbol"] for b in book]
    assert len(set(symbols)) >= 2
    assert conc["unique_symbols"] >= 2


def test_concentration_fragile_single_symbol():
    conc = _concentration_score([{"symbol": "QQQ"}, {"symbol": "QQQ"}])
    assert conc["fragile"] is True
    assert conc["hhi"] == 1.0
