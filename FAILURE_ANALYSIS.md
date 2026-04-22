# Abel Skill 失败原因分析

基于 679 条真实失败 case 的 LLM 逐条诊断汇总分析。每条失败都让独立 LLM Agent 读原文 + Claude 答案 + Abel 答案 + Ground Truth，写出针对该文本的具体失败原因，然后对 679 条诊断做主题归纳。

**核心结论**：Abel 失败不是偶然错误，而是**架构性局限**——它只有 4 个宏观节点的因果图 (`inflation↔federalFunds↔GDP↔unemployment`)，加上机械的关键词映射，无法处理央行语言中常见的领域外话题、语义对冲、时空语境。

---

## 失败原因分布（基于 LLM 诊断主题频率）

| 失败类型 | 频率 | 占比 |
|---------|------|------|
| 关键词反射（机械触发） | 156 | 23.0% |
| 过度扁平化到中性 | 152 | 22.4% |
| 监管/制度话题 blanket 外 | 142 | 20.9% |
| 否定/对冲盲点 | 137 | 20.2% |
| 历史/外国语境锚定错误 | 119 | 17.5% |
| 生产率/供给侧 blanket 外 | 87 | 12.8% |
| 当前条件锚定 | 80 | 11.8% |
| 财政政策 blanket 外 | 68 | 10.0% |
| 立场反转失败（批评 vs 认同） | 47 | 6.9% |
| 贸易/净出口 blanket 外 | 31 | 4.6% |
| 金融稳定 blanket 外 | 22 | 3.2% |
| 成本推动 vs 需求拉动混淆 | 10 | 1.5% |
| "从高位回落"vs"走弱"混淆 | 7 | 1.0% |
| QE/资产负债表 blanket 外 | 5 | 0.7% |
| 滞涨场景判断错误 | 4 | 0.6% |

（注：一条 case 可能被归入多个主题，所以总和超过 100%）

---

## 第一类：因果图覆盖缺失 (~43% 失败)

Abel 的 Markov blanket 只有 4 个核心宏观节点：`inflation`、`federalFunds`、`GDP`、`unemployment`。央行语言常涉及大量 blanket 外的领域，Abel 没有对应节点，只能退到默认（通常是 neutral 或错误触发相关宏观关键词）。

### 1.1 监管/制度话题（142 条）

Abel 图中没有 Basel、macroprudential、supervision、governance、TBTF 等节点。监管话题要么被误判为鸽派（"credit 相关=宽松"），要么扁平化到中性。

**例子：**
> **"simplicity there is significant justification for both higher levels and higher quality of capital"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：This is pro-tighter bank capital regulation (higher capital requirements), which is financial-conditions-hawkish, but Abel's Markov blanket has no regulatory/macropru node and it classified the sentence as neutral descriptive rather than recognizing the tightening implication for credit.

> **"past deregulation should enable businesses to adapt their organizational structures in response to these new opportunities"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Deregulation enabling adaptive business expansion is supply-side hawkish (higher potential/productivity), but Abel lacks a regulatory/institutional node in its blanket and classified it as neutral descriptive language instead of tracing deregulation -> capacity.

> **"this will require among other 12things reduction of obstacles to the expansion of nuclear facilities by our electric utilities and sufficient relaxation of antipollution regulation"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：Calling for deregulation to expand energy supply is a supply-side hawkish push (more capacity, lower cost pressure), but Abel parsed 'relaxation of regulations' as loosening/accommodative and inverted to dovish, confusing regulatory loosening with monetary easing.

### 1.2 财政政策（68 条）

Abel 把"政府支出"一律视为鸽派 accommodative，把"减税/刺激"误读为鹰派（二阶推理"刺激→通胀→紧缩"）。但央行实际视角是"财政减支 = 需求疲软 = 鸽派关切"。

**例子：**
> **"with spending by the federal government expected to slow activities in these industries may be hampered"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：Expected fiscal slowdown hampering industry activity is a negative demand shock -> dovish, but Abel likely mapped 'government spending slow' to fiscal tightening/anti-inflation and classified it hawkish, missing that the monetary-policy-relevant signal is the demand weakness in downstream industries.

> **"in the interest of enhancing our global competitiveness and ensuring continued improvement in living standards for coming generations congress needs to take steps now to trim spend"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：A call for fiscal discipline ('trim spending') to protect competitiveness aligns with tighter aggregate conditions and restrained demand -> hawkish, but Abel treated it as off-blanket fiscal-policy advocacy (congress-facing) and defaulted to neutral instead of tracing fiscal tightness -> lower inflationary pressure.

