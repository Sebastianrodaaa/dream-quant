"""Replay simulator tests — must not invoke backtester."""

from unittest.mock import MagicMock

import pytest

from dream_quant.backtest.engine import BacktestEngine
from dream_quant.discovery.rollout import OnlineRollout, RolloutConfig
from dream_quant.discovery.tree import DiscoveryTree
from dream_quant.data.loader import load_ohlcv, get_fixture_path
from dream_quant.policy.base import PolicyConfig
from dream_quant.policy.improver import PolicyImprover
from dream_quant.policy.parallel_refine import ParallelRefinePolicy
from dream_quant.replay.scoring import score_replay
from dream_quant.replay.types import ReplayScoreConfig
from dream_quant.replay.simulator import ReplaySimulator


@pytest.fixture
def sample_tree():
    ohlcv = load_ohlcv(get_fixture_path(), symbols=["SPY"])
    engine = BacktestEngine()
    policy = ParallelRefinePolicy(PolicyConfig(expand_top_k=2))
    rollout = OnlineRollout(engine, policy, RolloutConfig(max_attempts=12, batch_size=2, seed=1))
    return rollout.run(ohlcv)


def test_replay_does_not_call_backtester(sample_tree):
    simulator = ReplaySimulator()
    policy = ParallelRefinePolicy()
    mock_engine = MagicMock(wraps=BacktestEngine())
    result = simulator.replay(sample_tree, policy, batch_size=3, seed=0)
    mock_engine.run.assert_not_called()
    assert result.backtest_calls == 0
    assert result.attempts >= len(sample_tree.root_ids)


def test_replay_score_formula(sample_tree):
    simulator = ReplaySimulator(ReplayScoreConfig(quality_weight=1.0, attempt_penalty=0.02, parallelism_bonus=0.005))
    policy = ParallelRefinePolicy(PolicyConfig(min_sharpe_to_expand=-999))
    result = simulator.replay(sample_tree, policy, batch_size=3, max_attempts=50, seed=0)
    expected = 1.0 * result.best_quality - 0.02 * result.attempts + 0.005 * result.avg_batch_size
    assert score_replay(result, simulator.score_config) == pytest.approx(expected)


def test_policy_improvement_monotonicity(sample_tree):
    """Selected policy replay score must be >= current when current is in candidate set."""
    current = ParallelRefinePolicy(PolicyConfig(expand_top_k=2, min_sharpe_to_expand=-0.5))
    improver = PolicyImprover(seed=7)
    result = improver.improve(current, [sample_tree], batch_size=3)
    assert result.selected_score >= result.current_score - 1e-9
    assert any(
        c["config"] == current.config.to_dict() and c["score"] == result.current_score
        for c in result.candidates
    )
