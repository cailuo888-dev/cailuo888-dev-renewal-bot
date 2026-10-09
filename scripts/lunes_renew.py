#!/usr/bin/env python3
"""Lunes Host renewal - login to betadash.lunes.host (login = renewal)."""
import os
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def renew_lunes():
    email = os.environ.get('LUNES_EMAIL')
    password = os.environ.get('LUNES_PASSWORD')
    if not email or not password:
        return "SKIP: LUNES_EMAIL/PASSWORD not set"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        try:
            page = browser.new_page()
            logger.info("Navigating to betadash.lunes.host...")
            page.goto('https://betadash.lunes.host/', timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            logger.info(f"Page title: {page.title()}")
            logger.info(f"URL after goto: {page.url}")

            # Try multiple selector strategies
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[placeholder*="mail" i]',
                '#email',
            ]
            pwd_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password',
            ]

            email_filled = False
            for sel in email_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, email, timeout=10000)
                        email_filled = True
                        logger.info(f"Filled email with selector: {sel}")
                        break
                except Exception:
                    continue
            if not email_filled:
                return "FAIL: email input not found. Page HTML snippet: " + page.content()[:500]

            pwd_filled = False
            for sel in pwd_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, password, timeout=10000)
                        pwd_filled = True
                        logger.info(f"Filled password with selector: {sel}")
                        break
                except Exception:
                    continue
            if not pwd_filled:
                return "FAIL: password input not found"

            # Try submit button
            btn_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'button:has-text("登录")',
            ]
            clicked = False
            for sel in btn_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        page.click(sel, timeout=10000)
                        clicked = True
                        logger.info(f"Clicked submit: {sel}")
                        break
                except Exception:
                    continue
            if not clicked:
                page.keyboard.press('Enter')
                logger.info("Pressed Enter as fallback")

            page.wait_for_timeout(8000)
            content = page.content().lower()
            url = page.url
            logger.info(f"After login URL: {url}")
            if 'dashboard' in content or 'server' in content or 'logout' in content:
                return "OK: logged in, renewal complete"
            if 'invalid' in content or 'incorrect' in content or 'failed' in content:
                return "FAIL: login rejected (bad credentials?)"
            return f"UNKNOWN: url={url}, title={page.title()}"
        except Exception as e:
            logger.exception("Lunes renewal exception")
            return f"ERROR: {e}"
        finally:
            browser.close()
