import os
import asyncio
from playwright.async_api import async_playwright
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
ZENROWS_API_KEY = os.environ["ZENROWS_API_KEY"]
ID1 = os.environ["ID1"]
ID2 = os.environ["ID2"]
CUSTOMER_IDS = [ID1, ID2]

LOW_BALANCE_THRESHOLD = 100
BASE_URL = "https://customer.nesco.gov.bd/pre/panel"

CONNECTION_URL = f"wss://browser.zenrows.com?apikey={ZENROWS_API_KEY}&proxy_country=bd"

async def get_balance(customer_id):
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.connect_over_cdp(CONNECTION_URL)
            page = await browser.new_page()

            # Wait for initial page network idle with extended timeout
            await page.goto(BASE_URL, wait_until="networkidle", timeout=45000)
            await page.fill('input[name="cust_no"]', customer_id)

            # Wait for POST submission navigation to settle
            async with page.expect_navigation(wait_until="networkidle", timeout=30000):
                await page.click('input[name="submit"]')

            selector = "label:has-text('অবশিষ্ট ব্যালেন্স') + div input"
            await page.wait_for_selector(selector, timeout=25000)

            balance_value = await page.eval_on_selector(selector, "el => el.value")
            await browser.close()
            return float(balance_value.strip())
        except Exception:
            if browser:
                await browser.close()
            return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)

async def main():
    alerts = []
    for cid in CUSTOMER_IDS:
        balance = await get_balance(cid)
        if balance is None:
            alerts.append(f"🆔 `{cid}`\n⚠️ Could not fetch balance\n")
        elif balance < LOW_BALANCE_THRESHOLD:
            alerts.append(f"🚨 *LOW BALANCE ALERT*\n🆔 `{cid}`\n💰 Balance: *{balance} TK*\n")

        # Brief delay to allow proxy session cleanup between accounts
        await asyncio.sleep(3)

    if alerts:
        send_telegram("🔔 *NESCO Low Balance Alert*\n\n" + "\n".join(alerts))

if __name__ == "__main__":
    asyncio.run(main())