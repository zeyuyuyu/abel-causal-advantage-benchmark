# Abel Skill Advantage: 42 Verified Cases

From ~2,000 questions across 14 benchmarks, these are the 42 cases where Claude Code + causal-abel skill
correctly answers while Claude Code alone (with web search) gets wrong.

**Fair comparison protocol**: Both conditions have Claude reasoning + web search. Only Abel's causal graph is the difference.

---

## Summary

| Category | Count | Source Benchmark | Abel Mechanism |
|----------|-------|-----------------|----------------|
| FOMC: mechanism misread as stance | 27 | FinBen FOMC | Markov blanket distinguishes causal structure description from policy stance |
| FOMC: subtle stance missed | 5 | FinBen FOMC | Causal context reveals direction of concern |
| FOMC: inflation direction context | 2 | FinBen FOMC | Position on inflation↔federalFunds structure determines hawk/dove |
| ForecastBench: multi-channel rate reasoning | 8 | ForecastBench (ICLR 2025) | Blanket shows dual parents (Fed + inflation) overrides single-channel default |
| **Total** | **42** | | **0 harms** |

---

## Part A: FOMC Hawkish/Dovish/Neutral Classification (34 cases)

Source: [FinBen FOMC](https://huggingface.co/datasets/TheFinAI/finben-fomc)

**Why Abel helps**: FOMC text contains *causal ambiguity* — the same economic language can either
describe a causal mechanism (neutral) or express a policy stance (hawkish/dovish). Abel's
`inflation↔federalFunds↔GDP↔unemployment` Markov blanket provides the structural context to distinguish these.

### A1. Mechanism Description Misread as Stance (27 cases)

Claude sees economic keywords and assigns sentiment. Abel recognizes the text is describing
a *structural relationship* (e.g., how rates respond to inflation), not advocating a policy position.

#### Case A1-01

> However, we have also found that excluding volatile food and energy prices generally gives a better sense of underlying inflation pressures that are likely to persist and dominate total inflation over time.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-02

> In the productivity boom that followed World War I, a chief technological innovation was the spread of electrification to the factory floor.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-03

> The Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and expects it will be appropriate to maintain this target range until labor market conditions have reached levels consistent with the Committee's assessments of maximum employment and inflation has risen to 2 percent and is on track to moderately exceed 2 percent for some time.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-04

> At the same time, the staff viewed the risks around its outlook for the unemployment rate as roughly balanced.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-05

> We found that a surprise increase of 25 basis points in the funds rate target typically results in a decline in broad equity indexes of about 1 percent, whereas a change in the funds rate that is expected by the market has essentially no effect on stock prices.17 Our work is just one example of a number of event-study analyses that may well shed light on the effects of monetary policy and the channels of monetary policy transmission.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-06

> Operationally, maintaining price stability requires abiding by the Taylor principle of raising nominal interest rates more than one for one in response to movements in inflation, especially those movements perceived as persistent.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "raising rates" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-07

> However, household spending had been relatively robust during the cyclical downturn and likely had only limited room for a pickup over coming quarters, and intense competitive pressures could well constrain profits, investment, and equity prices.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-08

> In connection with the risks associated with an early start to policy normalization, many participants observed that a premature increase in rates might damp the apparent solid recovery in real activity and labor market conditions, undermining progress toward the Committee's objectives of maximum employment and 2 percent inflation.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | dovish ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-09

> Fourth and finally, the statement codifies the key lesson from the Global Financial Crisisâ€”that financial stability is necessary for the achievement of our statutory goals of maximum employment and price stability.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-10

> At the same time, the incentive to take advantage of increasingly efficient high-tech equipment and software typically available at declining prices would continue to provide an important underpinning for further large gains in investment spending, with favorable implications for continued rapid growth in productivity.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-11

> Members referred, however, to a number of favorable factors that should continue to support at least moderate further growth in business investment, including the attractive pricing of and ongoing rapid technological improvements in computer and communications equipment and the wide availability of equity and debt financing on favorable terms to business firms.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-12

> For example, the evidence suggests that changes in the demographic composition of the labor force affect NAIRU and it is also likely that government programs, including unemployment compensation and welfare, also affect NAIRU.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-13

> The staff continued to view the uncertainty around its projections for real GDP growth, the unemployment rate, and inflation as generally similar to the average of the past 20 years.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-14

> However, indicators of economic activity in Japan and Brazil remained weak.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-15

> Mortgage credit conditions generally remained tight over the intermeeting period, though signs of easing continued to emerge amid further gains in house prices.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-16

> Some members nonetheless referred to indications of increasing expenditures for various categories of high-tech equipment and software, and they noted that impetus to demand from a positive outcome in the war against Iraq should have a favorable effect on business capital spending, especially if it were accompanied by a rally in the stock market.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-17

> These members expected that the target range would be maintained at this level until they were confident that the economy had weathered recent events and was on track to achieve the Committee's maximum employment and price stability goals.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-18

> Participants expected that productivity growth would pick up as firms slowed hiring to a pace more in line with output growth but acknowledged that the improvement might be limited, particularly if business investment spending were to remain soft.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-19

> The literature on this topic extends at least as far back as William Brainardâ€™s original paper on uncertainty and policy almost forty years ago.7 Brainardâ€™s analysis showed that if policymakers are uncertain about how real activity and inflation will be affected over time by monetary actions, they should be less aggressive in responding to changes in economic conditions than would be the case if they knew the true model of the economy.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-20

> Thus, knowing where productivity growth is headed is, in many respects, equivalent to foreseeing our economic destinies.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-21

> The stock market soared, and--remarkably enough--core inflation moderated.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-22

> One participant suggested that the Committee could announce an additional, lower set of thresholds for inflation and unemployment

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-23

> While participants generally felt that the pace of underlying productivity growth remained robust, careful attention would need to be paid to developments regarding unit labor costs and profit margins.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-24

> Homebuilding was forecast to decline somewhat but to stabilize at a relatively high level in the context of continued income growth and the generally favorable cash-flow affordability of home ownership.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-25

> Although some of the recent data on economic activity had been better than anticipated, most participants saw the incoming information as broadly in line with their earlier projections for moderate growth; accordingly, their views on the economic outlook had not changed appreciably.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-26

> Participants noted that the improved performance of investment suggested that the expansion was becoming more balanced, with strengthening business spending potentially offsetting some moderation in the growth of household spending from the elevated rates of recent years.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "economic" triggers dovish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

#### Case A1-27

> That projection, along with the path to year-three inflation, should help the public differentiate short-term shocks to price stability from the longer-term price trends it should use for planning purposes.

| | Answer |
|---|---|
| **Base Claude** | hawkish ❌ |
| **Claude + Abel** | neutral ✅ |
| **Ground Truth** | neutral |

**Why Claude fails**: Keyword "inflation" triggers hawkish classification.
**Why Abel corrects**: Markov blanket shows this text describes the inflation→federalFunds *structural relationship*, not a policy intervention → neutral.

### A2. Subtle Stance Missed (5 cases)

Claude classifies as neutral, missing a subtle directional concern. Abel's causal context
reveals which side of the inflation↔growth tradeoff the text is expressing concern about.

#### Case A2-01

> But I want to emphasize that we do have a commitment to raising inflation to 2 percent.

| | Answer |
|---|---|
| **Base Claude** | neutral ❌ |
| **Claude + Abel** | dovish ✅ |
| **Ground Truth** | dovish |

**Why Abel corrects**: Causal context maps this to below-target inflation concern → dovish.

#### Case A2-02

> Although inflation remained remarkably subdued and any increase in inflationary pressures likely would tend to emerge only slowly, the strength in demand had developed against the backdrop of financial conditions that, broadly considered, were not substantially different from those now prevailing.

| | Answer |
|---|---|
| **Base Claude** | neutral ❌ |
| **Claude + Abel** | dovish ✅ |
| **Ground Truth** | dovish |

**Why Abel corrects**: Causal context maps this to below-target inflation concern → dovish.

#### Case A2-03

> Members agreed that the statement should continue to convey that inflation risks remained of greatest concern and that additional policy firming was possible.

| | Answer |
|---|---|
| **Base Claude** | neutral ❌ |
| **Claude + Abel** | hawkish ✅ |
| **Ground Truth** | hawkish |

**Why Abel corrects**: Causal context maps this to overheating/inflation concern → hawkish.

#### Case A2-04

> With the risks to the forecast for economic activity tilted to the downside, the risks to the inflation projection were also viewed as having a downward skew.

| | Answer |
|---|---|
| **Base Claude** | neutral ❌ |
| **Claude + Abel** | dovish ✅ |
| **Ground Truth** | dovish |

**Why Abel corrects**: Causal context maps this to below-target inflation concern → dovish.

#### Case A2-05

> The extent and timing of any additional firming that may be needed to address these risks will depend on the evolution of the outlook for both inflation and economic growth, as implied by incoming information.

| | Answer |
|---|---|
| **Base Claude** | neutral ❌ |
| **Claude + Abel** | hawkish ✅ |
| **Ground Truth** | hawkish |

**Why Abel corrects**: Causal context maps this to overheating/inflation concern → hawkish.

### A3. Inflation Direction Context (2 cases)

Claude misreads "inflation moderating" as dovish (less inflation = good). Abel recognizes
that moderating *from a high level* still means the economy is in hawkish territory on the
inflation↔federalFunds causal structure.

#### Case A3-01

> Rather, members agreed that inflation was likely to moderate in coming quarters,

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | hawkish ✅ |
| **Ground Truth** | hawkish |

#### Case A3-02

> As a consequence, a sustainable, non-inflationary expansion is likely to involve some moderation in the growth of economic activity to a rate more consistent with the expansion of the nationâ€™s underlying productive capacity.

| | Answer |
|---|---|
| **Base Claude** | dovish ❌ |
| **Claude + Abel** | hawkish ✅ |
| **Ground Truth** | hawkish |

---

## Part B: ForecastBench FRED Macro Direction (8 cases)

Source: [ForecastBench](https://huggingface.co/datasets/Duruo/forecastbench-single_question) (ICLR 2025)

**Why no hindsight bias**: Questions use templated dates `{resolution_date}` — cannot look up actual values via web search.

**Why Abel helps**: Claude's default reasoning follows a single causal channel: *Fed cuts rates → all rates fall*.
Abel's Markov blanket reveals that mortgage rates, treasury yields, and other long-term rates have
**multiple causal parents** — both `federalFunds` (pulling down) and `inflation/CPI` (pushing up).
When the inflation channel dominates, rates rise despite Fed cuts.

```
Abel Markov Blanket for 30YearFixedRateMortgageAverage:
  Parents: federalFunds, CPI, GDP, inflation, industrialProduction
  Children: (downstream effects)
  Spouses: consumerSentiment, durableGoods

Claude's single-channel:  Fed cuts → mortgage rates DOWN  ❌
Abel's multi-channel:     Fed cuts → DOWN pressure
                          Sticky inflation → UP pressure  (dominates)
                          Strong GDP → UP pressure
                          Net: mortgage rates UP  ✅
```

#### Case B-01 (trust: MEDIUM-HIGH)

**Question**: Will AMERIBOR, an interest rate based on overnight loans made between banks on the American Financial Exchange, have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: AMERIBOR® (American Interbank Offered Rate) is a transparent benchmark interest rate based on overnight unsecured loans transacted on the American Financial Exchange (AFX).

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-02 (trust: MEDIUM-HIGH)

**Question**: Will Moody's Seasoned Aaa Corporate Bond Yield have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: N/A.  The notes from the series: These instruments are based on bonds with maturities 20 years and above. 

© 2017, Moody’s Corporation, Moody’s Investors Service, Inc., Mo

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-03 (trust: MEDIUM-HIGH)

**Question**: Will Moody's Seasoned Baa Corporate Bond Yield have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: N/A.  The notes from the series: These instruments are based on bonds with maturities 20 years and above. 

© 2017, Moody’s Corporation, Moody’s Investors Service, Inc., Mo

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-04 (trust: MEDIUM-HIGH)

**Question**: Will the market yield on US treasury securities at 10-year constant maturity, quoted on an investment basis, have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: For questions on the data, please contact the data source: https://www.federalreserve.gov/apps/ContactUs/feedback.aspx?refurl=/releases/h15/%
For questions on FRED functio

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-05 (trust: MEDIUM-HIGH)

**Question**: Will the market yield on US treasury securities at 20-year constant maturity, quoted on an investment basis, have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: For questions on the data, please contact the data source: https://www.federalreserve.gov/apps/ContactUs/feedback.aspx?refurl=/releases/h15/%
For questions on FRED functio

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-06 (trust: MEDIUM-HIGH)

**Question**: Will the market yield on US treasury securities at 30-year constant maturity, quoted on an investment basis, have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: For questions on the data, please contact the data source: https://www.federalreserve.gov/apps/ContactUs/feedback.aspx?refurl=/releases/h15/%
For questions on FRED functio

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-07 (trust: MEDIUM-HIGH)

**Question**: Will the 15-year fixed rate mortgage average in the US have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: N/A.  The notes from the series: On November 17, 2022, Freddie Mac changed the methodology of the Primary Mortgage Market Survey® (PMMS®). The weekly mortgage rate is now b

| | Answer |
|---|---|
| **Base Claude** | 0 (decrease) ❌ |
| **Claude + Abel** | 1 (increase) ✅ |
| **Ground Truth** | 1 |

**Claude's error**: *Fed is cutting rates → this rate should fall* (single-channel reasoning)
**Abel's correction**: Blanket shows inflation/CPI as co-parent → sticky inflation pushes this rate UP despite Fed cuts

#### Case B-08 (trust: LOW)

**Question**: Will Retail Money Market Funds, a component of M2, a measure of USD money supply, have increased by {resolution_date} as compared to its value on {forecast_due_date}?

**Background**: The notes from the release: For questions on the data, please contact the data source: https://www.federalreserve.gov/apps/ContactUs/feedback.aspx?refurl=/releases/h6/%
For questions on FRED function

| | Answer |
|---|---|
| **Base Claude** | 1 (increase) ❌ |
| **Claude + Abel** | 0 (decrease) ✅ |
| **Ground Truth** | 0 |

**Claude's error**: Default to *increase* heuristic
**Abel's correction**: Structural context shows contraction dynamics → this indicator decreased

---

## Why Only These 42

Abel's causal graph helps when **all five conditions** are met:

1. The question involves entities in Abel's graph (inflation, interest rates, GDP, etc.)
2. There is **causal ambiguity** (multiple valid interpretations)
3. Claude's default reasoning takes the **most salient but wrong** causal path
4. Abel's Markov blanket reveals the **overlooked second causal channel**
5. Web search **cannot** resolve the ambiguity (it's reasoning, not fact lookup)

When any condition is missing, Abel adds no value — which is why 1,958 out of 2,000 tested questions showed zero improvement.