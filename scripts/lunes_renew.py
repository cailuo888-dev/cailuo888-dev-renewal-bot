#!/usr/bin/env python3
"""Lunes Host renewal - login to betadash.lunes.host (login = renewal)."""
import os
from playwright.sync_api import sync_playwright

def renew_lunes():
    email = os.environ.get('LUNES_EMAIL')
    password = os.environ.get('LUNES_PASSWORD')
    if not email or not password:
        return "SKIP: LUNES_EMAIL/PASSWORD not set"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto('https://betadash.lunes.host/', timeout=30000)
            # Fill login form
            page.fill('input[type="email"], input[name="email"]', email)
            page.fill('input[type="password"], input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            # Check if logged in (dashboard visible)
            content = page.content()
            if 'dashboard' in content.lower() or 'server' in content.lower():
                return "OK: logged in, renewal complete"
            return "UNKNOWN: login status unclear"
        finally:
            browser.close()
