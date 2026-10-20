"""Structural research try (try_012) smoke tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dream_quant.data.universe import load_universe_config
from dream_quant.research.forward_ceiling import GrindingFrozenError, assert_grinding_allowed
from dream_quant.research.structural_try import load_structural_challengers, write_pareto_note


def test_load_structural_challengers_excludes_paper_cluster() -> None:
    cfg = load_universe_config("configs/universe.yaml")
    names = {c["name"] for c in load_structural_challengers(cfg)}
    assert "rp2_corr35_rebal42" not in names
    assert "rp2_corr22_regime_ov_vt10" not in names
    assert "rp2_corr35_regime_ov" not in names
    assert "rp_gld_rebal42_corr40" not in names
    assert "ens_champ_regime_50" in names
    assert "tsmom_spy_tlt_gld_vt10" in names
    assert len(names) >= 8


def test_grinding_frozen_blocks_overlay_refinement() -> None:
    cfg = load_universe_config("configs/universe.yaml")
    with pytest.raises(GrindingFrozenError):
        assert_grinding_allowed(cfg, overlay_grid_mode=True)
    with pytest.raises(GrindingFrozenError):
        assert_grinding_allowed(cfg, refinement_grid_mode=True)
    assert_grinding_allowed(cfg, overlay_grid_mode=True, force=True)
    assert_grinding_allowed(cfg)


def test_write_pareto_note(tmp_path: Path) -> None:
    trials = [
        {"name": "a", "rolling_90d": 0.05, "sota_verified": True, "ops_ready": True, "median_30d_full": 0.1, "last_90d_full": 0.2},
        {"name": "b", "rolling_90d": 0.08, "sota_verified": False, "ops_ready": False},
    ]
    out = write_pareto_note(
        tmp_path,
        try_id="try_012",
        research_champion="rp2_corr35_rebal42",
        paper_policy="regime_ov_bond20_vt10_ros67_vss82_ts70_rb49",
        paper_fwd_90d=0.105,
        trials=trials,
        promoted_research=False,
        promoted_paper=False,
    )
    assert Path(out["json"]).exists()
    note = json.loads(Path(out["json"]).read_text())
    assert note["promoted_paper"] is False
    assert note["best_forward_replay"]["name"] == "b"
