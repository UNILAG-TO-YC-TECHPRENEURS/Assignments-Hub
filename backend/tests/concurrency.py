#!/usr/bin/env python3
"""
Concurrency test for Assignment Hub API.
Uses a separate token for each concurrent request.
"""

import requests
import concurrent.futures
import sys
import time

BASE_URL = "https://assignment-hub.duckdns.org/api"
DEPARTMENT = "cs"
CONCURRENCY = 5   # number of simultaneous users

def get_token():
    """Obtain a fresh token."""
    resp = requests.post(f"{BASE_URL}/tokens/", json={})
    resp.raise_for_status()
    return resp.json()["token"]

def generate_assignment(token):
    """Submit an assignment generation request."""
    payload = {
        "token": token,
        "name": "Test User",
        "matric_number": "12345",
        "email": "test@example.com",
        "department": DEPARTMENT
    }
    start = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/generate/", json=payload, timeout=300)
        elapsed = time.time() - start
        return resp.status_code, elapsed, resp.text[:100]  # first 100 chars
    except Exception as e:
        elapsed = time.time() - start
        return 0, elapsed, str(e)

def main():
    print(f"Starting test with {CONCURRENCY} concurrent users...")
    tokens = []
    for i in range(CONCURRENCY):
        try:
            token = get_token()
            tokens.append(token)
            print(f"Token {i+1}: {token}")
        except Exception as e:
            print(f"Failed to get token {i+1}: {e}")
            sys.exit(1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        future_to_token = {executor.submit(generate_assignment, token): token for token in tokens}
        results = []
        for future in concurrent.futures.as_completed(future_to_token):
            token = future_to_token[future]
            try:
                status, elapsed, snippet = future.result()
                results.append((token, status, elapsed, snippet))
            except Exception as e:
                results.append((token, 0, 0, str(e)))

    print("\n--- Results ---")
    successes = 0
    for token, status, elapsed, snippet in results:
        if status == 200:
            print(f"✅ {token} -> OK ({elapsed:.2f}s)")
            successes += 1
        else:
            print(f"❌ {token} -> status {status} after {elapsed:.2f}s: {snippet}")
    print(f"\nSuccess rate: {successes}/{CONCURRENCY}")

if __name__ == "__main__":
    main()