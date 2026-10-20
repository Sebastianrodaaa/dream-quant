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
