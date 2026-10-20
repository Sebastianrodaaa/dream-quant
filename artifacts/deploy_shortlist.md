# Paper Deploy Shortlist

> **NOT PROMOTION-READY — research only**
> Data: `cache` | Real data — verify deploy_readiness.json before paper-daemon

| Symbol | Strategy | Mean OOS Sharpe | Gates | Max DD | Composite |
|--------|----------|-----------------|-------|--------|-----------|
| SPY | safe_haven | 0.945 | FAIL | 0.00% | 0.945 |
| QQQ | absolute_momentum | 1.200 | PASS | -10.80% | 1.200 |
| SPY | absolute_momentum | 1.089 | PASS | -13.15% | 1.089 |
| USMV | absolute_momentum | 1.039 | PASS | -11.67% | 1.039 |
| QQQ | safe_haven | 0.948 | PASS | -10.80% | 0.948 |
| HYG | dual_momentum | 0.898 | FAIL | -4.12% | 0.898 |
| QQQ | dual_momentum | 0.843 | PASS | -12.46% | 0.843 |
| SPLV | absolute_momentum | 0.836 | PASS | -11.02% | 0.836 |

## Risk notes

- Worst drawdown in list: **-13.15%**
- Symbols: SPY, QQQ, USMV, HYG, SPLV

## What NOT to deploy

- **SPY** / safe_haven: Failed promotion gates (mean OOS Sharpe 0.95)
- **HYG** / dual_momentum: Failed promotion gates (mean OOS Sharpe 0.90)
- **HYG** / safe_haven: Failed promotion gates (mean OOS Sharpe 0.76)
- **USMV** / *: Low market fitness (0.50)
- **SPLV** / *: Low market fitness (0.49)
- **XLE** / *: Low market fitness (0.41)
