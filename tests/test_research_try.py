"""Research-try pipeline: Dream-RSI mandatory gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dream_quant.discovery.tree import DiscoveryTree
from dream_quant.research.dream_rsi import (
    DreamRSIRequiredError,
    extract_rsi_candidates,
    validate_dream_rsi_artifacts,
)
from dream_quant.research.try_pipeline import run_research_try
from tests.test_tree import _make_node


def _seed_minimal_dream_rsi(dream_dir: Path) -> None:
    """Minimal valid Dream-RSI artifact tree for fail-closed tests."""
    round_dir = dream_dir / "round_01"
    round_dir.mkdir(parents=True, exist_ok=True)
    tree = DiscoveryTree.empty(metadata={"symbol": "SPY", "round": 1})
    node = _make_node(sharpe=0.42)
    node.node_id = "n1"
    tree.add_node(node)
    tree.save(round_dir / "discovery_tree.json")
    (round_dir / "policy_improvement.json").write_text(
        json.dumps({"selected_score": 0.4, "current_score": 0.3, "candidates": []})
    )
    (dream_dir / "summary.json").write_text(json.dumps({"rounds": [{"round": 1}]}))


def test_validate_dream_rsi_missing_dir(tmp_path: Path) -> None:
    with pytest.raises(DreamRSIRequiredError, match="missing dream_rsi"):
        validate_dream_rsi_artifacts(tmp_path / "nope")


def test_validate_dream_rsi_incomplete_trees(tmp_path: Path) -> None:
    d = tmp_path / "dream_rsi"
    d.mkdir()
    with pytest.raises(DreamRSIRequiredError, match="discovery_tree"):
        validate_dream_rsi_artifacts(d)


def test_validate_dream_rsi_incomplete_policy(tmp_path: Path) -> None:
    d = tmp_path / "dream_rsi"
    rd = d / "round_01"
    rd.mkdir(parents=True)
    tree = DiscoveryTree.empty()
    node = _make_node()
    node.node_id = "x"
    tree.add_node(node)
    tree.save(rd / "discovery_tree.json")
    with pytest.raises(DreamRSIRequiredError, match="policy_improvement"):
        validate_dream_rsi_artifacts(d)


def test_validate_dream_rsi_passes_with_seed(tmp_path: Path) -> None:
    d = tmp_path / "dream_rsi"
    _seed_minimal_dream_rsi(d)
    validate_dream_rsi_artifacts(d, min_rounds=1)


def test_extract_rsi_candidates(tmp_path: Path) -> None:
    d = tmp_path / "dream_rsi"
    _seed_minimal_dream_rsi(d)
    cands = extract_rsi_candidates(d)
    assert len(cands) == 1
    assert cands[0]["symbol"] == "SPY"
    assert cands[0]["source"] == "dream_rsi"


def test_research_try_refuses_without_rsi_artifacts(tmp_path: Path, monkeypatch) -> None:
    """run_research_try must not complete if Dream-RSI artifacts are absent."""

    def _empty_rsi(*_a, **_k):
        from dream_quant.loop.rsi import RSILoopResult

        return RSILoopResult(rounds=[])

    monkeypatch.setattr("dream_quant.research.try_pipeline.run_mandatory_dream_rsi", _empty_rsi)
    monkeypatch.setattr(
        "dream_quant.research.try_pipeline.run_research_iteration",
        lambda *a, **k: {"readiness": {"status": "NOT_READY"}},
    )
    monkeypatch.setattr(
        "dream_quant.research.try_pipeline.load_preferred",
        lambda *a, **k: (__import__("pandas").read_csv("dream_quant/data/fixtures/universe_ohlcv.csv", index_col=0, header=[0, 1]), "fixture"),
    )
    with pytest.raises(DreamRSIRequiredError):
        run_research_try(
            "configs/default.yaml",
            tmp_path,
            try_fetch=False,
            skip_consistency_audit=True,
        )


def test_research_try_manifest_requires_rsi_dir(tmp_path: Path, monkeypatch) -> None:
    """End-to-end with mocked RSI + iterate to keep test fast."""

    def _fake_rsi(cfg, ohlcv, dream_dir, **kwargs):
        _seed_minimal_dream_rsi(Path(dream_dir))
        from dream_quant.loop.rsi import RSILoopResult, RSIRoundResult

        return RSILoopResult(
            rounds=[
                RSIRoundResult(
                    round_num=1,
                    tree_id="t1",
                    tree_path=str(Path(dream_dir) / "round_01/discovery_tree.json"),
                    best_sharpe=0.42,
                    attempt_count=2,
                    replay_score_before=0.1,
                    replay_score_after=0.2,
                    policy_config={},
                )
            ]
        )

    def _fake_iterate(*_a, **_k):
        return {
            "readiness": {"status": "NOT_READY", "n_searched": 0, "n_passing_individual": 0},
            "dream_rsi_dir": str(tmp_path / "research" / "try_001" / "dream_rsi"),
        }

    monkeypatch.setattr("dream_quant.research.try_pipeline.run_mandatory_dream_rsi", _fake_rsi)
    monkeypatch.setattr("dream_quant.research.try_pipeline.run_research_iteration", _fake_iterate)
    monkeypatch.setattr(
        "dream_quant.research.try_pipeline.load_preferred",
        lambda *a, **k: (__import__("pandas").read_csv("dream_quant/data/fixtures/universe_ohlcv.csv", index_col=0, header=[0, 1]), "fixture"),
    )

    result = run_research_try(
        "configs/default.yaml",
        tmp_path,
        try_fetch=False,
        skip_consistency_audit=True,
    )
    try_dir = Path(result["try_dir"])
    assert (try_dir / "dream_rsi" / "round_01" / "discovery_tree.json").exists()
    assert (try_dir / "manifest.json").exists()
    validate_dream_rsi_artifacts(try_dir / "dream_rsi", min_rounds=1)
