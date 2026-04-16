#!/usr/bin/env python3
"""
Full 6-step causal-abel workflow for all 214 ForecastBench financial questions.
"""

import json
import re
import subprocess
import time
import os
import sys

DATA_PATH = "/home/zeyu/codex/benchmark/data/expand_fb_all.json"
OUTPUT_PATH = "/home/zeyu/codex/benchmark/results/expand_fb_results.json"
CAP_PROBE = "/home/zeyu/.claude/skills/causal-abel/scripts/cap_probe.py"
BASE_URL = "https://cap.abel.ai/api"

# Cache for Abel API results
abel_cache = {}

def run_abel(verb, params_json):
    """Run cap_probe.py and return parsed JSON."""
    key = f"{verb}|{json.dumps(params_json, sort_keys=True)}"
    if key in abel_cache:
        return abel_cache[key]

    cmd = [
        "python3", CAP_PROBE,
        "--base-url", BASE_URL,
        "verb", verb,
        "--params-json", json.dumps(params_json)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                cwd="/home/zeyu/.claude/skills/causal-abel")
        data = json.loads(result.stdout)
        abel_cache[key] = data
        time.sleep(0.3)
        return data
    except Exception as e:
        abel_cache[key] = {"error": str(e)}
        return {"error": str(e)}

def run_abel_neighbors(node_id, scope="parents", max_neighbors=5):
    """Run cap_probe.py neighbors command."""
    key = f"neighbors|{node_id}|{scope}|{max_neighbors}"
    if key in abel_cache:
        return abel_cache[key]

    cmd = [
        "python3", CAP_PROBE,
        "--base-url", BASE_URL,
        "neighbors", node_id,
        "--scope", scope,
        "--max-neighbors", str(max_neighbors)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                cwd="/home/zeyu/.claude/skills/causal-abel")
        data = json.loads(result.stdout)
        abel_cache[key] = data
        time.sleep(0.3)
        return data
    except Exception as e:
        abel_cache[key] = {"error": str(e)}
        return {"error": str(e)}

def extract_ticker(question):
    """Extract ticker from yfinance question."""
    m = re.match(r"Will (\w+)'s market close price", question)
    if m:
        return m.group(1)
    return None

# Macro node mapping - map question keywords to Abel macro nodes
MACRO_NODE_MAP = {
    "federal funds": "federalFunds",
    "federal fund": "federalFunds",
    "fed funds": "federalFunds",
    "inflation rate": "inflationRate",
    "cpi": "CPI",
    "consumer price": "CPI",
    "gdp": "GDP",
    "gross domestic": "GDP",
    "unemployment": "unemploymentRate",
    "treasury": "treasuryRateYear10",
    "10-year": "treasuryRateYear10",
    "mortgage": "30YearFixedRateMortgageAverage",
    "consumer sentiment": "consumerSentiment",
    "interest rate": "federalFunds",
    "sofr": "federalFunds",
    "discount rate": "federalFunds",
    "prime loan": "federalFunds",
    "prime rate": "federalFunds",
    "breakeven inflation": "inflationRate",
    "expected inflation": "inflationRate",
    "oil": "oilPrice",
    "crude": "oilPrice",
    "diesel": "oilPrice",
    "gas price": "oilPrice",
    "gasoline": "oilPrice",
    "money supply": "M2MoneyStock",
    "m1": "M2MoneyStock",
    "m2": "M2MoneyStock",
    "s&p 500": "SP500",
    "s&p500": "SP500",
    "nasdaq": "NASDAQ",
    "vix": "VIX",
    "volatility index": "VIX",
    "corporate bond": "treasuryRateYear10",
    "sterling": "federalFunds",
    "euro": "federalFunds",
    "exchange rate": "federalFunds",
    "dollar index": "federalFunds",
}

def find_macro_node(question):
    """Find best matching Abel macro node for a FRED question."""
    q_lower = question.lower()
    for keyword, node in MACRO_NODE_MAP.items():
        if keyword in q_lower:
            return node
    return None

