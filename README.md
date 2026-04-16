# Abel Skill Advantage Benchmark

**1,463 verified cases** where **Claude Code + [causal-abel](https://github.com/Abel-ai-causality/Abel-skills) skill** correctly answers while **Claude Code alone** gets wrong.

Every case comes from real A/B testing on **15,624 central bank communication questions**.

## Results at a Glance

| | Count | Rate |
|---|---|---|
| Total questions tested (real A/B) | **15,624** | 100% |
| Abel wins (Claude wrong → Abel right) | **1,463** | 9.4% |
| Abel loses (Claude right → Abel wrong) | 760 | 4.9% |
| Both correct | ~8,500 | ~54% |
| Both wrong | ~4,900 | ~31% |
| **Net improvement** | **+703** | **+4.5%** |

## What Was Tested

15,624 central bank monetary policy communications from 6 datasets:

| Dataset | Entries | Source | Task |
|---------|---------|--------|------|
| FinBen FOMC | 496 | TheFinAI/finben-fomc | Hawkish/Dovish/Neutral |
| FinanceMTEB FOMC | 2,281 | FinanceMTEB/FOMC | Hawkish/Dovish/Neutral |
| GTFinTech FOMC | 149 | gtfintechlab/fomc_communication | Hawkish/Dovish/Neutral |
| Moritz ECB | 2,563 | Moritz-Pfeifer/CentralBankCommunication/ECB | Hawkish/Dovish |
| Moritz FED | 6,618 | Moritz-Pfeifer/CentralBankCommunication/FED | Hawkish/Dovish |
| Moritz BIS | 4,047 | Moritz-Pfeifer/CentralBankCommunication/BIS | Hawkish/Dovish |
| **Total (deduplicated)** | **15,624** | | |

## How Each Question Was Tested

Every question went through two conditions:

**Condition A — Claude Code (no Abel):**
- Agent reads the central bank text
- Classifies as hawkish/dovish/neutral using pure economic reasoning
- No Abel API calls, no causal graph

**Condition B — Claude Code + Abel Skill (full 6-step workflow):**
1. **Classify**: Map to macro nodes (federalFunds, inflationRate, GDP, unemploymentRate)
2. **Hypotheses**: Generate including mandatory contrarian
3. **Graph discovery**: Run real `graph.markov_blanket` API calls via `cap_probe.py` against `https://cap.abel.ai/api`
4. **Verify**: Use blanket structure (inflation↔federalFunds↔GDP↔unemployment) to disambiguate
5. **Web grounding**: Where applicable
6. **Synthesize**: Final classification informed by causal structure

**Scoring**: Both answers independently compared to ground truth label.

A question enters this benchmark only if: **Condition A is wrong AND Condition B is correct.**

## Why Abel Helps

Abel's Markov blanket (`inflation↔federalFunds↔GDP↔unemployment`) resolves **causal ambiguity** in central bank text:

| Pattern | Example | Claude says | Abel says | Truth |
|---------|---------|-------------|-----------|-------|
| Mechanism description misread as stance | "Taylor principle of raising rates in response to inflation" | hawkish | **neutral** | neutral |
| Economic strength misread as neutral | "Credit conditions continued to ease, CRE loans growing" | neutral | **hawkish** | hawkish |
| Subtle dovish concern missed | "Commitment to raising inflation to 2 percent" | neutral | **dovish** | dovish |
| Surface sentiment contradicts direction | "Inflation likely to moderate" (from high base) | dovish | **hawkish** | hawkish |
| Dual-channel rate reasoning | "Will 15Y mortgage rate have increased?" (Fed cuts but inflation sticky) | decrease | **increase** | increase |

## Where Abel Helps Most (and Least)

| Data type | Abel advantage | Why |
|-----------|---------------|-----|
| **FOMC 3-class** (hawk/dove/neutral) | **Strong** (+8-15pp) | Abel excels at distinguishing neutral mechanism descriptions from directional stances |
| **ECB hawkish** | **Strong** (+12-15pp) | ECB "structural reform" language reads neutral to Claude but is hawkish in ECB context |
| **BIS hawkish** | **Strong** (+15pp) | Similar to ECB — institutional language that implies hawkish stance |
| **Mixed dovish** | **Moderate** (+5-12pp) | Abel helps identify subtle dovish signals in analytical language |
| **Moritz FED binary** | **Weak** (0 to -1pp) | Without neutral class, Abel's main advantage (mechanism vs stance) disappears |
| **Homogeneous batches** | **Negligible** | When all labels are same class, disambiguation provides no edge |

## Files

```
skill_advantage_benchmark_1000.json  # ← THE BENCHMARK: 1,463 verified Abel-wins cases
data/all_flips_final.json            # Same data, raw format
results/cb_batch_*_ab.json           # Complete A/B results for all 33 batches (15,624 questions)
data/all_central_bank_unique.json    # Source data (15,624 deduplicated entries)
data/cb_batch_*.json                 # Input batches (500 questions each)
```

## Reproducibility

```bash
# Install Abel skill
npx --yes skills add https://github.com/Abel-ai-causality/Abel-skills/tree/main/skills --skill causal-abel -g -y

# Download central bank datasets
python3 scripts/mass_download.py

# Build deduplicated pool
# (see scripts/build_final_1000.py for entity extraction logic)

# Run A/B test (launches parallel agents, each processing 500 questions)
# Each agent: reads batch → classifies with pure Claude → runs Abel API → reclassifies → scores
# See results/cb_batch_*_ab.json for outputs
```

## Limitations

1. **Abel also causes 760 harms** (Claude right → Abel wrong, 4.9% rate). This benchmark only contains the wins.
2. **Abel's advantage concentrates on 3-class tasks** (hawk/dove/neutral). On binary tasks without neutral, the advantage shrinks or disappears.
3. **The "base Claude" is an Agent's reasoning**, not a controlled Claude API call. Different Claude instances may produce different base answers.
4. **Central bank text classification is the only domain tested**. Abel's causal graph may help on other tasks (macro prediction, financial reasoning) but those were not verified at this scale.

## License

Apache 2.0. Source datasets retain their original licenses.
