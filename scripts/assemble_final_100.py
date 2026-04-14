#!/usr/bin/env python3
"""
Assemble final 100-question benchmark from 144 real questions with Abel signal.
Selection strategy: maximize source diversity and category coverage.
"""
import json, os, random

random.seed(42)
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")

with open(os.path.join(RESULTS, "v3_with_signal.json")) as f:
    pool = json.load(f)

print(f"Pool: {len(pool)} questions with Abel signal")

# Group by source:category
groups = {}
for q in pool:
    key = f"{q['source']}:{q['category']}"
    groups.setdefault(key, []).append(q)

for k, v in sorted(groups.items()):
    print(f"  {k}: {len(v)}")

# Selection quota:
# - DeLLMa stock_decision: 50 (from 94, diverse stock combos)
# - ForecastBench macro_prediction: 35 (all 35)
# - ForecastBench stock_direction: 4 (all 4)
# - FutureX all: 11 (all 11)
# Total: 100

selected = []

# All ForecastBench
for q in groups.get("ForecastBench:macro_prediction", []):
    selected.append(q)
for q in groups.get("ForecastBench:stock_direction", []):
    selected.append(q)

# All FutureX
for cat in ["FutureX:stock_prediction", "FutureX:macro_prediction",
            "FutureX:commodity_prediction", "FutureX:index_prediction",
            "FutureX:crypto_prediction", "FutureX:fx_prediction"]:
    for q in groups.get(cat, []):
        selected.append(q)

remaining = 100 - len(selected)
print(f"\nAfter ForecastBench + FutureX: {len(selected)}, need {remaining} more from DeLLMa")

# DeLLMa: select diverse stock combos
dellma_pool = groups.get("DeLLMa:stock_decision", [])
# Prefer: different stock counts, diverse ground truths
by_gt = {}
for q in dellma_pool:
    gt = q["ground_truth"]
    by_gt.setdefault(gt, []).append(q)

# Take proportional from each ground truth winner
dellma_selected = []
for gt, qs in sorted(by_gt.items()):
    # Proportional: take N proportional to pool size
    n = max(1, int(remaining * len(qs) / len(dellma_pool)))
    dellma_selected.extend(random.sample(qs, min(n, len(qs))))

# Trim or pad to exactly remaining
if len(dellma_selected) > remaining:
    dellma_selected = random.sample(dellma_selected, remaining)
elif len(dellma_selected) < remaining:
    used_ids = {q["id"] for q in dellma_selected}
    extras = [q for q in dellma_pool if q["id"] not in used_ids]
    dellma_selected.extend(random.sample(extras, remaining - len(dellma_selected)))

selected.extend(dellma_selected[:remaining])

print(f"Final selection: {len(selected)} questions")

# Build benchmark JSON
benchmark_questions = []
for i, q in enumerate(selected, 1):
    entry = {
        "id": f"ACAB-{i:03d}",
        "original_id": q.get("id", ""),
        "source_benchmark": q["source"],
        "category": q["category"],
        "abel_has_signal": q["abel_has_signal"],
        "abel_signals": q["abel_signals"],
    }
    if q["source"] == "DeLLMa":
        entry["question"] = q["question"]
        entry["stocks"] = q["stocks"]
        entry["abel_covered_stocks"] = q["abel_stocks"]
        entry["ground_truth"] = q["ground_truth"]
        entry["ground_truth_return_pct"] = q.get("gt_return")
        entry["scoring"] = "exact_match"
        entry["abel_ops"] = [f"observe({s}.price)" for s in q["abel_stocks"][:2]] + \
                            [f"neighbors({s}.price, parents)" for s in q["abel_stocks"][:2]]
    elif q["source"] == "ForecastBench":
        entry["question"] = q["question"]
        entry["ground_truth"] = q["ground_truth"]
        if q["category"] == "stock_direction":
            entry["ticker"] = q.get("ticker")
            entry["abel_node"] = q.get("abel_node")
            entry["scoring"] = "exact_match"
            entry["abel_ops"] = [f"observe({q['abel_node']})", f"neighbors({q['abel_node']}, parents)"]
        else:
            entry["abel_node"] = q.get("abel_node")
            entry["scoring"] = "exact_match"
            entry["abel_ops"] = [f"graph.markov_blanket({q['abel_node']})"]
    elif q["source"] == "FutureX":
        entry["question"] = q.get("question", "")
        entry["title"] = q.get("title", "")
        entry["abel_node"] = q.get("abel_node")
        entry["ground_truth"] = q["ground_truth"]
        entry["difficulty_level"] = q.get("level")
        entry["scoring"] = "numeric_proximity" if isinstance(q["ground_truth"], (list,)) and q["ground_truth"] and isinstance(q["ground_truth"][0], (int, float)) else "exact_match"
        ops = []
        node = q.get("abel_node", "")
        if node.endswith(".price"):
            ops = [f"observe({node})", f"neighbors({node}, parents)"]
        elif node in {"CPI", "inflationRate", "treasuryRateYear10", "GDP",
                       "unemploymentRate", "federalFunds", "consumerSentiment"}:
            ops = [f"graph.markov_blanket({node})"]
        entry["abel_ops"] = ops

    benchmark_questions.append(entry)

