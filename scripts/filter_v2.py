#!/usr/bin/env python3
"""
V2: Precise filtering and testing. Fix false-positive ticker matching.
"""
import json, subprocess, os, re, time

SKILL_DIR = "/home/zeyu/.claude/skills/causal-abel"
BASE_URL = "https://cap.abel.ai/api"
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")

ABEL_EQUITY_NODES = {
    "AAPL","MSFT","GOOG","AMZN","META","INTC","QCOM","AVGO",
    "TSM","ASML","TXN","JPM","BAC","GS","MS","WFC","TSLA",
}
ABEL_MACRO_BLANKET = {
    "treasuryRateYear10","federalFunds","CPI","inflationRate",
    "GDP","realGDP","unemploymentRate","30YearFixedRateMortgageAverage",
    "15YearFixedRateMortgageAverage","consumerSentiment","durableGoods",
    "initialClaims","industrialProductionTotalIndex",
}

def probe(args, timeout=25):
    cmd = ["python3", f"{SKILL_DIR}/scripts/cap_probe.py", "--base-url", BASE_URL] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout or r.stderr)
    except:
        return {"ok": False}


# ============================================================
# 1. DeLLMa: precise stock matching
# ============================================================
def process_dellma():
    with open(os.path.join(DATA, "dellma_stock_questions.json")) as f:
        qs = json.load(f)
    covered = []
    for q in qs:
        # GOOGL -> GOOG mapping
        abel_stocks = []
        for s in q["stocks"]:
            mapped = "GOOG" if s == "GOOGL" else s
            if mapped in ABEL_EQUITY_NODES:
                abel_stocks.append(mapped)
        if abel_stocks:
            covered.append({
                "id": q["id"], "source": "DeLLMa", "category": "stock_decision",
                "question": q["prompt"][:300], "full_prompt": q["prompt"],
                "stocks": q["stocks"], "abel_stocks": abel_stocks,
                "ground_truth": q["ground_truth"],
                "gt_return": q.get("ground_truth_return_pct"),
            })
    return covered


# ============================================================
# 2. ForecastBench: extract exact ticker from question text
# ============================================================
def process_forecastbench():
    with open(os.path.join(DATA, "forecastbench_financial.json")) as f:
        qs = json.load(f)

    covered = []
    for q in qs:
        src = q.get("data_source", "")
        question = q.get("question", "")
        bg = q.get("background", "")

        if src == "yfinance":
            # Extract ticker: "Will XXXX's market close price..."
            m = re.match(r"Will (\w+)'s", question)
            if m:
                ticker = m.group(1)
                if ticker in ABEL_EQUITY_NODES:
                    covered.append({
                        "id": q["id"], "source": "ForecastBench",
                        "category": "stock_direction",
                        "question": question, "ticker": ticker,
                        "abel_node": f"{ticker}.price",
                        "ground_truth": q["answer"],
                    })

        elif src == "fred":
            text = (question + " " + bg).lower()
            node = None
            # Precise keyword matching
            if "10-year treasury" in text or "10 year treasury" in text:
                node = "treasuryRateYear10"
            elif "federal fund" in text:
                node = "federalFunds"
            elif "consumer price index" in text or "cpi" in text.split():
                node = "CPI"
            elif "unemployment" in text:
                node = "unemploymentRate"
            elif "initial claim" in text or "jobless claim" in text:
                node = "initialClaims"
            elif "gdp" in text.split() or "gross domestic" in text:
                node = "GDP"
            elif "mortgage" in text:
                node = "30YearFixedRateMortgageAverage"
            elif "consumer sentiment" in text:
                node = "consumerSentiment"
            elif "durable good" in text:
                node = "durableGoods"
            elif "industrial production" in text:
                node = "industrialProductionTotalIndex"
            elif "inflation" in text:
                node = "inflationRate"

            if node:
                covered.append({
                    "id": q["id"], "source": "ForecastBench",
                    "category": "macro_prediction",
                    "question": question, "abel_node": node,
                    "ground_truth": q["answer"],
                })

    return covered