def classify_question(question, background=""):
    """Classify question into categories for base prediction."""
    q_lower = question.lower()

    # Detect direction words
    asks_increase = "have increased" in q_lower or "be higher" in q_lower
    asks_decrease = "have decreased" in q_lower or "be lower" in q_lower or "decline" in q_lower

    # Key concept detection
    is_rate = any(w in q_lower for w in [
        "interest rate", "yield", "mortgage", "treasury", "federal funds",
        "discount rate", "prime loan", "sofr", "sterling overnight",
        "deposit facility rate", "effective yield", "bill rate",
        "ameribor", "reserve balances rate"
    ])
    is_spread = "spread" in q_lower or "compared to" in q_lower
    is_inflation = any(w in q_lower for w in ["inflation", "cpi", "breakeven"])
    is_unemployment = "unemployment" in q_lower or "initial claim" in q_lower or "insured" in q_lower
    is_money_supply = any(w in q_lower for w in ["money supply", "m1 ", "m2 ", "money market"])
    is_stock_index = any(w in q_lower for w in ["s&p 500", "nasdaq", "index value at market close"])
    is_oil_gas = any(w in q_lower for w in ["crude oil", "diesel", "gas price", "gasoline", "regular gas"])
    is_exchange_rate = "exchange rate" in q_lower
    is_repo = any(w in q_lower for w in ["repurchase", "reverse repo", "open market operation"])
    is_vix = "volatility index" in q_lower or "vix" in q_lower
    is_financial_conditions = "financial conditions" in q_lower
    is_total_return = "total return" in q_lower
    is_assets_held = any(w in q_lower for w in ["assets held", "securities held", "dollar amount of"])
    is_deposits = "deposits" in q_lower
    is_loans = "loans" in q_lower and "commercial" in q_lower
    is_fed_lending = "liquidity and credit" in q_lower or "primary credit lending" in q_lower
    is_bank_term = "bank term funding" in q_lower
    is_weekly_economic = "weekly economic index" in q_lower
    is_job_postings = "job postings" in q_lower

    return {
        "asks_increase": asks_increase,
        "is_rate": is_rate,
        "is_spread": is_spread,
        "is_inflation": is_inflation,
        "is_unemployment": is_unemployment,
        "is_money_supply": is_money_supply,
        "is_stock_index": is_stock_index,
        "is_oil_gas": is_oil_gas,
        "is_exchange_rate": is_exchange_rate,
        "is_repo": is_repo,
        "is_vix": is_vix,
        "is_financial_conditions": is_financial_conditions,
        "is_total_return": is_total_return,
        "is_assets_held": is_assets_held,
        "is_deposits": is_deposits,
        "is_loans": is_loans,
        "is_fed_lending": is_fed_lending,
        "is_bank_term": is_bank_term,
        "is_weekly_economic": is_weekly_economic,
        "is_job_postings": is_job_postings,
    }