> **"because the dollar price of imported goods rises while that of exported commodities remains unchanged the trade deficit initially worsens especially for trade flows covered by cont"**
> 
> - Claude：dovish ✓ · Abel：neutral ✗ · 真值：dovish
> - **LLM 诊断**：A worsening trade deficit is a near-term drag on GDP (dovish), but Abel treated it as a textbook J-curve explanation and classified the passage as neutral mechanism description rather than scoring the implied near-term growth drag.

### 1.3 生产率/供给侧（87 条）

"生产率提升"、"技术革命"、"潜在产出扩大" 本属鹰派（经济变强 → 加息更可能），但 Abel 读成描述性中性。

**例子：**
> **"in the first place our manufacturing sector is not nearly as bad off as some would have us believe and the potential for significant advances in productivity is at hand"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：The statement is a positive reassessment of manufacturing and a forward-looking productivity claim, which is hawkish (stronger output/potential), but Abel's stance-vs-mechanism heuristic flattened a rhetorical rebuttal ('not as bad off') into a 'descriptive/neutral' observation instead of recognizing optimism about supply capacity.

> **"productivity gains in the motor vehicle industry have been strong and steady over the past 20 years"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Strong sustained productivity gains imply higher potential output and supply capacity -> hawkish via the supply-side channel, but Abel treated the sentence as a historical sector fact with no direct blanket attachment and picked neutral instead of tracing productivity -> output.

> **"production rose from 60 per cent of the 195759 average in 1930 to 118 per cent in 1967 thus in 1967 the nations farms produced almost double the 1930 level"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：A doubling of farm output over several decades is a supply-expansion/productivity fact (hawkish via higher potential), but Abel saw a purely historical statistic with no rate/inflation keyword and defaulted to neutral rather than inferring the supply-side implication.

### 1.4 贸易/净出口（31 条）

Abel blanket 没有净出口节点。"日本出口放缓"对美国是鹰派（进口替代、本土需求替代），Abel 只看到"放缓"判鸽派。

**例子：**
> **"japanese export growth has slowed considerably in recent months and some categories have actu ally registered declines"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：Abel saw 'growth has slowed' and 'declines' and pattern-matched to weakening activity -> dovish, but in a Japanese/US-trade context slower Japanese exports means reduced import competition and a hawkish demand-shift toward US producers; Abel's blanket has no trade-balance node to capture this substitution channel.

> **"these circumstances should help our net export position"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Improved net exports raise aggregate demand and GDP -> hawkish, but the sentence lacks explicit inflation/rate/unemployment keywords, so Abel's Markov-blanket pass found no node to attach to and defaulted to neutral rather than tracing exports -> GDP -> policy.

---

## 第二类：语义理解太表层 (~65% 失败)

即使话题在 blanket 内，Abel 也经常读错，因为它的工作方式是"看到关键词 → 激活节点 → 套用预设方向"，无法处理自然语言的细微差别。

### 2.1 关键词反射（156 条，最常见）

Abel 对特定关键词有条件反射：

| 关键词 | Abel 触发方向 | 问题 |
|--------|-------------|------|
| inflation / prices / expectations | 鹰派 | 即使说话人在批评紧缩也被判鹰派 |
| risk / stability / concerns | 鹰派警觉 | 即使是承认下行风险（鸽派） |
| government spending | 鸽派 accommodation | 财政紧缩语境下应为鸽派关切 |
| credit / banking | 鸽派宽松 | 监管加强语境应为鹰派 |

**例子：**
> **"these circumstances should help our net export position"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Improved net exports raise aggregate demand and GDP -> hawkish, but the sentence lacks explicit inflation/rate/unemployment keywords, so Abel's Markov-blanket pass found no node to attach to and defaulted to neutral rather than tracing exports -> GDP -> policy.

> **"in particular inflation has reduced corporate funds available for investment"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：The sentence highlights inflation's damage to investment capacity (weakening capex channel) which is a dovish growth concern, but Abel saw the keyword 'inflation' and reflexively mapped the sentence to a hawkish inflation-warning stance, ignoring the negative capex mechanism.

> **"over the next few months 12month measures of inflation are expected to move above our 2 percent longerrun goal largely reflecting i believe transitory factors such as a run of year"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：The speaker is pre-emptively dismissing an inflation overshoot as 'transitory' base-effects, which is the classic dovish framing for looking through high prints, but Abel's keyword radar caught 'inflation above 2 percent goal' and labelled it hawkish while ignoring the dismissal.

### 2.2 过度扁平化到中性（152 条）

