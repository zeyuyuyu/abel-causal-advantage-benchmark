# Abel Causal Advantage Benchmark (ACAB) v2.0

100 real questions from existing benchmarks where **Claude Code + [causal-abel](https://github.com/Abel-ai-causality/Abel-skills) skill** provides causal graph signal unavailable to **Claude Code alone**.

**Every question is taken directly from its source benchmark — no custom-designed questions.**

## Question Sources

| Source Benchmark | Category | Questions | Paper |
|-----------------|----------|-----------|-------|
| [DeLLMa](https://github.com/DeLLMa/DeLLMa) | Stock investment decision | 50 | ICLR 2025 |
| [ForecastBench](https://forecastbench.org) | Macro indicator prediction | 35 | ICLR 2025 |
| [FutureX-Past](https://huggingface.co/datasets/futurex-ai/Futurex-Past) | Market/macro prediction | 11 | arXiv:2508.11987 |
| [ForecastBench](https://forecastbench.org) | Stock direction prediction | 4 | ICLR 2025 |
| **Total** | | **100** | |

## How Questions Were Selected

```
5 benchmarks downloaded (~10K questions total)
    → 412 economics/finance questions identified
        → 154 matched to Abel graph nodes (equities + macro indicators)
            → 144 confirmed with live Abel API signal (1s rate-limited)
                → 100 selected (maximize source diversity)
```

Also tested but excluded:
- **EconCausal** (2943 questions): 0/15 sampled had Abel coverage — micro-academic causal relationships not in Abel's market graph
- **CLadder** (6952 questions): Abstract formal causal logic, not Abel's empirical domain

## What Abel Provides Per Category

| Category | Abel Signal | Example |
|----------|-----------|---------|
| Stock decision (DeLLMa) | `observe` prediction + `neighbors` (structural drivers) for each Abel-covered stock | META observe: -0.0017, parents: Evaxion Biotech, FIGS, D-Market |
| Macro prediction (ForecastBench FRED) | `graph.markov_blanket` — complete informational neighborhood of macro indicator | CPI blanket: GDP, Fed Funds, Mortgage Rates, Consumer Sentiment, ... (20 nodes) |
| Stock direction (ForecastBench yfinance) | `observe` directional prediction + structural parents | INTC observe: +0.0013, 10 parents identified |
| Market prediction (FutureX) | `observe` + `neighbors` for equities; `markov_blanket` for macro nodes | AAPL observe: +0.0025 (slightly bullish) |

## Files

```
abel_advantage_benchmark_v2.json   # ← THE BENCHMARK (100 real questions, main file)
abel_advantage_benchmark_v1.json   # v1 prototype (custom-designed questions)
abel_advantage_benchmark.json      # Initial 8-question A/B test prototype
data/
  dellma_stock_questions.json      # 120 DeLLMa stock decision prompts
  forecastbench_financial.json     # 214 ForecastBench financial questions
  futurex_past.json                # 388 FutureX-Past questions
  econcausal.json                  # 2943 EconCausal entries
  cladder_rung23.json              # 6952 CLadder rung 2-3 questions
results/
  v3_with_signal.json              # 144 questions with confirmed Abel signal
  v3_all_tested.json               # All 154 tested questions
  ab_test_scored.json              # Original A/B test scores (22 questions)
  econcausal_ab.json               # EconCausal A/B results (0 coverage)
  graph_exploration.json           # Abel graph coverage exploration
  benchmark_validation.json        # API validation results
scripts/                           # All evaluation and generation scripts
```

## How to Evaluate

1. **Control**: Claude Code answers each question using only base reasoning + web search (no Abel)
2. **Treatment**: Claude Code answers using full `causal-abel` skill (observe, neighbors, markov_blanket, etc.)
3. **Score**: Compare both answers against ground truth
   - Binary/choice questions: exact match (1=correct, 0=wrong)
   - Numeric questions: `1 - min(1, |pred - actual| / actual)`
4. **Report**: Per-source and per-category accuracy, paired significance test

## Abel Graph Coverage

- **17 equities with structure**: AAPL, AMZN, ASML, AVGO, BAC, GS, GOOG, INTC, JPM, META, MS, MSFT, QCOM, TSM, TSLA, TXN, WFC
- **13 macro nodes with Markov blankets**: Treasury 10Y, Fed Funds, CPI, Inflation, GDP, Real GDP, Unemployment, 30Y Mortgage, 15Y Mortgage, Consumer Sentiment, Durable Goods, Initial Claims, Industrial Production
- **Abel operations**: observe_predict, neighbors (parents/children), graph.markov_blanket, discover_consensus, discover_deconsensus, discover_fragility, paths, intervene_time_lag

## Benchmarks Tested

| Benchmark | Questions | Abel Coverage | Included |
|-----------|-----------|--------------|----------|
| DeLLMa (stocks) | 120 | 94 (78%) | 50 |
| ForecastBench (financial) | 214 | 39 (18%) | 39 |
| FutureX-Past (financial) | 78 | 21 (27%) | 11 |
| EconCausal | 2943 | 0 (0%) | 0 |
| CLadder | 6952 | 0 (0%) | 0 |

## License

Apache 2.0