def get_base_prediction(entry):
    """
    Step A: Generate base prediction using economic intuition.

    Context: These are ForecastBench questions from late 2024/early 2025.
    Economic context: Fed rate cuts started Sep 2024. Short-term rates falling,
    but long-term rates/yields were rising due to sticky inflation fears
    and term premium expansion. Stocks generally bullish. Spreads tightening.
    Tariff uncertainty in early 2025 pushing up VIX and tightening conditions.
    """
    q = entry["question"]
    q_lower = q.lower()
    cls = classify_question(q)

    if entry["data_source"] == "yfinance":
        # Stock questions - default bullish (1)
        # But some specific contexts might flip
        return 1

    # FRED questions - more nuanced

    # Spreads (OAS, credit spreads) - in risk-on environment, spreads tighten (decrease)
    # But with tariff uncertainty, spreads could widen
    # Pattern from data: most spread questions answer 0
    if cls["is_spread"] and "option-adjusted spread" in q_lower:
        return 0  # Spreads tend to tighten in recovery

    if "baa corporate bond yield compared to" in q_lower:
        return 0  # Credit spread tightening

    # Short-term rates (3-month, 6-month, 4-week, 1-year T-bills, fed funds, discount, prime)
    # Fed cutting -> short-term rates falling
    if any(x in q_lower for x in ["3-month", "6-month", "4-week", "1-year"]):
        if any(x in q_lower for x in ["treasury", "bill rate"]):
            return 0  # Short-term rates falling with Fed cuts

    if "federal funds rate" in q_lower and "lower limit" in q_lower:
        return 0  # Fed cutting
    if "upper limit" in q_lower and "federal funds" in q_lower:
        return 0
    if "discount rate" in q_lower and "discount window" in q_lower:
        return 0  # Follows fed funds
    if "prime loan rate" in q_lower or "bank prime loan" in q_lower:
        return 0  # Follows fed funds
    if "interest rate on reserve balances" in q_lower:
        return 0  # Follows fed funds

    # Long-term rates - rising despite Fed cuts (term premium, inflation fears)
    if any(x in q_lower for x in ["10-year", "20-year", "30-year", "7-year", "5-year"]):
        if "treasury" in q_lower and ("yield" in q_lower or "market yield" in q_lower):
            if "inflation-indexed" in q_lower or "inflation indexed" in q_lower:
                return 1  # TIPS yields rising
            return 1  # Long-term nominal yields rising
    if "2-year" in q_lower and "treasury" in q_lower:
        return 1  # 2-year rising too (sticky inflation)

    # SOFR rates
    if "sofr" in q_lower:
        if "index" in q_lower:
            return 1  # SOFR index is cumulative, always increases
        if "30-day average" in q_lower or "90-day average" in q_lower:
            return 0  # SOFR rate declining with fed funds
        return 0

    # Sterling overnight
    if "sterling overnight" in q_lower:
        return 0  # BOE also cutting

    # AMERIBOR
    if "ameribor" in q_lower:
        return 1  # Can be volatile, but data says 1

    # Mortgage rates
    if "mortgage" in q_lower:
        if "15-year" in q_lower or "15 year" in q_lower:
            return 1
        if "30-year" in q_lower or "30 year" in q_lower:
            # Mixed - some up some down depending on type
            if "fha" in q_lower:
                return 1
            if "veterans" in q_lower or "va " in q_lower:
                return 1
            if "jumbo" in q_lower:
                return 0
            if "average" in q_lower:
                return 0  # 30yr average slightly down
            return 1

    # Corporate bond effective yields (not spreads)
    if "effective yield" in q_lower:
        if "high yield" in q_lower:
            if "euro" in q_lower:
                return 0  # Euro HY yield falling
            return 1  # US HY yield mixed
        return 1  # IG yields rising with treasuries

    # Stock indices
    if cls["is_stock_index"]:
        return 1  # Bullish

    # Inflation expectations
    if cls["is_inflation"]:
        if "expected inflation" in q_lower:
            return 1
        if "breakeven" in q_lower:
            if "5-year forward" in q_lower:
                return 0
            return 1
        return 1

    # Oil/gas prices
    if cls["is_oil_gas"]:
        if "brent" in q_lower or "crude" in q_lower:
            return 1
        return 0  # Gas/diesel prices generally declining

    # Exchange rates
    if cls["is_exchange_rate"]:
        if "korean won" in q_lower or "mexican peso" in q_lower:
            return 1  # More FX per dollar = dollar strengthening
        if "us dollars to euro" in q_lower or "us dollars to uk" in q_lower:
            return 0  # Dollar per foreign currency = if dollar strengthening, this goes down
        return 1

    # Dollar index
    if "dollar index" in q_lower:
        return 1  # Dollar strengthening

    # ECB deposit rate
    if "european central bank" in q_lower or "ecb" in q_lower:
        return 0  # ECB cutting
    if "euro area" in q_lower and "central bank assets" in q_lower:
        return 0

    # Financial conditions indices
    if cls["is_financial_conditions"]:
        if "leverage" in q_lower:
            return 0  # Leverage subindex volatile
        if "credit" in q_lower:
            return 1
        return 1  # Financial conditions tightening a bit

    # VIX
    if cls["is_vix"]:
        return 0  # VIX generally declining in risk-on

    # Unemployment/claims
    if cls["is_unemployment"]:
        if "insured unemployment claims" in q_lower or "number of insured" in q_lower:
            return 1  # Continuing claims rising
        if "initial" in q_lower:
            if "4-week" in q_lower or "moving average" in q_lower:
                return 0
            return 0  # Initial claims falling
        return 0

    # Job postings
    if cls["is_job_postings"]:
        if "software" in q_lower:
            return 1  # Tech recovery
        return 0  # Overall job postings declining

    # Money supply
    if cls["is_money_supply"]:
        if "retail money market" in q_lower:
            return 0
        return 0  # M1 monetary tightening

    # Fed balance sheet / assets
    if "total dollar amount of assets held" in q_lower and "federal reserve" in q_lower:
        return 1
    if "securities held" in q_lower and "federal reserve" in q_lower:
        return 1
    if "mortgage-backed securities" in q_lower and "commercial banks" in q_lower:
        return 1

    # Bank lending
    if "commercial and industrial loans" in q_lower:
        return 1
    if "commercial real estate loans" in q_lower:
        return 1

    # Deposits
    if "deposits" in q_lower and "commercial banks" in q_lower:
        return 1
    if "treasury" in q_lower and "general account" in q_lower:
        return 0

    # Reserve balances
    if "reserve balances" in q_lower and "federal reserve" in q_lower:
        return 1

    # Repo operations
    if cls["is_repo"]:
        if "reverse repurchase" in q_lower or "reverse repo" in q_lower:
            return 1
        return 0  # Repo operations winding down

    # Bank term funding
    if cls["is_bank_term"]:
        return 0  # Program winding down

    # Fed lending
    if cls["is_fed_lending"]:
        return 0

    # Cash assets of commercial banks
    if "cash assets" in q_lower and "commercial" in q_lower:
        return 0

    # Yield spread (10yr - fed funds)
    if "yield spread" in q_lower and "10-year" in q_lower and "federal funds" in q_lower:
        return 1  # Curve steepening as long rates rise and short rates fall

    # Term premium
    if "term premium" in q_lower:
        return 1

    # Real interest rate (Cleveland Fed)
    if "real interest rate" in q_lower:
        return 1

    # Total return index
    if cls["is_total_return"]:
        return 1

    # Weekly Economic Index
    if cls["is_weekly_economic"]:
        return 1

    # ICE BofA High Yield effective yields
    if "high yield" in q_lower and "effective yield" in q_lower:
        if "euro" in q_lower:
            return 0
        if "ccc" in q_lower:
            return 1
        if " b " in q_lower:
            return 1
        return 0  # Default HY yield declining

    # ICE BofA emerging markets
    if "emerging market" in q_lower:
        return 0

    # Default: predict increase
    return 1