Abel 的"机制描述 vs 政策立场"启发式过度使用——任何带条件语气（"should"、"would"、"if"）或分析框架的文本都被扁平化为中性，即使实际表达了明确方向。

**例子：**
> **"in the first place our manufacturing sector is not nearly as bad off as some would have us believe and the potential for significant advances in productivity is at hand"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：The statement is a positive reassessment of manufacturing and a forward-looking productivity claim, which is hawkish (stronger output/potential), but Abel's stance-vs-mechanism heuristic flattened a rhetorical rebuttal ('not as bad off') into a 'descriptive/neutral' observation instead of recognizing optimism about supply capacity.

> **"that development in turn could make it more difficult during downturns for monetary policy to support household spending business investment and employment and keep inflation from "**
> 
> - Claude：dovish ✓ · Abel：neutral ✗ · 真值：dovish
> - **LLM 诊断**：The concern that policy may struggle to prevent inflation from 'falling too low' is explicitly about disinflation risk at the lower bound -> dovish, but Abel treated the sentence as a meta-discussion of policy mechanics (a 'framework' observation) and flattened it to neutral instead of scoring the below-target-inflation worry.

> **"in particular inflation has reduced corporate funds available for investment"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：The sentence highlights inflation's damage to investment capacity (weakening capex channel) which is a dovish growth concern, but Abel saw the keyword 'inflation' and reflexively mapped the sentence to a hawkish inflation-warning stance, ignoring the negative capex mechanism.

### 2.3 否定/对冲盲点（137 条）

Abel 忽略 "without"、"not"、"illusory"、"weakened"、"errors" 这类反转信号，只看关键词本身。

**例子：**
> **"some of it however represents loans for the purchase of additional land and equipment or livestock which may well represent efforts to improe efficiency of farm operaticnsrather th"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Reinterpreting rising farm loans as productivity-improving capex (not distress) is a hawkish reassessment of real activity, but Abel read 'loans... rather than losses' as a hedge/neutralization and picked neutral instead of the positive reframing.

> **"improved strategic planning and marketing tighter control of operating expenses reduction of unnecessary overhead greater use of computers communications technology and atts increa"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：A list of efficiency gains (cost control, tech adoption) boosts productivity/margins (hawkish via potential output), but Abel parsed it as a descriptive management checklist without a blanket node and classified it neutral.

> **"to be sure with the us now a major oil producer lower oil prices have also had some negative effects on the us economy"**
> 
> - Claude：dovish ✓ · Abel：neutral ✗ · 真值：dovish
> - **LLM 诊断**：Lower oil prices having negative effects on US producers is a dovish real-activity signal (energy-sector drag), but Abel saw the classic 'lower oil prices = demand stimulus' frame and the hedge 'some negative effects' cancelled out to neutral.

### 2.4 立场反转失败（91 条）

说话人批评某观点、引用对立观点、反问、讽刺——Abel 无法识别论辩框架，把被批评的观点当成说话人的立场。

**例子：**
> **"in the first place our manufacturing sector is not nearly as bad off as some would have us believe and the potential for significant advances in productivity is at hand"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：The statement is a positive reassessment of manufacturing and a forward-looking productivity claim, which is hawkish (stronger output/potential), but Abel's stance-vs-mechanism heuristic flattened a rhetorical rebuttal ('not as bad off') into a 'descriptive/neutral' observation instead of recognizing optimism about supply capacity.

> **"using history as a guide we can see that energy and commodity shocks dont fully pass through to other prices"**
> 
> - Claude：dovish ✓ · Abel：neutral ✗ · 真值：dovish
> - **LLM 诊断**：Arguing that commodity shocks don't fully pass through is a dovish argument for not reacting to headline inflation spikes, but Abel read the sentence as a neutral empirical generalization about pass-through rather than as a policy-relevant dismissal of inflation risk.

> **"it would seem in the selfinterest of these countries to ensure that domestic demands are expanded to take up the slack that will be left by diminishing foreign outlets for their go"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Calling on foreign countries to expand domestic demand to offset lost export markets is a pro-growth/demand-supportive argument (hawkish), but Abel saw both 'expand demand' and 'slack/diminishing outlets' cues and cancelled them to neutral instead of resolving the net policy tilt.

---

## 第三类：时空锚定错误 (~30% 失败)

### 3.1 历史/外国语境错误（119 条）

Abel 用当前（2026年）美国通胀粘性的思维去读 1970s Fed 演讲、ECB 文本、BIS 跨国报告——不同政策周期下同样的词意思完全不同。

