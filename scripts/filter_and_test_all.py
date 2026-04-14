#!/usr/bin/env python3
"""
Filter all 412 real benchmark questions for Abel coverage,
then batch-test Abel API to find questions where Abel adds signal.
"""
import json, subprocess, os, re

SKILL_DIR = "/home/zeyu/.claude/skills/causal-abel"
BASE_URL = "https://cap.abel.ai/api"
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")

# Verified Abel nodes
ABEL_EQUITIES = {
    "AAPL","MSFT","GOOG","GOOGL","AMZN","META","INTC","QCOM","AVGO",
    "TSM","ASML","TXN","JPM","BAC","GS","MS","WFC","C","TSLA",
    "LI","NDAQ",
}
ABEL_MACRO = {
    "treasuryRateYear10","federalFunds","CPI","inflationRate","inflation",
    "GDP","realGDP","unemploymentRate","30YearFixedRateMortgageAverage",
    "15YearFixedRateMortgageAverage","consumerSentiment","durableGoods",
    "initialClaims","industrialProductionTotalIndex",
    "3MonthOr90DayRatesAndYieldsCertificatesOfDeposit",
    "commercialBankInterestRateOnCreditCardPlansAllAccounts",
}
# Keyword -> macro node mapping for FRED questions
FRED_MACRO_MAP = {
    "treasury": "treasuryRateYear10",
    "10-year": "treasuryRateYear10",
    "federal fund": "federalFunds",
    "fed fund": "federalFunds",
    "cpi": "CPI",
    "consumer price": "CPI",
    "inflation": "inflationRate",
    "gdp": "GDP",
    "gross domestic": "GDP",
    "unemployment": "unemploymentRate",
    "initial claim": "initialClaims",
    "jobless claim": "initialClaims",
    "mortgage": "30YearFixedRateMortgageAverage",
    "consumer sentiment": "consumerSentiment",
    "durable good": "durableGoods",
    "industrial production": "industrialProductionTotalIndex",
    "certificate of deposit": "3MonthOr90DayRatesAndYieldsCertificatesOfDeposit",
}

def probe(args, timeout=20):
    cmd = ["python3", f"{SKILL_DIR}/scripts/cap_probe.py", "--base-url", BASE_URL] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout or r.stderr)
    except:
        return {"ok": False}

# ============================================================
# 1. DELLMA: filter questions containing Abel-covered stocks
# ============================================================
def process_dellma():
    with open(os.path.join(DATA, "dellma_stock_questions.json")) as f:
        qs = json.load(f)

    covered = []
    for q in qs:
        # Map GOOGL -> GOOG for Abel
        stocks = q["stocks"]
        abel_stocks = [s for s in stocks if s in ABEL_EQUITIES or s.replace("L","") in ABEL_EQUITIES]
        if len(abel_stocks) >= 1:  # at least 1 stock has Abel coverage
            covered.append({
                "id": q["id"],
                "source": "DeLLMa",
                "category": "stock_decision",
                "stocks": stocks,
                "abel_covered_stocks": abel_stocks,
                "ground_truth": q["ground_truth"],
                "ground_truth_return_pct": q.get("ground_truth_return_pct"),
                "prompt_preview": q["prompt"][:200],
                "full_prompt": q["prompt"],
            })
    print(f"DeLLMa: {len(covered)}/{len(qs)} have Abel-covered stocks")
    return covered

# ============================================================
# 2. FORECASTBENCH: filter yfinance + FRED with Abel coverage
# ============================================================
def process_forecastbench():
    with open(os.path.join(DATA, "forecastbench_financial.json")) as f:
        qs = json.load(f)

    covered = []
    for q in qs:
        src = q.get("data_source", "")
        question = q.get("question", "")
        bg = q.get("background", "")
        text = (question + " " + bg).lower()

        abel_nodes = []

        if src == "yfinance":
            # Extract ticker from question
            # Pattern: "Will X's close price" or ticker mentions
            for ticker in ABEL_EQUITIES:
                if ticker.lower() in text or ticker in question:
                    abel_nodes.append(f"{ticker}.price")

        elif src == "fred":
            # Match FRED concepts to macro nodes
            for keyword, node in FRED_MACRO_MAP.items():
                if keyword in text:
                    abel_nodes.append(node)
                    break

        if abel_nodes:
            covered.append({
                "id": q["id"],
                "source": "ForecastBench",
                "category": "yfinance_direction" if src == "yfinance" else "fred_macro",
                "question": question,
                "background": bg[:300],
                "data_source": src,
                "abel_nodes": abel_nodes,
                "ground_truth": q["answer"],
                "full_question": question,
            })

    yf = sum(1 for c in covered if c["category"] == "yfinance_direction")
    fred = sum(1 for c in covered if c["category"] == "fred_macro")
    print(f"ForecastBench: {len(covered)}/{len(qs)} have Abel coverage (yfinance={yf}, fred={fred})")
    return covered

