# Paper Alignment Report

> Explains Sharpe differences between forward paper, full-history book, and OOS gates.

## Summary

| Metric | Sharpe |
|--------|--------|
| Forward / backfill paper | 1.021 |
| PortfolioBook full history | 1.046 |
| Portfolio OOS mean (gate) | 0.913 |
| Equal-weight, no vol cap | 1.046 |
| Equal-weight + vol/min-hold | 1.046 |

**Paper aligned with book simulator:** True

## OOS fold Sharpes (same simulator, test windows only)

- Fold 1: 1.300
- Fold 2: 0.243
- Fold 3: 1.196

## Decomposition

- OOS period selection (OOS mean − full history): **-0.134**
- Inverse-vol weights vs equal-weight: **+0.000**
- Missing vol-target / min-hold (old paper bug): **+0.000**

## Sleeve weights (inverse-vol, correlation cap)

- `SPY:risk_parity_regime:0`: 0.493
- `TLT:risk_parity_regime:0`: 0.132
- `GLD:risk_parity_regime:0`: 0.235

## Interpretation

- **Gate metric (OOS ~1.29)** averages Sharpe on three outer test windows only — not full 2005–2024.
- **Full-history book (~0.85)** is the apples-to-apples target for backfill paper after alignment.
- Forward paper is primary evidence; rolling 30/90/252d metrics in `forward_metrics.json`.
- `paper_aligned` is true when backfill Sharpe matches PortfolioBook within 0.05.
