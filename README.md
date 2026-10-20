# dream-quant

Personal quantitative trading **research + gated paper deployment** inspired by Dream-RSI.

> **Verified RP SPY+TLT+GLD regime** (`rp2_corr35_rebal42`) — see `artifacts/sota_audit/VERDICT.json`. **Live LOCKED.**

> **Paper-first.** Live execution **LOCKED** unless `deploy_readiness.json` → `READY`, `DREAM_QUANT_LIVE=1`, and `--i-understand-risk`.

## One-command research loop

```bash
pip install -e ".[dev]" && pip install "dream-quant[fetch]"

# Hardening loop: research → diversify → stability → regime search → forward paper
dream-quant harden-iterate --config configs/universe.yaml --no-fetch

# Regime book search (frozen 252d holdout, dual OOS + train-252d objective)
dream-quant regime-search --config configs/universe.yaml

# Close rolling 90d gap (train-only de-risk selection; updates book + overlays)
dream-quant close-90d --config configs/universe.yaml

# SOTA overfitting audit (CPCV, PBO, DSR, PSR, permutation, locked holdout)
dream-quant sota-audit --config configs/universe.yaml
dream-quant sota-iterate --config configs/universe.yaml --rounds 3

# Research try (Dream-RSI mandatory → search → consistency → try_NNN/)
dream-quant research-try --config configs/universe.yaml --no-fetch

# Paper policy try (try_007–011; overlay/refinement grids blocked when grinding_frozen)
dream-quant paper-policy-try --config configs/universe.yaml --no-fetch

# Structural research (try_012 — distinct sleeves; no overlay grind on incumbent)
dream-quant structural-try --config configs/universe.yaml --no-fetch

# Research iterate (Dream-RSI embedded; no stability / diversification)
dream-quant research-iterate --config configs/universe.yaml

# OSS toolkit catalog: docs/OSS_TOOLKIT.md + docs/OSS_RSI_TOOLKIT.md + artifacts/research/oss_toolkit.json

# === Standing ops path (paper autonomy) ===
dream-quant autonomous-paper --config configs/universe.yaml --mode forward
dream-quant paper-status --config configs/universe.yaml

# Cron / monitoring (ops_snapshot.json + forward_integrity.json + CHAMPION_OPS.md)
./scripts/cron_forward_paper.sh
dream-quant ops-check --config configs/universe.yaml   # 0=healthy, 1=ineligible/kill/halt/integrity, 2=error

# One-time bootstrap only (historical warm-up; not daily ops)
dream-quant autonomous-paper --config configs/universe.yaml --mode backfill

# Human-readable status
cat artifacts/paper/daily_summary.md
cat artifacts/paper/ledger/statement.md
cat artifacts/paper/ops_snapshot.json
```

## Personal runbook (paper → live consideration)

**Daily (automated):** run `./scripts/cron_forward_paper.sh` after US market close (or on a weekday schedule). This executes:

1. `autonomous-paper --mode forward` — append new bars only; kill switches active
2. `paper-status` — refresh readiness, daily summary, **ops_snapshot.json**, shadow ledger
3. `ops-check` — forward **integrity gate** (no fake/duplicate bars), exit code for cron/alerting, refreshes **`artifacts/sota_audit/CHAMPION_OPS.md`**

**Maintenance mode (current):** research champion `rp2_corr35_rebal42` (SOTA 12/12); paper policy `regime_ov_bond20_vt10_ros67_vss82_ts70_rb49` with overlay/rebalance grinding **frozen**. No further grid searches on that cluster unless `--force`.

**Weekly:** review `artifacts/paper/daily_summary.md`, sleeve attribution, and `artifacts/deploy_eligible_flip.md` caveats.

**Deploy eligibility ≠ live trading.** `deploy_eligible=true` in `ops_snapshot.json` means forward-consistency gates pass on the backfilled paper book. Live execution stays **triple-locked** until you deliberately:

1. Observe `deploy_eligible=true` on **N consecutive forward days** (suggest N≥20; configure in your cron alert — no auto-live)
2. Confirm `halted=false` and `kill_switch_trips=0` across those days
3. Manually set `DREAM_QUANT_LIVE=1` **and** pass `--i-understand-risk` on any `live-order` call

There is no default for `DREAM_QUANT_LIVE`. The stack never calls live broker APIs autonomously.

**Alert mapping for `ops-check`:**

| Exit | Meaning |
|------|---------|
| 0 | Healthy — deploy eligible, not halted |
| 1 | Action needed — `deploy_eligible=false`, kill switch, halt, or forward integrity fail |
| 2 | Error — missing artifacts, config, or data |

Ops alignment doc (auto-refreshed on ops-check): `artifacts/sota_audit/CHAMPION_OPS.md`

## Promotion gates (real OOS only)

Individual strategy gates + **portfolio outer walk-forward** gates. Status `READY` requires real cached/yfinance data and portfolio mean OOS Sharpe ≥ 0.8 with DD ≤ 20%. `READY_FRAGILE` indicates concentration or stability concerns while portfolio gates pass.

**Research READY ≠ deploy eligible ≠ SOTA verified.** Forward consistency gates `deploy_eligible`. López-de-Prado-grade audit gates `verified_profitable_no_overfit` in `artifacts/sota_audit/VERDICT.json` (CPCV, PBO, DSR, permutation, locked holdout).

| Gate | Threshold |
|------|-----------|
| Mean OOS Sharpe | ≥ 0.8 |
| Sharpe on ≥2 WF folds | ≥ 0.8 |
| Max OOS drawdown | ≤ 20% |
| OOS trades | ≥ 30 |
| Portfolio mean OOS Sharpe | ≥ 0.8 |
| Sharpe @ 10 bps costs | ≥ 0.5 |

Fixtures → always `NOT_READY`.

## Strategy families

- Dual momentum (absolute + vs SPY)
- Donchian breakout + vol cap
- Carry proxy (relative strength vs peer ETF)
- Momentum, mean reversion (ADX filter), RSI/SMA

Nested walk-forward param search: tune on inner folds, report outer OOS only.

## Workflow

```
fetch-data → harden-iterate → close-90d → deploy_readiness + deploy_eligible
                    ↓
     autonomous-paper --mode backfill  (one-time warm-up)
                    ↓
     cron: forward → paper-status → ops-check   (daily standing ops)
                    ↓
     ops_snapshot.json + ledger/statement.md
                    ↓
     (manual, after N forward days eligible) live-order — triple lock
```

## Live path (triple lock)

1. `artifacts/deploy_readiness.json` → `"status": "READY"`
2. `export DREAM_QUANT_LIVE=1`
3. `dream-quant live-order ... --i-understand-risk`

## Tests

```bash
pytest   # offline fixtures incl. ops-check exit codes
```

## Disclaimer

Past OOS backtests do not guarantee future results. Not financial advice. Review concentration risk (e.g. single-symbol sleeves) before any live consideration.