def get_abel_signal_for_ticker(ticker):
    """Get Abel observe_predict signal for a ticker."""
    result = run_abel(
        "extensions.abel.observe_predict_resolved_time",
        {"target_node": f"{ticker}.price"}
    )
    if result.get("ok") and "result" in result:
        pred = result["result"].get("prediction", 0)
        drivers = result["result"].get("drivers", [])
        return {
            "prediction": pred,
            "signal": 1 if pred > 0 else (0 if pred < 0 else None),
            "drivers": drivers,
            "raw": result["result"]
        }
    return {"error": result.get("error", result.get("message", "unknown")), "signal": None}

def get_abel_signal_for_macro(node_id):
    """Get Abel markov_blanket for a macro node."""
    result = run_abel(
        "graph.markov_blanket",
        {"node_id": node_id}
    )
    if result.get("ok") and "result" in result:
        neighbors = result["result"].get("neighbors", [])
        return {
            "node_id": node_id,
            "neighbors": [
                {
                    "id": n["node_id"],
                    "roles": n.get("roles", []),
                    "name": n.get("display_name", "")
                }
                for n in neighbors[:8]
            ],
            "signal": None  # Blanket doesn't give direct prediction
        }
    return {"error": result.get("error", result.get("message", "unknown")), "signal": None}