**例子：**
> **"japanese export growth has slowed considerably in recent months and some categories have actu ally registered declines"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：Abel saw 'growth has slowed' and 'declines' and pattern-matched to weakening activity -> dovish, but in a Japanese/US-trade context slower Japanese exports means reduced import competition and a hawkish demand-shift toward US producers; Abel's blanket has no trade-balance node to capture this substitution channel.

> **"over the next few months 12month measures of inflation are expected to move above our 2 percent longerrun goal largely reflecting i believe transitory factors such as a run of year"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：The speaker is pre-emptively dismissing an inflation overshoot as 'transitory' base-effects, which is the classic dovish framing for looking through high prints, but Abel's keyword radar caught 'inflation above 2 percent goal' and labelled it hawkish while ignoring the dismissal.

> **"productivity gains in the motor vehicle industry have been strong and steady over the past 20 years"**
> 
> - Claude：hawkish ✓ · Abel：neutral ✗ · 真值：hawkish
> - **LLM 诊断**：Strong sustained productivity gains imply higher potential output and supply capacity -> hawkish via the supply-side channel, but Abel treated the sentence as a historical sector fact with no direct blanket attachment and picked neutral instead of tracing productivity -> output.

### 3.2 当前条件锚定（80 条）

Abel 永远假设"今天"的宏观环境，不识别文本所处的不同政策周期。通胀高位时期的"通胀担忧"和通胀低位时期的"通胀担忧"含义完全不同，但 Abel 一视同仁。

**例子：**
> **"3 surge in sale of durable goods machinery and large appliances will moderate though recent data shows continued strength"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：The emphasis is 'recent data shows continued strength' in durable-goods spending (hawkish demand), but Abel anchored on 'will moderate' and read it as a forward dovish cooling signal rather than current hawkish strength with a mild forward qualifier.

> **"this would lead to another round of price increases overexpansion and possibly ultimate deflation"**
> 
> - Claude：dovish ✓ · Abel：hawkish ✗ · 真值：dovish
> - **LLM 诊断**：The punchline is 'possibly ultimate deflation' (dovish tail-risk warning), but Abel anchored on the earlier 'price increases' and 'overexpansion' as hawkish inflation/overheating signals and missed that the sentence's conclusion is a deflation/bust concern.

### 3.3 "从高位回落"vs"走弱"混淆（7 条）

失业率从 7% 回落到 5%（鹰派正常化）和从 3.5% 上升到 5%（鸽派走弱）在 Abel 眼里都是"5%"，无法区分轨迹方向。

**例子：**
> **"these include the recent decline in mortgage rates slower house price appreciation which was running 6 to 7 percent in early 2018 and is now in the 3 to 4 percent range and an incr"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：Cooling house price appreciation from an unsustainably hot 6-7% to a healthier 3-4% is a hawkish-normalization signal of sustainable activity, but Abel read 'decline in mortgage rates' and 'slower house price appreciation' as easing/cooling dovish and missed the 'slowing-from-hot-base' hawkish interpretation.

> **"on net i do expect the unemployment rate to normalize at close to 5 percent within the next five years"**
> 
> - Claude：hawkish ✓ · Abel：dovish ✗ · 真值：hawkish
> - **LLM 诊断**：Expecting unemployment to 'normalize... to 5 percent' from a higher current rate is a hawkish labor-market-tightening forecast, but Abel read 'unemployment 5 percent' as still-elevated slack and labeled it dovish, missing the implied decline to NAIRU.

---

## 一句话总结

> **Abel 的优势和劣势来自同一个特性：它强制把文本映射到一个小的因果图上。**

**当它对时**：Claude 习惯默认中性时，Abel 的强制映射把 neutral 拉出来成正确方向（1,463 个翻转）。

**当它错时**：

1. 话题不在图里 → 默认 neutral 或错误触发宏观节点（43%）
2. 关键词触发但语义相反 → 机械映射忽略否定、反讽、条件（65%）
3. 当前条件锚定 → 用 2026 思维读 1970s 文本（30%）

**改进方向**（按影响排序）：

1. 扩展 Markov blanket 覆盖：加入监管、财政、贸易、金融稳定、QE、生产率节点
2. 增加否定/对冲/立场反转的语义解析层
3. 给 Abel 提供文本时间/地理上下文，避免当前条件锚定
4. 区分"水平"和"方向"（正常化 vs 走弱）

---

**数据来源**：
- 679 条真实失败 case 来自 A/B 测试 15,624 道央行文本分类题
- 每条 case 都由独立 LLM Agent 做逐条诊断（7 个并行 Agent，每个 ~97 条）
- 完整诊断数据：[`data/harm_llm_analysis_full.json`](data/harm_llm_analysis_full.json)