# Category summary
cats = {}
for q in benchmark_questions:
    key = f"{q['source_benchmark']}:{q['category']}"
    cats[key] = cats.get(key, 0) + 1

benchmark = {
    "benchmark_name": "Abel Causal Advantage Benchmark (ACAB)",
    "version": "2.0.0",
    "created": "2026-04-13",
    "total_questions": len(benchmark_questions),
    "description": "100-question benchmark of REAL questions from existing benchmarks (DeLLMa, ForecastBench, FutureX-Past) where Claude Code + causal-abel skill provides Abel graph signal unavailable to base Claude Code. Every question is taken directly from its source benchmark with original text and ground truth preserved.",
    "source_benchmarks": {
        "DeLLMa": {
            "paper": "arxiv.org/abs/2402.02392 (ICLR 2025)",
            "repo": "github.com/DeLLMa/DeLLMa",
            "license": "MIT",
            "questions_in_pool": 94,
            "questions_selected": sum(1 for q in benchmark_questions if q["source_benchmark"] == "DeLLMa"),
        },
        "ForecastBench": {
            "paper": "arxiv.org/abs/2409.19839 (ICLR 2025)",
            "website": "forecastbench.org",
            "huggingface": "Duruo/forecastbench-single_question",
            "license": "Apache 2.0",
            "questions_in_pool": 39,
            "questions_selected": sum(1 for q in benchmark_questions if q["source_benchmark"] == "ForecastBench"),
        },
        "FutureX-Past": {
            "paper": "arxiv.org/abs/2508.11987",
            "huggingface": "futurex-ai/Futurex-Past",
            "license": "Apache 2.0",
            "questions_in_pool": 11,
            "questions_selected": sum(1 for q in benchmark_questions if q["source_benchmark"] == "FutureX"),
        },
    },
    "also_tested_but_excluded": {
        "EconCausal": "0/15 Abel coverage — micro-academic causal relationships not in Abel's market graph",
        "CLadder": "Abstract formal causal logic — not Abel's empirical domain",
    },
    "category_breakdown": cats,
    "methodology": {
        "step1": "Downloaded 3 open-source benchmark datasets (total ~10K questions)",
        "step2": "Filtered for questions involving Abel-covered entities (equities, macro indicators)",
        "step3": "Batch-tested Abel API on all 154 filtered questions (with 1s rate limiting)",
        "step4": "Selected 144 questions with confirmed Abel signal",
        "step5": "Sampled 100 questions maximizing source diversity",
    },
    "abel_coverage_used": {
        "equities_with_structure": sorted(["AAPL","MSFT","GOOG","AMZN","META","INTC","QCOM","AVGO",
            "TSM","ASML","TXN","JPM","BAC","GS","MS","WFC","TSLA"]),
        "macro_nodes_with_blanket": sorted(["treasuryRateYear10","federalFunds","CPI","inflationRate",
            "GDP","realGDP","unemploymentRate","30YearFixedRateMortgageAverage",
            "15YearFixedRateMortgageAverage","consumerSentiment","durableGoods",
            "initialClaims","industrialProductionTotalIndex"]),
    },
    "evaluation_protocol": {
        "control": "Claude Code answers using only base reasoning and web search. No Abel API calls.",
        "treatment": "Claude Code answers using full causal-abel skill workflow (observe, neighbors, markov_blanket, consensus, etc.)",
        "scoring_exact_match": "1 if correct, 0 if wrong",
        "scoring_numeric": "1 - min(1, |prediction - actual| / actual) for numeric questions",
    },
    "questions": benchmark_questions,
}

out_path = os.path.join(os.path.dirname(__file__), "..", "abel_advantage_benchmark_v2.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(benchmark, f, indent=2, ensure_ascii=False)

print(f"\n=== FINAL BENCHMARK ===")
print(f"File: {out_path}")
print(f"Total: {len(benchmark_questions)} questions")
print(f"\nBy source:category:")
for k, v in sorted(cats.items()):
    print(f"  {k}: {v}")
