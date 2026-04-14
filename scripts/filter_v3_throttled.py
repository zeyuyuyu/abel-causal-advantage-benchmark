#!/usr/bin/env python3
"""
V3: Same as V2 but with rate limiting (1 second between API calls).
Processes all benchmark sources: DeLLMa, ForecastBench, FutureX.
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

call_count = 0
def probe(args, timeout=25):
    global call_count
    call_count += 1
    time.sleep(1.0)  # rate limit: 1 call per second
    cmd = ["python3", f"{SKILL_DIR}/scripts/cap_probe.py", "--base-url", BASE_URL] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        data = json.loads(r.stdout or r.stderr)
        if data.get("status_code") == 429:
            print(f"    [RATE LIMITED at call #{call_count}, waiting 30s...]")
            time.sleep(30)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            data = json.loads(r.stdout or r.stderr)
        return data
    except:
        return {"ok": False}


def process_dellma():
    with open(os.path.join(DATA, "dellma_stock_questions.json")) as f:
        qs = json.load(f)
    covered = []
    for q in qs:
        abel_stocks = []
        for s in q["stocks"]:
            mapped = "GOOG" if s == "GOOGL" else s
            if mapped in ABEL_EQUITY_NODES:
                abel_stocks.append(mapped)
        if abel_stocks:
            covered.append({
                "id": q["id"], "source": "DeLLMa", "category": "stock_decision",
                "question": q["prompt"][:300],
                "stocks": q["stocks"], "abel_stocks": abel_stocks,
                "ground_truth": q["ground_truth"],
                "gt_return": q.get("ground_truth_return_pct"),
            })
    return covered


def process_forecastbench():
    with open(os.path.join(DATA, "forecastbench_financial.json")) as f:
        qs = json.load(f)
    covered = []
    for q in qs:
        src = q.get("data_source", "")
        question = q.get("question", "")
        bg = q.get("background", "")
        if src == "yfinance":
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
            if "10-year treasury" in text or "10 year treasury" in text:
                node = "treasuryRateYear10"
            elif "federal fund" in text:
                node = "federalFunds"
            elif "consumer price index" in text:
                node = "CPI"
            elif "unemployment" in text:
                node = "unemploymentRate"
            elif "initial claim" in text or "jobless claim" in text:
                node = "initialClaims"
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
            elif "gdp" in text.split() or "gross domestic" in text:
                node = "GDP"
            if node:
                covered.append({
                    "id": q["id"], "source": "ForecastBench",
                    "category": "macro_prediction",
                    "question": question, "abel_node": node,
                    "ground_truth": q["answer"],
                })
    return covered


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
        for ticker in ABEL_EQUITY_NODES:
            if re.search(rf'\b{ticker}\b', text):
                abel_node = f"{ticker}.price"
                category = "stock_prediction"
                break
        if not abel_node:
            if "NVIDIA" in text or "Nvidia" in text:
                abel_node = "NVDA.price"; category = "stock_prediction"
            elif "Apple stock" in text or "(AAPL)" in text:
                abel_node = "AAPL.price"; category = "stock_prediction"
            elif "Li Auto" in text:
                abel_node = "LI.price"; category = "stock_prediction"
            elif "NASDAQ" in text and ("index" in text.lower() or "composite" in text.lower()):
                abel_node = "NDAQ.price"; category = "index_prediction"
            elif "S&P 500" in text:
                category = "index_prediction"; abel_node = "SPX.price"
            elif "Bitcoin" in text:
                abel_node = "BTCUSD.price"; category = "crypto_prediction"
            elif re.search(r'\b(inflation|CPI)\b', text, re.I) and not re.search(r'(sport|game|oscar)', text, re.I):
                abel_node = "CPI"; category = "macro_prediction"
            elif "Crude Oil" in text:
                abel_node = "CL.price"; category = "commodity_prediction"
            elif re.search(r'Gold.*\(GC\)', text):
                abel_node = "GC.price"; category = "commodity_prediction"
        if abel_node and category:
            covered.append({
                "id": f"fx_{q['id']}", "source": "FutureX", "category": category,
                "question": prompt[:400], "title": title,
                "abel_node": abel_node, "ground_truth": q["ground_truth"],
                "level": q["level"],
            })
    return covered


def test_signal(q):
    signals = []
    if q["source"] == "DeLLMa":
        for s in q["abel_stocks"][:2]:  # limit to 2 stocks to save API calls
            node = f"{s}.price"
            r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                        "--params-json", json.dumps({"target_node": node})])
            if r.get("ok"):
                signals.append({"op": f"observe({node})", "val": r["result"].get("prediction")})
            r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "3"])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"parents({node})", "n": len(r["result"]["neighbors"])})
    else:
        node = q.get("abel_node", "")
        if node.endswith(".price"):
            r = probe(["verb", "extensions.abel.observe_predict_resolved_time",
                        "--params-json", json.dumps({"target_node": node})])
            if r.get("ok"):
                signals.append({"op": f"observe({node})", "val": r["result"].get("prediction")})
            r = probe(["neighbors", node, "--scope", "parents", "--max-neighbors", "3"])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"parents({node})", "n": len(r["result"]["neighbors"])})
        elif node in ABEL_MACRO_BLANKET:
            r = probe(["verb", "graph.markov_blanket",
                        "--params-json", json.dumps({"node_id": node})])
            if r.get("ok") and r.get("result", {}).get("neighbors"):
                signals.append({"op": f"blanket({node})", "n": len(r["result"]["neighbors"])})
    return signals


if __name__ == "__main__":
    print("STEP 1: PRECISE FILTERING")
    dellma = process_dellma()
    fb = process_forecastbench()
    fx = process_futurex()
    all_q = dellma + fb + fx
    print(f"DeLLMa={len(dellma)}, ForecastBench={len(fb)}, FutureX={len(fx)}, Total={len(all_q)}")

    print(f"\nSTEP 2: TESTING ({len(all_q)} questions, ~1s/call, est {len(all_q)*3//60}min)")
    for i, q in enumerate(all_q):
        signals = test_signal(q)
        q["abel_signals"] = signals
        q["abel_has_signal"] = len(signals) > 0
        if (i+1) % 20 == 0:
            n_sig = sum(1 for x in all_q[:i+1] if x.get("abel_has_signal"))
            print(f"  [{i+1}/{len(all_q)}] signals={n_sig} (api calls={call_count})")

    with_signal = [q for q in all_q if q["abel_has_signal"]]
    print(f"\n=== RESULTS ===")
    print(f"Total with signal: {len(with_signal)}/{len(all_q)}")
    by_src = {}
    for q in with_signal:
        key = f"{q['source']}:{q['category']}"
        by_src[key] = by_src.get(key, 0) + 1
    for k, v in sorted(by_src.items()):
        print(f"  {k}: {v}")

    out = os.path.join(RESULTS, "v3_with_signal.json")
    with open(out, "w") as f:
        json.dump([{k:v for k,v in q.items()} for q in with_signal], f, indent=2, ensure_ascii=False)
    all_out = os.path.join(RESULTS, "v3_all_tested.json")
    with open(all_out, "w") as f:
        json.dump([{k:v for k,v in q.items()} for q in all_q], f, indent=2, ensure_ascii=False)
    print(f"Saved: {out}, {all_out}")
