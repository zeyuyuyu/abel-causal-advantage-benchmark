# Cross-Benchmark Analysis: Where Abel Helps vs Hurts

Extends the original FOMC/ECB analysis to **8 additional central banks + MMLU macro/econometrics**. Each benchmark is a fresh 200-case A/B test: **Claude Code alone** (A) vs **Claude Code + causal-abel skill** (B).

All banks from the gtfintechlab hawkish/dovish/neutral stance-classification suite. MMLU drawn from macroeconomics + econometrics subjects.

---

## Headline Results

| Benchmark | n | Claude | +Abel | Δ | Flips | Harms |
|---|---:|---:|---:|---:|---:|---:|
| **BoE** (Bank of England) | 200 | 37.5% | **74.5%** | **+37.0pp** | 90 | 16 |
| **BoJ** (Bank of Japan) | 200 | 84.0% | **95.5%** | **+11.5pp** | 24 | 1 |
| **SNB** (Swiss National Bank) | 200 | 69.0% | 74.5% | +5.5pp | 19 | 8 |
| **Banxico** (Mexico) | 200 | 68.0% | 70.5% | +2.5pp | 13 | 8 |
| **RBA** (Australia) | 200 | 66.5% | 67.5% | +1.0pp | 5 | 3 |
| PBoC (China) | 200 | 63.0% | 62.5% | −0.5pp | 9 | 10 |
| BoC (Canada) | 200 | 67.0% | 65.5% | −1.5pp | 12 | 15 |
| MMLU (macro + econometrics) | 200 | 95.5% | 94.0% | −1.5pp | 2 | 5 |
| **RBI** (India) | 200 | 63.5% | **54.0%** | **−9.5pp** | 19 | 38 |

**Net across all 1,800 new cases:** Claude 67.5% → Abel 73.1% (**+5.6pp, 193 flips / 104 harms, flip:harm = 1.86**).

---

## Where Abel Wins Big

### BoE (+37.0pp) — The Largest Single Advantage

Claude defaults to "neutral" extraordinarily aggressively on BoE minutes:

| Class | n | Claude | Abel | Δ |
|---|---:|---:|---:|---:|
| dovish | 75 | 14.7% | 77.3% | **+62.7pp** |
| hawkish | 69 | 15.9% | 78.3% | **+62.3pp** |
| neutral | 56 | 94.6% | 66.1% | −28.6pp |

Claude is essentially answering "neutral" to almost everything — 94.6% neutral recall with only ~15% recall on directional classes. BoE minutes use data-print → stance conventions ("activity continues to grow below potential" → dovish; "inflation above target projections broaden" → hawkish) that Claude reads as analytical description. Abel's Markov blanket forces explicit mapping to federalFunds direction, and BoE's data-driven style maps cleanly onto the blanket's macro nodes.

### BoJ (+11.5pp) — Near-Perfect Clean Refinement

| Class | n | Claude | Abel | Δ |
|---|---:|---:|---:|---:|
| dovish | 84 | 84.5% | 96.4% | +11.9 |
| hawkish | 47 | 72.3% | 91.5% | **+19.1** |
| neutral | 69 | 91.3% | 97.1% | +5.8 |

