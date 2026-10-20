# Market Fitness Rankings

> **Research/paper mode only.** Rankings from historical OHLCV features — not financial advice.

Features: dollar volume (liquidity), high-low spread proxy, annualized volatility,
ATR%, return autocorrelation, variance ratio (VR≈1 random; <1 MR-friendly; >1 trend-friendly),
estimated cost drag at configured commission+slippage.

| Rank | Symbol | Class | Fitness | Avg $Vol | Spread bps | Ann Vol | VR | Autocorr | Cost drag |
|------|--------|-------|---------|----------|------------|---------|-----|----------|-----------|
| 1 | SPY | equities_etfs | 0.786 | 20,511,187,395 | 123.8 | 19.04% | 0.81 | -0.103 | 0.0252 |
| 2 | QQQ | equities_etfs | 0.674 | 7,026,844,676 | 151.6 | 21.54% | 0.85 | -0.082 | 0.0252 |
| 3 | GLD | equities_etfs | 0.663 | 1,241,119,698 | 104.8 | 17.55% | 0.97 | -0.012 | 0.0252 |
| 4 | TLT | equities_etfs | 0.622 | 965,286,079 | 91.4 | 14.80% | 0.87 | -0.030 | 0.0252 |
| 5 | HYG | equities_etfs | 0.617 | 851,680,699 | 63.1 | 11.24% | 0.97 | 0.003 | 0.0252 |
| 6 | EFA | equities_etfs | 0.602 | 890,795,864 | 108.0 | 21.28% | 0.82 | -0.113 | 0.0252 |
| 7 | IWM | equities_etfs | 0.590 | 3,861,740,961 | 176.8 | 24.22% | 0.89 | -0.070 | 0.0252 |
| 8 | USMV | defensive_optional | 0.503 | 135,923,507 | 88.8 | 13.61% | 0.88 | -0.099 | 0.0252 |
| 9 | SPLV | defensive_optional | 0.485 | 104,092,837 | 96.3 | 14.70% | 0.83 | -0.137 | 0.0252 |
| 10 | XLE | equities_etfs | 0.411 | 910,521,732 | 209.4 | 30.14% | 0.89 | -0.060 | 0.0252 |
