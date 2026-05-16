#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import requests

API_KEY = "AIzaSyBAJuLUQwDtMVSM5YPHpEaRVLXwuRuH7UI"

URL = "https://developerknowledge.googleapis.com/mcp"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
}


def run_handshake():
    session = requests.Session()
    session.headers.update(headers)

    print(f"--- Step 1: Initialize ({URL}) ---")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }

    try:
        resp = session.post(URL, json=init_payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}...")  # Truncate for brevity

        if resp.status_code != 200:
            print("Initialize failed.")
            return

        print(
            """
--- Step 2: Initialized Notification ---"""
        )
        notify_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        # Notifications don't expect a response, but we send it to complete handshake
        resp = session.post(URL, json=notify_payload)
        print(f"Status: {resp.status_code}")

        print(
            """
--- Step 3: List Tools ---"""
        )
        list_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},  # explicit empty params
        }
        resp = session.post(URL, json=list_payload)
        print(f"Tools Found: {resp.text[:200]}...")  # Truncate

        print(
            """
--- Step 4: Search Documents (User Payload) ---"""
        )
        search_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_documents",
                "arguments": {"query": "Cloud Run authentication best practices"},
            },
        }
        resp = session.post(URL, json=search_payload)
        print(f"Status: {resp.status_code}")
        print(f"Search Result: {resp.text[:500]}...")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run_handshake()
