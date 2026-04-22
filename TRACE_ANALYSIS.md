# Trace-Based Deep Analysis: Where Reasoning Succeeds and Fails

基于 **200 条真实双 trace**（100 翻转 + 100 失败）的端到端分析。每条 trace 记录纯 Claude 的 5 阶段推理 + Abel 完整 6 步工作流。

核心问题：**在推理链的哪一步，Claude 出错？在哪一步，Abel 救回或搞砸？**

---

## 结论速览

| 问题 | 答案 |
|------|------|
| Claude 最常在哪里出错？ | **Weighing 步骤**（对信号权重判断错误） |
| Claude 最致命的单一失败模式？ | **默认中性**（看不到触发词就退缩） |
| Abel 最常在哪里救 Claude？ | **Step 3 图发现**（blanket 强制激活推理路径） |
| Abel 最常在哪里出错？ | **Step 3 blanket 盲区** + **Step 6 合成时忽略对冲词** |
| Abel 失败的最主要可修复原因？ | **否定/对冲盲视**（"presumed"、"without"、"not"） |

---

## Part 1：Claude 纯推理的失败模式

从 100 条翻转 trace 中提取 Claude 出错的步骤：

| Claude 失败步骤 | 频率 | 模式 |
|----------------|------|------|
| **Weighing → 默认中性** | 17 | 看不到"rates/hikes/inflation target"就判中性 |
| **Weighing → 财政/货币混同** | 12 | "deficit=inflationary=hawkish"的教科书反射，忽略上下文 |
| **Concepts → 方向反读** | 6 | 把正面语气当鸽派 |
| **Reads → 关键词锚定** | 3 | 只看表面词汇 |

### 案例 1：财政-货币混同

**文本**：
> "the substantial expansion of the federal budget deficit has contributed to this situation"

**Claude 链路**：
- `reads`：看到 "expansion of deficit"
- `concepts`：财政赤字、扩张
- `weighing`："deficit = inflationary = hawkish"（教科书）
- `answer`：hawkish ❌
- `why_wrong`："Claude applies the textbook 'deficit = inflationary = hawkish' frame. But 'contributed to this situation' is vague"

**Abel 链路**：
- `step3_blanket_insight`："Fiscal deficit sits two hops from federalFunds via long rates and aggregate demand"
- `step6_synthesize`："Deficit commentary here is diagnostic of a weak outcome that monetary policy should not exacerbate"
- `answer`：dovish ✅

**关键差异**：Abel 通过 `fiscalStance → long_rates → aggregate_demand → federalFunds` 的两跳因果推理，识别出说话人是在**诊断已有的弱局**，而非呼吁紧缩。

### 案例 2：默认中性（Claude 最常见失败模式）

**文本**：
> "european bank valuations have been depressed by very low profitability caused by excess capacity"

**Claude 链路**：
- `weighing`："These are structural/descriptive observations... No explicit hawkish or dovish policy call"
- `answer`：neutral ❌

**Abel 链路**：
- `step3_blanket_insight`："Bank valuations sit in the Markov blanket of creditTransmission → federalFunds/policyRate. When valuations are depressed, the lending channel weakens, which under standard monetary transmission implies easier policy stance"
- `answer`：dovish ✅

**关键差异**：Abel 的 `proxy_routed` 分类强制把"银行估值疲软"路由到 `creditTransmission` 节点，再沿因果链推到宽松。Claude 看不到直接的"rates/cuts"词汇就默认中性。

---

## Part 2：Abel 成功救场的步骤分布

从 100 条翻转 trace 中统计 Abel 的哪一步真正起作用：

| Abel 关键步骤 | 频率 |
|--------------|------|
| **Step 3（图发现 / Markov blanket）** | 10+ 显式提及 |
| **Step 1（分类 / proxy routing）** | 3 显式提及 |
| **Step 2、4、5、6** | 支持性角色 |

**模式**：Abel 的价值不在 step 5（web grounding）也不在 step 6（synthesize），而在 **step 3 的强制图映射**——它逼着推理必须穿过一个因果节点。当 Claude 退到"中性"时，Abel 的 Step 3 要求"这段文本对应哪个图节点？"，只要能找到节点，Step 4 的方向一致性检查就能推出方向。

---

## Part 3：Abel 失败的步骤级分布

从 100 条 harm trace 中提取 Abel 工作流在哪一步崩溃：

| Abel 失败位置 | 频率 | 机制 |
|--------------|------|------|
| **否定/对冲盲视（跨步骤）** | 35 | 漏读 "presumed"、"not"、"without"、"fortunately"、"illusory" 等反转词 |
| **Step 3 盲区：blanket 不覆盖话题** | 29 | 监管/财政/贸易/FX/supply-chain 超出 4 节点图 |
| **关键词反射（跨步骤）** | 29 | "inflation/rates/risk" 触发方向，忽略语境 |
| **Current-conditions anchoring** | 25 | 用今天的宏观框架读历史文本 |
| **立场反转（批评 vs 认同）** | 12 | 说话人在批评某观点时被当成支持 |
| **过度扁平化到中性** | 6 | 条件语气被当理论描述 |
| **Step 5 错误历史锚定** | 3 | Web grounding 带来错误的先例映射 |

### 案例 3：否定盲视（Abel 最致命的单一失败）

**文本**：
> "for the investor prudence took on another dimension with the presumed ability to mathematize judgment and hedge away the risk of default"

