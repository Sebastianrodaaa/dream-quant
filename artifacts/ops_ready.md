# Paper Ops Autonomy — Ready

Generated: 2026-09-18

## Standing ops path

| Step | Command | Output |
|------|---------|--------|
| 1 | `dream-quant autonomous-paper --mode forward` | New bars, kill switches, forward state |
| 2 | `dream-quant paper-status` | Daily summary, readiness refresh |
| 3 | `dream-quant ops-check` | Exit code for cron/monitoring |

**Cron:** `./scripts/cron_forward_paper.sh` runs all three in order.

## Machine-readable snapshot

`artifacts/paper/ops_snapshot.json` — written by `paper-status` and forward paper:

- `deploy_eligible`, `research_status`, `paper_aligned`
- `rolling_sharpe_30/90/252`, `equity`, `last_bar`
- `halted`, `halt_reason`, `kill_switch_trips`
- `timestamp` (UTC)

## ops-check exit codes

| Code | Meaning |
|------|---------|
| 0 | Healthy — deploy eligible, not halted, no kill trips |
| 1 | `deploy_eligible=false`, halted, or kill switch tripped |
| 2 | Error (missing config/artifacts/data) |

## Shadow ledger (simulated)

`artifacts/paper/ledger/` — account statement style artifacts:

- `account.json`, `positions.json`, `fills.jsonl`, `statement.md`
- All entries marked `simulated: true` — not a real brokerage.

## Current status (last run)

- **deploy_eligible:** true
- **halted:** false
- **kill_switch_trips:** 0
- **Rolling 90d Sharpe:** ~1.58

## Live trading

**Not enabled.** Eligibility ≠ live. Triple lock remains:

1. `deploy_readiness.json` → READY
2. `DREAM_QUANT_LIVE=1` (never set by default)
3. `--i-understand-risk` on `live-order`

No live broker APIs are called by cron or paper mode.
