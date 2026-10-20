"""RSI archive + Reflexion adapters."""

from __future__ import annotations

import json
from pathlib import Path

from dream_quant.research.reflexion import (
    FROZEN_EVALUATORS,
    load_reflexion_hints,
    write_reflexion_postmortem,
)
from dream_quant.research.rsi_archive import append_challenger_archive, load_challenger_lineage


def test_challenger_archive_lineage(tmp_path: Path) -> None:
    out = tmp_path / "artifacts"
    append_challenger_archive(
        out,
        try_id="try_001",
        phase="paper_policy",
        challengers=[{"id": "policy_a", "rolling_90d": 0.01, "eligible": True, "sota_verified": True, "ops_ready": True}],
        incumbent_id="policy_root",
        promoted_id="policy_a",
        research_champion="rp2_corr35_rebal42",
    )
    append_challenger_archive(
        out,
        try_id="try_002",
        phase="paper_policy",
        challengers=[{"id": "policy_b", "rolling_90d": 0.02, "eligible": True, "sota_verified": True, "ops_ready": True}],
        incumbent_id="policy_a",
        promoted_id="policy_b",
        research_champion="rp2_corr35_rebal42",
    )
    lin = load_challenger_lineage(out, "policy_b")
    assert lin is not None
    assert "policy_b" in lin["lineage"]
    assert (out / "research" / "challenger_archive.jsonl").exists()


def test_reflexion_dedupes_what_failed(tmp_path: Path) -> None:
    out = tmp_path / "artifacts"
    trials = [
        {
            "id": f"p{i}",
            "rolling_90d": -0.1 + i * 0.01,
            "rolling_30d": 0.1,
            "sota_verified": False,
            "ops_ready": True,
            "eligible": False,
            "forward_replay": {"halted": True, "halt_reason": f"gross exposure kill: 1.0{i}"},
            "incumbent_baseline_90d": 0.024,
        }
        for i in range(20)
    ]
    write_reflexion_postmortem(
        out, try_id="try_x", phase="test", trigger="halt", trials=trials, incumbent_id="inc", promoted=False
    )
    hints = load_reflexion_hints(out)
    assert hints["what_failed"].count("kill_switch_halt") == 1
    assert len(hints["next_explore_bias"]["avoid"]) == len(set(hints["next_explore_bias"]["avoid"]))


def test_reflexion_postmortem_and_hints(tmp_path: Path) -> None:
    out = tmp_path / "artifacts"
    trials = [
        {
            "id": "bad_policy",
            "rolling_90d": -0.1,
            "rolling_30d": -0.2,
            "sota_verified": False,
            "ops_ready": False,
            "eligible": False,
            "forward_replay": {"halted": True, "halt_reason": "max daily loss kill"},
            "incumbent_baseline_90d": 0.006,
        }
    ]
    result = write_reflexion_postmortem(
        out,
        try_id="try_009",
        phase="paper_policy_grid",
        trigger="kill_switch_halt",
        trials=trials,
        incumbent_id="incumbent",
        target_forward_90d=0.15,
        promoted=False,
    )
    assert result is not None
    hints = load_reflexion_hints(out)
    assert hints.get("try_id") == "try_009"
    assert "kill_switch" in str(hints.get("what_failed", [])).lower() or hints.get("what_failed")
    assert "sota_12_12" in FROZEN_EVALUATORS
