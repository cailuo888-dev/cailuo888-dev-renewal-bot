#!/usr/bin/env python3
"""Katabump renewal - login and click Renew for server 394212.
Note: Cloudflare Turnstile may block automated browsers."""
import os
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def renew_katabump():
    email = os.environ.get('KATABUMP_EMAIL')
    password = os.environ.get('KATABUMP_PASSWORD')
    if not email or not password:
        return "SKIP: KATABUMP_EMAIL/PASSWORD not set"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        try:
            page = browser.new_page()
            logger.info("Navigating to dashboard.katabump.com...")
            page.goto('https://dashboard.katabump.com/', timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(4000)
            html = page.content().lower()
            if 'turnstile' in html or 'cf-turnstile' in html or 'just a moment' in html:
                return "BLOCKED: Cloudflare Turnstile/verification detected, manual renewal required"
            logger.info(f"Page title: {page.title()}")

            email_selectors = ['input[type="email"]', 'input[name="email"]', '#email']
            pwd_selectors = ['input[type="password"]', 'input[name="password"]', '#password']
            for sel in email_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, email, timeout=10000)
                        logger.info(f"Filled email: {sel}")
                        break
                except Exception:
                    continue
            for sel in pwd_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, password, timeout=10000)
                        logger.info(f"Filled password: {sel}")
                        break
                except Exception:
                    continue
            for sel in ['button[type="submit"]', 'button:has-text("Login")', 'button:has-text("Sign in")']:
                try:
                    if page.locator(sel).count() > 0:
                        page.click(sel, timeout=10000)
                        logger.info(f"Clicked: {sel}")
                        break
                except Exception:
                    continue
            page.wait_for_timeout(8000)
            content = page.content()
            if '394212' in content:
                # Try to find and click Renew button near server 394212
                try:
                    renew_btn = page.locator('button:has-text("Renew")').first
                    if renew_btn.count() > 0:
                        renew_btn.click(timeout=10000)
                        page.wait_for_timeout(5000)
                        return "OK: clicked Renew for server"
                except Exception as e:
                    logger.warning(f"Renew click failed: {e}")
                return "OK: logged in, server 394212 found (Renew may need manual click)"
            if 'turnstile' in content.lower():
                return "BLOCKED: Cloudflare Turnstile appeared after login"
            return f"UNKNOWN: title={page.title()}, url={page.url}"
        except Exception as e:
            logger.exception("Katabump renewal exception")
            return f"ERROR: {e}"
        finally:
            browser.close()
