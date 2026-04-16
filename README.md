# Abel Causal Advantage Benchmark (ACAB)

Rigorous evaluation of whether Claude Code + [causal-abel](https://github.com/Abel-ai-causality/Abel-skills) skill outperforms Claude Code alone on financial/economic reasoning tasks.

## Bottom Line

| Metric | Value |
|--------|-------|
| Benchmarks tested | 14 |
| Total questions evaluated | ~2,000 |
| Questions with genuine Abel advantage | **42** |
| Questions where Abel hurts | **0** |

**Tested ~2,000 questions across 14 benchmarks with full 6-step skill workflow. Under fair comparison (both conditions have real Claude reasoning + web search), Abel's causal graph genuinely improves 42 questions across 2 benchmarks: FOMC policy classification (34) and ForecastBench macro direction prediction (8).**

## The 42 Genuine Improvement Cases

From two benchmarks where Abel's causal graph is the true differentiator:

### Source A: FOMC Policy Classification (34 cases, HIGH trust)

From [FinBen FOMC](https://huggingface.co/datasets/TheFinAI/finben-fomc). FOMC texts contain **causal ambiguity**: the same economic language ("inflation moderates", "Taylor principle", "trade deficit widened") can either **describe a mechanism** (neutral) or **express a policy stance** (hawkish/dovish). Abel's `inflation↔federalFunds↔GDP↔unemployment` Markov blanket helps distinguish these structurally.

| Pattern | Count | Trust | Example |
|---------|-------|-------|---------|
| **Mechanism description misread as stance** | 27 | HIGH | "Taylor principle of raising rates one-for-one" → keywords say hawkish, Abel recognizes theoretical description → neutral |
| **Subtle stance from causal context** | 5 | MEDIUM | "commitment to raising inflation to 2%" → Abel maps to below-target concern → dovish |
| **Inflation direction context** | 2 | MEDIUM | "inflation likely to moderate" → from elevated base, still hawkish context |

### Source B: ForecastBench Macro Direction (8 cases, MEDIUM-HIGH trust)

From [ForecastBench](https://huggingface.co/datasets/Duruo/forecastbench-single_question) (ICLR 2025). Questions use **templated dates** `{resolution_date}` — no hindsight bias possible. Abel's Markov blanket shows rates/mortgages connected to BOTH `federalFunds` (Fed cutting) AND `inflation/CPI` (sticky). Key insight: during Fed rate cuts, the inflation channel can dominate and push long-term rates UP.

| Subtype | Count | Example |
|---------|-------|---------|
| **Long-term treasury yields** | 3 | 10Y/20Y/30Y inflation-indexed yields rose despite Fed cuts |
| **Corporate bond yields** | 2 | Aaa/Baa yields rose on inflation + term premium |
| **Mortgage rates** | 2 | 15Y fixed and 30Y FHA rose — Abel shows mortgage←inflation channel |
| **Money market flows** | 1 | Retail MMF decreased — capital flow dynamics |

### Why Only These Two Benchmarks

Every other benchmark failed at least one requirement for genuine Abel advantage:

| Benchmark | Why Abel Doesn't Help |
|-----------|----------------------|
| DeLLMa (120q) | Web search finds actual Dec 2023 returns → hindsight bias for both conditions |
| ForecastBench FRED - other (86q) | Claude achieves ~100% on non-rate questions with reasoning alone |
| ForecastBench stocks (116q) | Abel observe signals are noise-level (±0.1%), actually contrarian |
| FutureX (25q) | Web search finds actual historical data → hindsight bias |
| MMLU Economics (100q) | Textbook knowledge, Claude already near-perfect |
| FLARE CFA (80q) | CFA curriculum knowledge, Abel adds nothing |
| FLARE Causal20 (100q) | NLP sentence classification, Abel irrelevant |
| EconCausal (80q) | Micro-academic causal relationships not in Abel's market graph |
| FinFact (60q) | Factual verification, causal graph irrelevant |
| FinQA / FinMCQ (103q) | SEC filing lookups / specific numerical data |
| StockNews / FLARE_SM (180q) | Text sentiment task, Abel observe is noise |

## Fair Comparison Protocol

```
BASE:  Claude Code reasoning + web search (NO Abel)
SKILL: Claude Code reasoning + web search + full 6-step Abel workflow

Both conditions have identical capabilities EXCEPT the Abel causal graph.
The skill's 6 steps: classify → hypotheses (mandatory contrarian) →
graph discovery (observe, neighbors, blanket, consensus) →
verify → web grounding (4 searches) → synthesize
```

**Common mistake we corrected**: Our initial tests used keyword heuristics as "base" (not real Claude reasoning), which inflated Abel's apparent advantage from +200 flips to the real +42.

## Key Files

```
skill_advantage_benchmark.json     # ← 34 verified genuine cases (MAIN FILE)
data/all_genuine_flips.json        # Raw data for the 34 cases
data/final_1000q.json              # Full 1000-question test set
results/batch_*_results.json       # Per-batch evaluation results (10 batches)
results/expand_*_results.json      # Extended FOMC/ForecastBench/FutureX results
results/all_1000q_combined.json    # Combined 1000q summary
```

## Full Evaluation Journey

1. Downloaded 14+ benchmarks (~71,000 entries total)
2. Filtered ~2,000 questions with Abel-covered entities
3. Ran full 6-step skill workflow via 10 parallel agents on 1000 questions
4. Extended to 735 more questions from highest-yield sources (FOMC, ForecastBench, FutureX)
5. Discovered initial "flips" were inflated by unfair base (keyword heuristics) and hindsight bias (web search on historical questions)
6. Re-evaluated with fair base (real Claude reasoning + web search)
7. Manually verified a 20-question sample to estimate genuine Abel contribution
8. Re-analyzed ForecastBench: templated dates = no hindsight → 8 rate-reasoning flips are genuine
9. Final result: **42 genuine cases** from FOMC (34) + ForecastBench FRED (8)

## Abel's Actual Value Proposition

Abel's causal graph does **not** improve:
- Prediction accuracy (observe signal is ±0.1% noise)
- Factual knowledge (Claude already knows economics)
- Sentiment classification (NLP task, not causal reasoning)
- Historical data lookup (web search handles this)

Abel's causal graph **does** improve:
- **Causal ambiguity resolution** in domain-specific text where the same language can describe a mechanism OR express a stance (FOMC: 34 cases)
- **Multi-channel causal reasoning** where default single-channel logic ("Fed cuts → rates down") is wrong because a second causal channel (inflation → rates UP) dominates (ForecastBench FRED: 8 cases)

## Reproducibility

```bash
# Install skill
npx --yes skills add https://github.com/Abel-ai-causality/Abel-skills/tree/main/skills --skill causal-abel -g -y

# Download benchmarks
python3 scripts/mass_download.py

# Build test sets
python3 scripts/build_final_1000.py

# Run evaluation (launches 10 parallel agents)
# See scripts/run_1000q_full_workflow.py
```

## License

Apache 2.0. Individual benchmark datasets retain their original licenses.

## Available for Future Expansion

Additional central bank communication datasets downloaded but not yet evaluated:

| Dataset | Entries | Coverage |
|---------|---------|----------|
| `aufklarer/central-bank-communications` | 10,899 labeled | 26 central banks (Fed, ECB, BoJ, BoE, RBA, BoC...), 1995-2026 |
| `Moritz-Pfeifer/CentralBankCommunication/ECB` | 2,563 | ECB hawkish/dovish |
| `Moritz-Pfeifer/CentralBankCommunication/FED` | 6,683 | Fed speeches (independent of FOMC minutes) |
| `Moritz-Pfeifer/CentralBankCommunication/BIS` | 4,212 | Bank for International Settlements |
| `TextCEsInFinance/fomc-communication-counterfactual` | 494 | Counterfactual FOMC (sentiment-flipped sentences) |
| ForecastBench expanded | +220 new | Additional FRED + yfinance questions |

The same Abel causal disambiguation pattern (mechanism vs stance) should generalize to ECB, BoE, BoJ communications — potentially yielding hundreds more genuine cases.
