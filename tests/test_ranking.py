"""Strategy grid and shortlist tests (offline)."""

from pathlib import Path

from dream_quant.data.loader import get_universe_fixture_path, load_ohlcv
from dream_quant.data.universe import load_universe_config
from dream_quant.markets.ranker import rank_markets
from dream_quant.ranking.shortlist import build_deploy_shortlist


def test_strategy_grid_walk_forward(tmp_path):
    cfg = load_universe_config("configs/universe.yaml")
    syms = cfg.get("test_symbols", ["SPY"])
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=syms)
    from dream_quant.markets.ranker import rank_markets

    market_df = rank_markets(ohlcv, cfg, tmp_path)
    from dream_quant.ranking.grid import rank_strategies

    df = rank_strategies(ohlcv, market_df, cfg, tmp_path, data_source="fixture")
    assert not df.empty
    assert "mean_test_sharpe" in df.columns
    assert "gates_passed" in df.columns
    assert df.iloc[0]["composite_score"] >= df.iloc[-1]["composite_score"]


def test_deploy_shortlist(tmp_path: Path):
    cfg = load_universe_config("configs/universe.yaml")
    syms = cfg.get("test_symbols", ["SPY", "QQQ"])
    ohlcv = load_ohlcv(get_universe_fixture_path(), symbols=syms)
    market_df = rank_markets(ohlcv, cfg, tmp_path)
    from dream_quant.ranking.grid import rank_strategies

    strategy_df = rank_strategies(ohlcv, market_df, cfg, tmp_path)
    payload = build_deploy_shortlist(market_df, strategy_df, cfg, tmp_path)
    assert payload["shortlist"]
    assert (tmp_path / "deploy_shortlist.md").exists()
    assert "risk_notes" in payload