# ============================================================
# 3. FUTUREX: filter financial questions with Abel coverage
# ============================================================
def process_futurex():
    with open(os.path.join(DATA, "futurex_past.json")) as f:
        qs = json.load(f)

    covered = []
    for q in qs:
        text = (q["prompt"] + q["title"]).lower()
        abel_nodes = []

        # Check equity tickers
        for ticker in ABEL_EQUITIES:
            if ticker.lower() in text:
                abel_nodes.append(f"{ticker}.price")

        # Check macro keywords
        for keyword, node in FRED_MACRO_MAP.items():
            if keyword in text:
                abel_nodes.append(node)
                break

        # Special cases
        if "bitcoin" in text or "btc" in text:
            abel_nodes.append("BTCUSD.price")
        if "nasdaq" in text:
            abel_nodes.append("NDAQ.price")
        if "s&p" in text or "s&p 500" in text:
            abel_nodes.append("SPX.price")

        # Filter out false positives (sports, entertainment)
        noise = ["kings", "knights", "oscars", "grammy", "super bowl", "nfl",
                 "nba", "ufc", "uefa", "f1", "grand prix", "soccer",
                 "audio drama", "猫耳", "anime", "movie", "book", "song",
                 "president", "election", "traded by", "rangers"]
        if any(n in text for n in noise):
            continue

        if abel_nodes and q["level"] >= 1:
            covered.append({
                "id": f"fx_{q['id']}",
                "source": "FutureX",
                "category": "market_prediction",
                "question": q["prompt"][:500],
                "title": q["title"],
                "abel_nodes": list(set(abel_nodes)),
                "ground_truth": q["ground_truth"],
                "level": q["level"],
            })

    print(f"FutureX: {len(covered)}/{len(qs)} have Abel coverage (after noise filter)")
    return covered


# ============================================================
# 4. Batch test Abel API on covered questions
# ============================================================
def test_abel_signal(q):
    """Test if Abel returns usable signal for a question."""
    signals = []

    if q["source"] == "DeLLMa":
        # For each Abel-covered stock, try observe + neighbors
        for s in q["abel_covered_stocks"][:3]:
            ticker = s.replace("GOOGL", "GOOG")
            node = f"{ticker}.price"

            r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                        "--params-json", json.dumps({"target_node": node})])
            if r.get("ok"):
                pred = r.get("result", {}).get("prediction")
                signals.append({"op": f"observe({node})", "prediction": pred})

            r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "3"])
            if r.get("ok"):
                nbrs = r.get("result", {}).get("neighbors", [])
                if nbrs:
                    signals.append({"op": f"parents({node})", "count": len(nbrs)})

    elif q["source"] == "ForecastBench":
        for node in q["abel_nodes"][:2]:
            if node.endswith(".price"):
                # equity: observe
                r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                            "--params-json", json.dumps({"target_node": node})])
                if r.get("ok"):
                    pred = r.get("result", {}).get("prediction")
                    signals.append({"op": f"observe({node})", "prediction": pred})

                r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "3"])
                if r.get("ok") and r.get("result", {}).get("neighbors"):
                    signals.append({"op": f"parents({node})", "count": len(r["result"]["neighbors"])})
            else:
                # macro: markov blanket
                r = probe(["verb", "graph.markov_blanket",
                            "--params-json", json.dumps({"node_id": node})])
                if r.get("ok"):
                    nbrs = r.get("result", {}).get("neighbors", [])
                    if nbrs:
                        signals.append({"op": f"blanket({node})", "count": len(nbrs)})

    elif q["source"] == "FutureX":
        for node in q["abel_nodes"][:2]:
            if node.endswith(".price"):
                r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                            "--params-json", json.dumps({"target_node": node})])
                if r.get("ok"):
                    pred = r.get("result", {}).get("prediction")
                    signals.append({"op": f"observe({node})", "prediction": pred})

                r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "3"])
                if r.get("ok") and r.get("result", {}).get("neighbors"):
                    signals.append({"op": f"parents({node})", "count": len(r["result"]["neighbors"])})
            else:
                r = probe(["verb", "graph.markov_blanket",
                            "--params-json", json.dumps({"node_id": node})])
                if r.get("ok") and r.get("result", {}).get("neighbors"):
                    signals.append({"op": f"blanket({node})", "count": len(r["result"]["neighbors"])})

    return signals


if __name__ == "__main__":
    # Step 1: Filter
    print("="*60)
    print("STEP 1: FILTER FOR ABEL COVERAGE")
    print("="*60)

    dellma = process_dellma()
    fb = process_forecastbench()
    fx = process_futurex()

    all_covered = dellma + fb + fx
    print(f"\nTotal covered: {len(all_covered)}")

    # Step 2: Batch test Abel API (sample for speed)
    print(f"\n{'='*60}")
    print("STEP 2: BATCH TEST ABEL API")
    print("="*60)

    # Test ALL covered questions (may take a while)
    tested = []
    for i, q in enumerate(all_covered):
        signals = test_abel_signal(q)
        has_signal = len(signals) > 0
        q["abel_signals"] = signals
        q["abel_has_signal"] = has_signal
        tested.append(q)

        if (i+1) % 20 == 0:
            sig_count = sum(1 for t in tested if t["abel_has_signal"])
            print(f"  Tested {i+1}/{len(all_covered)}: {sig_count} with signal so far")

    # Summary
    with_signal = [t for t in tested if t["abel_has_signal"]]
    print(f"\nTotal with Abel signal: {len(with_signal)}/{len(tested)}")

    by_source = {}
    for t in with_signal:
        s = t["source"]
        by_source[s] = by_source.get(s, 0) + 1
    for s, c in by_source.items():
        print(f"  {s}: {c}")

    # Save
    out = os.path.join(RESULTS, "all_covered_tested.json")
    # Save without full_prompt to keep file manageable
    save_data = []
    for t in tested:
        entry = {k: v for k, v in t.items() if k != "full_prompt"}
        save_data.append(entry)
    with open(out, "w") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out}")
