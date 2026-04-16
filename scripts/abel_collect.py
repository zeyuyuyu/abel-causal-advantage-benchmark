#!/usr/bin/env python3
"""Collect Abel API data for batch_8 tickers with retry logic."""
import json
import subprocess
import time
import sys

SKILL_DIR = "/home/zeyu/.claude/skills/causal-abel"
BASE_CMD = [
    "python3", f"{SKILL_DIR}/scripts/cap_probe.py",
    "--base-url", "https://cap.abel.ai/api",
    "--env-file", f"{SKILL_DIR}/.env.skill",
    "--compact"
]

TICKERS = ["AAPL", "AMZN", "BAC", "DIS", "GOOG", "INTC", "JPM", "META", "TSLA"]

def call_abel(verb, node_id, max_retries=5):
    """Call Abel API with exponential backoff on rate limit."""
    cmd = BASE_CMD + [verb, node_id]
    for attempt in range(max_retries):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip() or result.stderr.strip()
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            data = {"ok": False, "raw": output}

        if data.get("ok") == True:
            return data

        if data.get("status_code") == 429:
            wait = min(3 * (2 ** attempt), 60)
            print(f"  429 on {verb} {node_id}, waiting {wait}s (attempt {attempt+1}/{max_retries})", flush=True)
            time.sleep(wait)
            continue
        else:
            return data  # non-retryable error

    return data  # return last attempt

def main():
    cache = {}

    for ticker in TICKERS:
        node = f"{ticker}.price"
        print(f"\n=== {ticker} ===", flush=True)

        # markov-blanket
        print(f"  markov-blanket...", flush=True)
        mb = call_abel("markov-blanket", node)
        cache.setdefault(ticker, {})["markov_blanket"] = mb
        time.sleep(1.5)

        # observe
        print(f"  observe...", flush=True)
        obs = call_abel("observe", node)
        cache[ticker]["observe"] = obs
        time.sleep(1.5)

        # traverse-parents
        print(f"  traverse-parents...", flush=True)
        par = call_abel("traverse-parents", node)
        cache[ticker]["traverse_parents"] = par
        time.sleep(1.5)

    out_path = "/home/zeyu/codex/benchmark/results/abel_cache_batch8.json"
    with open(out_path, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"\nSaved to {out_path}", flush=True)

if __name__ == "__main__":
    main()