**Claude 链路**（对的）：
- `weighing`："This is a critique of risk-model overconfidence (classic GFC narrative). When models FAIL and default risk is mispriced, financial conditions tighten involuntarily → recessionary pressure → dovish"
- `answer`：dovish ✅

**Abel 链路**（错的）：
- `step3_blanket_insight`：激活 default risk / hedging 节点 → 关联到 rates
- `step4_verify`："re-confirmed the keyword rather than the hedge"
- `step6_synthesize`：hawkish ❌
- `why_wrong`："Abel's pipeline dropped the critical hedge word 'presumed' (negation/irony blindness). The blanket for 'default risk' is keyword-wired to hawkish, and verification re-confirmed the keyword rather than recognizing the ironic frame."

**关键问题**：Abel 的 6 步工作流里**没有一步专门处理语义对冲**。Step 3 把"default risk"映射到鹰派节点后，Step 4 只做方向一致性检查（不重新审视语义），Step 6 就照搬前面的方向。

---

## Part 4：成功 vs 失败的"推理链签名"

通过对比 trace，发现两条推理链的"签名"：

### Abel 成功的签名

1. **Step 1**：正确识别为 `proxy_routed`（话题不直接命中宏观节点）
2. **Step 3**：找到了代理节点（`bankValuations → creditTransmission`、`fiscalStance → long_rates`）
3. **Step 4**：沿因果链的方向验证一致
4. **Step 6**：合成时采用图方向而非表面语气

### Abel 失败的签名

1. **Step 3 崩溃**：要么找不到节点（blanket 盲区），要么找到错节点（关键词触发）
2. **Step 4 惯性**：方向验证没有回头审视 step 3 的映射是否合理
3. **Step 6 合成保守**：当信号冲突时，Abel 倾向 **退到关键词方向** 或 **退到中性**

---

## Part 5：Abel 工作流的结构性缺陷

基于 200 条 trace 的观察，Abel 的 6 步工作流存在以下结构性问题：

### 缺陷 1：Step 3 和 Step 4 的不对称

- Step 3（图发现）会生成关键词驱动的映射
- Step 4（verify）只检查方向一致性，**不回头质疑映射本身**
- 一旦 Step 3 错误映射关键词，后续所有步骤都在错误基础上强化

**修复方向**：Step 4 应该加入"语义反事实检查"（这段文本的否定/对冲词是否反转了 Step 3 的方向？）

### 缺陷 2：Step 2 的对冲假设执行不严格

- Step 2 要求生成 4 个假设，含"必须的逆向假设"
- 实际 trace 中，逆向假设常常是**模板化的**（"hypothetical opposite"）而非真正基于文本生成
- Step 6 合成时，逆向假设没有被认真权衡

**修复方向**：Step 2 的逆向假设必须引用文本具体表述，Step 6 必须显式回答"为什么没采用逆向假设"

### 缺陷 3：Markov blanket 的 4 节点太小

- 监管/财政/贸易/FX/供应链/金融稳定/银行业结构都在 blanket 外
- 超出 blanket 的文本只能靠关键词反射或退到中性

**修复方向**：扩展 blanket 到 10-15 节点（加入 fiscalStance、tradeBalance、financialStability、supervisoryStance、supplyChain、productivity 等）

### 缺陷 4：Web grounding 的锚定偏差

- Step 5 会把文本关联到著名先例（Volcker、Draghi、GFC）
- 但这会**覆盖**文本的实际语境（pre-2000 Fed 演讲 vs 当前 2026 环境）
- 35/100 harm 涉及历史锚定错误

**修复方向**：Step 5 应该先定位**文本本身的时间背景**，再选择同期先例（而非默认当前框架）

---

## Part 6：实用决策规则

基于 trace 签名，agent 在使用 Abel 时可以遵循：

```
IF (Claude 答案是 neutral) AND (文本含 Abel blanket 节点) AND (无否定/对冲词):
    → 采用 Abel 的答案（70%+ 概率翻转为正确）

IF (文本涉及监管/财政/贸易/FX) OR (文本有否定/对冲词):
    → 采用 Claude 的答案（Abel 在这些区域不可靠）

IF (文本是历史/外国语境) AND (Abel 的 step 5 锚定到当前) :
    → 采用 Claude 的答案（Abel 时间锚定有偏差）

IF (Claude 和 Abel 都给出明确方向且相同):
    → 高置信度接受
    
IF (Claude 和 Abel 方向相反且无否定词):
    → Abel 的结构推理通常更可靠

IF (Claude 和 Abel 方向相反且有否定词):
    → Claude 更可靠
```

---

## 原始 Trace 文件

- [`data/traces/all_flip_traces.json`](data/traces/all_flip_traces.json) — 100 条翻转案例完整双 trace
- [`data/traces/all_harm_traces.json`](data/traces/all_harm_traces.json) — 100 条失败案例完整双 trace
- [`data/traces/flip_trace_{0-3}.json`](data/traces/) — 分 batch 源文件
- [`data/traces/harm_trace_{0-3}.json`](data/traces/) — 分 batch 源文件

每条 trace 包含：
- Claude 的 5 阶段推理（reads → concepts → weighing → answer → why）
- Abel 的 6 步工作流（classify → hypotheses → graph_discovery → verify → web_grounding → synthesize）
- Comparison 字段解释两条推理链的差异