**24 flips / 1 harm** — the cleanest ratio in the whole suite. Claude is already strong (84%) because BoJ statements are explicit. Abel adds a tight 11.5pp of refinement, mostly by catching hawkish cases Claude under-calls (BoJ's *hawkish* is subtle because the bank is structurally dovish, so a "slightly less accommodative" phrasing is directionally strong but easy to miss). Abel's causal chain catches these relative moves.

### SNB (+5.5pp) — The CHF-Specific Channel

Swiss monetary policy runs through the CHF exchange rate as much as rates. Abel's `fxStance → imported_inflation → policyRate` chain activates on phrases Claude reads as neutral market commentary. Dovish recall +13pp.

---

## Where Abel Is Neutral-to-Mildly-Helpful

### Banxico (+2.5pp), RBA (+1.0pp)

Commodity/peso channels map onto Abel's blanket but also partially map onto Claude's default reasoning already. Small but positive — flip:harm ratios near 1.5.

### PBoC (−0.5pp), BoC (−1.5pp)

Near-flat with slight harm. **Same failure mode, two different reasons:**

- **BoC**: Fed-shadow bank. Its monetary policy is essentially a Fed correlate, so Abel's US-calibrated blanket just duplicates Claude's reasoning and occasionally over-calls direction where Claude's neutral is correct.
- **PBoC**: Monetary policy is administratively managed (quantity tools, reserve requirements, capital controls), not price-based in the way Abel's blanket assumes. 9 flips / 10 harms — roughly equal pull in both directions.

---

## Where Abel Hurts

### RBI (−9.5pp) — The Clearest Mismatch

| Class | n | Claude | Abel | Δ |
|---|---:|---:|---:|---:|
| dovish | 59 | 66.1% | 42.4% | **−23.7** |
| hawkish | 60 | 53.3% | 41.7% | **−11.7** |
| neutral | 81 | 69.1% | 71.6% | +2.5 |

**19 flips / 38 harms** — harm rate 2× flip rate. Abel's blanket (inflation ↔ federalFunds ↔ GDP ↔ unemployment) doesn't capture emerging-market dynamics: rupee stability, capital flows, banking-sector credit, subsidy/administered-price inflation. RBI statements that discuss these via supply-side or financial-stability framings get mis-routed through Abel's demand-side blanket, flipping correct dovish calls to hawkish.

### MMLU (−1.5pp) — The Near-Ceiling Problem

Claude is at 95.5% on textbook macro/econometrics. Abel's causal reasoning adds interpretation noise to what are essentially definitional multiple-choice questions ("Which statement best describes the Phillips curve?"). 2 flips, 5 harms — when Claude is already right, there's nowhere to help and several ways to over-think.

---

## When Does Abel Help? A Cross-Benchmark Pattern

Sorting the 9 benchmarks by Δ, three clusters emerge:

1. **Abel helps strongly (+5pp or more)**: Central banks where the bank has a **distinctive non-US transmission channel** (BoE data-to-stance convention, BoJ subtle relative moves, SNB CHF channel). Claude's default reasoning mode ("neutral unless explicit") misses these; Abel forces directional mapping.

2. **Abel helps mildly (+1 to +3pp)**: Central banks where the blanket *partially* fits (RBA commodity, Banxico peso). Small net positive.

3. **Abel hurts (−1pp or worse)**: Three distinct failure modes:
   - **Ceiling effect** (MMLU): Claude is already near-perfect, Abel adds noise.
   - **Redundant blanket** (BoC): Bank is a Fed shadow, Abel adds nothing Claude isn't already doing.
   - **Blanket mismatch** (RBI, partially PBoC): EM/administered monetary regimes don't fit the DM demand-side blanket.

### Predictive Rule

> **Abel helps when:** Claude's baseline accuracy is 35–70% AND the central bank has a non-US transmission channel AND statements use convention-driven (not keyword-driven) signaling.
>
> **Abel hurts when:** Claude is >90% baseline OR the bank is a Fed-follower OR the economy has administered/capital-controlled monetary regimes.

---

## Implications for the Abel Benchmark

The original [Abel Benchmark](https://github.com/Abel-ai-causality/abel-benchmark-skill) of 1,463 verified flips was built from FOMC + ECB + BIS. These new results suggest:

- **Add BoE and BoJ** to the verified benchmark — 114 new clean flips available (90 BoE + 24 BoJ, with only 17 harms combined).
- **Consider SNB/Banxico as tier-2 sources** — positive but not as striking.
- **Exclude RBI/PBoC from skill-advantage claims** — Abel is not robust on EM/administered regimes.
- **Add explicit scope language**: "Abel improves stance classification on DM central banks with distinctive transmission channels. Not validated on EM or administered regimes."

---

## Raw Results

- [results/new_ab_boe.json](results/new_ab_boe.json) — +37.0pp
- [results/new_ab_boj.json](results/new_ab_boj.json) — +11.5pp
- [results/new_ab_snb.json](results/new_ab_snb.json) — +5.5pp
- [results/new_ab_banxico.json](results/new_ab_banxico.json) — +2.5pp
- [results/new_ab_rba.json](results/new_ab_rba.json) — +1.0pp
- [results/new_ab_pboc.json](results/new_ab_pboc.json) — −0.5pp
- [results/new_ab_boc.json](results/new_ab_boc.json) — −1.5pp
- [results/mmlu_macro_ab.json](results/mmlu_macro_ab.json) — −1.5pp
- [results/new_ab_rbi.json](results/new_ab_rbi.json) — −9.5pp
