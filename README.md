# Abel Causal Advantage Benchmark (ACAB)

Rigorous evaluation of whether Claude Code + [causal-abel](https://github.com/Abel-ai-causality/Abel-skills) skill outperforms Claude Code alone on financial/economic reasoning tasks.

## Bottom Line

| Metric | Value |
|--------|-------|
| Benchmarks tested | 14 |
| Total questions evaluated | ~2,000 |
| Questions with genuine Abel advantage | **34** |
| Questions where Abel hurts | **0** |

**Tested ~2,000 questions across 14 benchmarks with full 6-step skill workflow. Under fair comparison (both conditions have real Claude reasoning + web search), Abel's causal graph genuinely improves 34 questions — all in FOMC monetary policy text classification.**

## The 34 Genuine Improvement Cases

All 34 are from [FinBen FOMC](https://huggingface.co/datasets/TheFinAI/finben-fomc) (Federal Reserve hawkish/dovish/neutral classification).

### Why Abel Helps Here

FOMC texts contain **causal ambiguity**: the same economic language ("inflation moderates", "Taylor principle", "trade deficit widened") can either **describe a mechanism** (neutral) or **express a policy stance** (hawkish/dovish). Abel's `inflation↔federalFunds↔GDP↔unemployment` Markov blanket helps distinguish these two cases structurally.

### Flip Patterns

| Pattern | Count | Trust | Example |
|---------|-------|-------|---------|
| **Mechanism description misread as stance** | 27 | HIGH | "Taylor principle of raising rates one-for-one" → keywords say hawkish, Abel recognizes theoretical description → neutral |
| **Subtle stance from causal context** | 5 | MEDIUM | "commitment to raising inflation to 2%" → Abel maps to below-target concern → dovish |
| **Inflation direction context** | 2 | MEDIUM | "inflation likely to moderate" → from elevated base, still hawkish context |

### Why Only FOMC

Every other benchmark failed at least one of these requirements for genuine Abel advantage:

| Benchmark | Why Abel Doesn't Help |
|-----------|----------------------|
| DeLLMa (120q) | Web search finds actual Dec 2023 returns → hindsight bias for both conditions |
| ForecastBench FRED (98q) | Claude achieves **100%** with pure economic reasoning alone |
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

**Common mistake we corrected**: Our initial tests used keyword heuristics as "base" (not real Claude reasoning), which inflated Abel's apparent advantage from +200 flips to the real +34.

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
8. Final result: **34 genuine cases**, all FOMC policy text classification

## Abel's Actual Value Proposition

Abel's causal graph does **not** improve:
- Prediction accuracy (observe signal is ±0.1% noise)
- Factual knowledge (Claude already knows economics)
- Sentiment classification (NLP task, not causal reasoning)
- Historical data lookup (web search handles this)

Abel's causal graph **does** improve:
- **Causal ambiguity resolution** in domain-specific text where the same language can describe a mechanism OR express a stance
- Specifically: FOMC monetary policy text where `inflation↔federalFunds↔GDP` structure disambiguates theoretical descriptions from policy positions

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