# ============================================================
# 3. FutureX: precise financial question extraction
# ============================================================
def process_futurex():
    with open(os.path.join(DATA, "futurex_past.json")) as f:
        qs = json.load(f)

    covered = []
    for q in qs:
        title = q["title"]
        prompt = q["prompt"]
        text = title + " " + prompt

        abel_node = None
        category = None

        # Exact ticker mentions with word boundary
        for ticker in ABEL_EQUITY_NODES:
            # Match "AAPL" as whole word or in parentheses like "(AAPL)"
            if re.search(rf'\b{ticker}\b', text):
                abel_node = f"{ticker}.price"
                category = "stock_prediction"
                break

        # Specific financial instruments
        if not abel_node:
            if "NVIDIA" in text or "Nvidia" in text:
                abel_node = "NVDA.price"  # NVDA exists but no structure
                category = "stock_prediction"
            elif "Apple stock" in text or "(AAPL)" in text:
                abel_node = "AAPL.price"
                category = "stock_prediction"
            elif "Li Auto" in text:
                abel_node = "LI.price"
                category = "stock_prediction"
            elif "NASDAQ" in text and ("index" in text.lower() or "composite" in text.lower()):
                abel_node = "NDAQ.price"
                category = "index_prediction"
            elif "S&P 500" in text or "S&P500" in text:
                category = "index_prediction"
                abel_node = "macro_sp500"  # no direct node, but macro context
            elif "Bitcoin" in text or "BTC" in text:
                abel_node = "BTCUSD.price"
                category = "crypto_prediction"
            elif re.search(r'\b(inflation|CPI)\b', text, re.I):
                abel_node = "CPI"
                category = "macro_prediction"
            elif re.search(r'\bPCE\b', text):
                abel_node = "inflationRate"
                category = "macro_prediction"
            elif "Crude Oil" in text or "crude oil" in text:
                abel_node = "CL.price"
                category = "commodity_prediction"
            elif re.search(r'\bGold\b.*\b(GC)\b', text):
                abel_node = "GC.price"
                category = "commodity_prediction"
            elif "exchange rate" in text.lower() or "USD" in text:
                category = "fx_prediction"
                abel_node = "USDCNY.price"

        if abel_node and category:
            covered.append({
                "id": f"fx_{q['id']}",
                "source": "FutureX",
                "category": category,
                "question": prompt[:400],
                "title": title,
                "abel_node": abel_node,
                "ground_truth": q["ground_truth"],
                "level": q["level"],
            })

    return covered


# ============================================================
# 4. Test Abel signal
# ============================================================
def test_signal(q):
    signals = []

    if q["source"] == "DeLLMa":
        for s in q["abel_stocks"][:3]:
            node = f"{s}.price"
            r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                        "--params-json", json.dumps({"target_node": node})])
            if r.get("ok"):
                signals.append({"op": f"observe({node})", "val": r["result"].get("prediction")})
            r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "5"])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"parents({node})", "n": len(r["result"]["neighbors"])})

    elif q["source"] in ("ForecastBench", "FutureX"):
        node = q.get("abel_node", "")
        if node.endswith(".price"):
            r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                        "--params-json", json.dumps({"target_node": node})])
            if r.get("ok"):
                signals.append({"op": f"observe({node})", "val": r["result"].get("prediction")})
            r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "5"])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"parents({node})", "n": len(r["result"]["neighbors"])})
        elif node in ABEL_MACRO_BLANKET:
            r = probe(["verb", "graph.markov_blanket",
                        "--params-json", json.dumps({"node_id": node})])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"blanket({node})", "n": len(r["result"]["neighbors"])})
        # Also try consensus if it's a stock
        if node.endswith(".price"):
            r = probe(["verb", "extensions.abel.discover_consensus",
                        "--params-json", json.dumps({"seed_nodes": [node], "direction": "out", "limit": 5})])
            if r.get("ok") and r.get("result", {}).get("items"):
                signals.append({"op": f"consensus({node})", "n": len(r["result"]["items"])})

    return signals


if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: PRECISE FILTERING")
    print("=" * 60)

    dellma = process_dellma()
    fb = process_forecastbench()
    fx = process_futurex()

    print(f"DeLLMa: {len(dellma)} questions with Abel-covered stocks")
    print(f"ForecastBench: {len(fb)} questions (stock={sum(1 for q in fb if q['category']=='stock_direction')}, macro={sum(1 for q in fb if q['category']=='macro_prediction')})")
    print(f"FutureX: {len(fx)} questions")
    for cat in set(q["category"] for q in fx):
        print(f"  {cat}: {sum(1 for q in fx if q['category'] == cat)}")

    all_q = dellma + fb + fx
    print(f"\nTotal to test: {len(all_q)}")

    print(f"\n{'=' * 60}")
    print("STEP 2: BATCH TEST ABEL API")
    print("=" * 60)

    for i, q in enumerate(all_q):
        signals = test_signal(q)
        q["abel_signals"] = signals
        q["abel_has_signal"] = len(signals) > 0
        if (i+1) % 30 == 0:
            n_sig = sum(1 for x in all_q[:i+1] if x.get("abel_has_signal"))
            print(f"  Tested {i+1}/{len(all_q)}: {n_sig} with signal")

    with_signal = [q for q in all_q if q["abel_has_signal"]]
    print(f"\nTotal with Abel signal: {len(with_signal)}/{len(all_q)}")

    by_src = {}
    for q in with_signal:
        key = f"{q['source']}:{q['category']}"
        by_src[key] = by_src.get(key, 0) + 1
    for k, v in sorted(by_src.items()):
        print(f"  {k}: {v}")

    # Save
    out = os.path.join(RESULTS, "v2_all_tested.json")
    save = [{k: v for k, v in q.items() if k != "full_prompt"} for q in all_q]
    with open(out, "w") as f:
        json.dump(save, f, indent=2, ensure_ascii=False)

    # Also save just the signal questions with full data for benchmark assembly
    sig_out = os.path.join(RESULTS, "v2_with_signal.json")
    sig_save = [{k: v for k, v in q.items() if k != "full_prompt"} for q in with_signal]
    with open(sig_out, "w") as f:
        json.dump(sig_save, f, indent=2, ensure_ascii=False)

    print(f"\nSaved full: {out}")
    print(f"Saved signal only: {sig_out}")
