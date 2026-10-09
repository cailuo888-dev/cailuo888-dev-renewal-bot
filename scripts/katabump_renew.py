#!/usr/bin/env python3
"""Katabump renewal - login and click Renew for server 394212.
Note: Cloudflare Turnstile may block automated browsers."""
import os
from playwright.sync_api import sync_playwright

def renew_katabump():
    email = os.environ.get('KATABUMP_EMAIL')
    password = os.environ.get('KATABUMP_PASSWORD')
    if not email or not password:
        return "SKIP: KATABUMP_EMAIL/PASSWORD not set"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto('https://dashboard.katabump.com/', timeout=30000)
            page.wait_for_timeout(3000)
            # Check for Cloudflare challenge
            if 'turnstile' in page.content().lower() or 'cloudflare' in page.content().lower():
                return "BLOCKED: Cloudflare Turnstile detected, manual renewal required"
            # Try login
            page.fill('input[type="email"], input[name="email"]', email)
            page.fill('input[type="password"], input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            # Look for server 394212 and Renew button
            # This is best-effort; actual selectors may vary
            content = page.content()
            if '394212' in content:
                return "OK: logged in, server found (manual Renew click may still be needed)"
            return "UNKNOWN: login status unclear"
        finally:
            browser.close()