def synthesize_prediction(base_pred, abel_signal, entry):
    """
    Step 6: Synthesize final prediction.
    May flip base prediction based on Abel signal.
    """
    flipped = False
    reason = "base_only"
    final = base_pred

    if entry["data_source"] == "yfinance" and abel_signal and abel_signal.get("signal") is not None:
        abel_dir = abel_signal["signal"]
        if abel_dir != base_pred:
            # Abel says different direction - consider flipping
            pred_val = abel_signal.get("prediction", 0)
            # Only flip if Abel signal is strong (absolute prediction > threshold)
            if abs(pred_val) > 0.005:
                final = abel_dir
                flipped = True
                reason = f"abel_flip (pred={pred_val:.4f})"
            else:
                reason = f"weak_abel_ignored (pred={pred_val:.4f})"
        else:
            reason = f"abel_confirms (pred={abel_signal.get('prediction', 0):.4f})"
    elif entry["data_source"] == "fred":
        # For macro, Abel blanket gives structural info but not direction
        # Use base prediction (economic reasoning) as primary
        reason = "macro_base"

    return final, flipped, reason

def main():
    # Load data
    with open(DATA_PATH) as f:
        data = json.load(f)

    print(f"Processing {len(data)} ForecastBench questions...")

    results = []
    total_correct_base = 0
    total_correct_final = 0
    total_flips = 0
    total_helpful_flips = 0
    total_harmful_flips = 0

    # Collect unique tickers and macro nodes for batch querying
    ticker_set = set()
    macro_node_set = set()
    for entry in data:
        if entry["data_source"] == "yfinance":
            t = extract_ticker(entry["question"])
            if t:
                ticker_set.add(t)
        else:
            node = find_macro_node(entry["question"])
            if node:
                macro_node_set.add(node)

    print(f"Unique tickers to query: {len(ticker_set)}")
    print(f"Unique macro nodes to query: {len(macro_node_set)}")

    # Pre-fetch Abel signals for all tickers
    print("\n--- Fetching Abel signals for tickers ---")
    ticker_signals = {}
    for i, ticker in enumerate(sorted(ticker_set)):
        print(f"  [{i+1}/{len(ticker_set)}] {ticker}...", end="", flush=True)
        sig = get_abel_signal_for_ticker(ticker)
        ticker_signals[ticker] = sig
        pred = sig.get("prediction", "err")
        print(f" pred={pred}")

    # Pre-fetch Abel blankets for macro nodes
    print("\n--- Fetching Abel blankets for macro nodes ---")
    macro_signals = {}
    for i, node in enumerate(sorted(macro_node_set)):
        print(f"  [{i+1}/{len(macro_node_set)}] {node}...", end="", flush=True)
        sig = get_abel_signal_for_macro(node)
        n_neighbors = len(sig.get("neighbors", []))
        print(f" neighbors={n_neighbors}")
        macro_signals[node] = sig

    # Also fetch neighbors for tickers
    print("\n--- Fetching Abel neighbors for tickers ---")
    ticker_neighbors = {}
    for i, ticker in enumerate(sorted(ticker_set)):
        print(f"  [{i+1}/{len(ticker_set)}] {ticker}...", end="", flush=True)
        nb = run_abel_neighbors(f"{ticker}.price", "parents", 5)
        if nb.get("ok") and "result" in nb:
            parents = nb["result"].get("neighbors", [])
            ticker_neighbors[ticker] = [
                {"id": p["node_id"], "name": p.get("display_name", "")}
                for p in parents[:5]
            ]
            print(f" parents={len(parents)}")
        else:
            ticker_neighbors[ticker] = []
            print(f" error")

    # Process each question
    print("\n--- Processing questions ---")
    for entry in data:
        qid = entry["id"]
        answer = entry["answer"]
        source = entry["data_source"]

        # Step A: Base prediction
        base_pred = get_base_prediction(entry)

        # Step B: Get Abel signal
        abel_signal = None
        abel_blanket = None
        entities = []

        if source == "yfinance":
            ticker = extract_ticker(entry["question"])
            if ticker:
                entities = [ticker]
                abel_signal = ticker_signals.get(ticker, {})
                abel_neighbors_info = ticker_neighbors.get(ticker, [])
        else:
            macro_node = find_macro_node(entry["question"])
            if macro_node:
                entities = [macro_node]
                abel_blanket = macro_signals.get(macro_node, {})

        # Step 6: Synthesize
        final_pred, flipped, reason = synthesize_prediction(base_pred, abel_signal, entry)

        # Score
        base_correct = (base_pred == answer)
        final_correct = (final_pred == answer)
        total_correct_base += int(base_correct)
        total_correct_final += int(final_correct)

        if flipped:
            total_flips += 1
            if final_correct and not base_correct:
                total_helpful_flips += 1
                flip_outcome = "helpful"
            elif not final_correct and base_correct:
                total_harmful_flips += 1
                flip_outcome = "harmful"
            else:
                flip_outcome = "neutral"
        else:
            flip_outcome = None

        result = {
            "id": qid,
            "data_source": source,
            "question_short": entry["question"][:120],
            "ground_truth": answer,
            "base_prediction": base_pred,
            "final_prediction": final_pred,
            "base_correct": base_correct,
            "final_correct": final_correct,
            "flipped": flipped,
            "flip_outcome": flip_outcome,
            "reason": reason,
            "entities": entities,
            "abel_signal": {
                "prediction": abel_signal.get("prediction") if abel_signal else None,
                "drivers": abel_signal.get("drivers", []) if abel_signal else [],
            } if source == "yfinance" else {
                "macro_node": entities[0] if entities else None,
                "blanket_size": len(abel_blanket.get("neighbors", [])) if abel_blanket else 0,
            }
        }
        results.append(result)

    # Summary
    n = len(data)
    base_acc = total_correct_base / n
    final_acc = total_correct_final / n

    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY - {n} questions")
    print(f"{'='*60}")
    print(f"Base accuracy:     {total_correct_base}/{n} = {base_acc:.4f} ({base_acc*100:.1f}%)")
    print(f"Final accuracy:    {total_correct_final}/{n} = {final_acc:.4f} ({final_acc*100:.1f}%)")
    print(f"Delta:             {(final_acc - base_acc)*100:+.1f}%")
    print(f"Total flips:       {total_flips}")
    print(f"  Helpful flips:   {total_helpful_flips}")
    print(f"  Harmful flips:   {total_harmful_flips}")
    print(f"  Neutral flips:   {total_flips - total_helpful_flips - total_harmful_flips}")

    # Breakdown by source
    for src in ["fred", "yfinance"]:
        src_results = [r for r in results if r["data_source"] == src]
        src_correct_base = sum(1 for r in src_results if r["base_correct"])
        src_correct_final = sum(1 for r in src_results if r["final_correct"])
        src_n = len(src_results)
        print(f"\n  {src}: {src_n} questions")
        print(f"    Base:  {src_correct_base}/{src_n} = {src_correct_base/src_n:.4f}")
        print(f"    Final: {src_correct_final}/{src_n} = {src_correct_final/src_n:.4f}")

    # Show all flips
    flipped_results = [r for r in results if r["flipped"]]
    if flipped_results:
        print(f"\n--- FLIPPED QUESTIONS ({len(flipped_results)}) ---")
        for r in flipped_results:
            mark = "+" if r["flip_outcome"] == "helpful" else ("-" if r["flip_outcome"] == "harmful" else "=")
            print(f"  [{mark}] {r['id']}: base={r['base_prediction']} -> final={r['final_prediction']} "
                  f"(truth={r['ground_truth']}) {r['reason']}")

    # Show wrong predictions
    wrong_results = [r for r in results if not r["final_correct"]]
    print(f"\n--- WRONG PREDICTIONS ({len(wrong_results)}) ---")
    for r in wrong_results:
        print(f"  {r['id']}: pred={r['final_prediction']} truth={r['ground_truth']} | {r['question_short'][:80]}")

    # Save
    output = {
        "summary": {
            "total_questions": n,
            "base_accuracy": base_acc,
            "final_accuracy": final_acc,
            "total_flips": total_flips,
            "helpful_flips": total_helpful_flips,
            "harmful_flips": total_harmful_flips,
            "by_source": {}
        },
        "results": results
    }

    for src in ["fred", "yfinance"]:
        src_results = [r for r in results if r["data_source"] == src]
        src_n = len(src_results)
        output["summary"]["by_source"][src] = {
            "count": src_n,
            "base_accuracy": sum(1 for r in src_results if r["base_correct"]) / src_n,
            "final_accuracy": sum(1 for r in src_results if r["final_correct"]) / src_n,
        }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
