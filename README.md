# NESCO Bill Checker

A Python script that automatically checks prepaid electricity balance from [NESCO (Northern Electricity Supply Company)](https://customer.nesco.gov.bd/pre/panel) and sends Telegram alerts when the balance is low. Runs automatically via GitHub Actions on a schedule.

## Features

- 🔍 Fetches prepaid meter balance using Playwright browser automation
- 🌍 Bypasses geo-restriction via [Zenrows](https://zenrows.com/) browser proxy (NESCO portal is only accessible from Bangladesh)
- 📱 Sends Telegram notifications for low balance alerts
- 👥 Supports multiple customer IDs (`ID1`, `ID2`)
- ⚡ Configurable low balance threshold (default: 100 TK)
- 🕐 **Scheduled Runs** via GitHub Actions
- 🔧 Manual trigger support via `workflow_dispatch`

## How It Works

1. GitHub Actions runs the script on schedule (or manually triggered)
2. The script connects to a Zenrows browser proxy (located in Bangladesh) to bypass the geo-restriction — the NESCO customer portal blocks access from non-Bangladesh IP addresses, which is why GitHub-hosted runners in the US would otherwise be blocked
3. Playwright automation visits the NESCO customer portal through the proxy
4. Fetches the remaining balance for each configured customer ID (`ID1`, `ID2`)
5. If balance is below threshold (100 TK), sends a Telegram alert

## Requirements

- Python 3.11+
- Playwright
- Telegram Bot Token & Chat ID
- Zenrows account (for the browser proxy to bypass geo-restriction)
- Active connection to a Bangladesh IP (handled automatically via the Zenrows proxy)

## Installation

```bash
pip install -r requirements.txt
playwright install
```

## Environment Variables / GitHub Secrets

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot API token |
| `CHAT_ID` | Telegram Chat ID for notifications |
| `ZENROWS_API_KEY` | Zenrows API key (used for the browser proxy to bypass the Bangladesh-only geo-restriction on the NESCO portal) |
| `ID1` | First NESCO customer ID |
| `ID2` | Second NESCO customer ID |

For GitHub Actions, add these as repository secrets.

## Zenrows Browser Proxy

The NESCO customer portal (`customer.nesco.gov.bd`) is only accessible from Bangladesh. Since GitHub Actions runners operate from non-Bangladesh IPs, the script uses the [Zenrows browser proxy](https://zenrows.com/) with `proxy_country=bd` to route all browser traffic through a Bangladesh-based browser session.

You need an active Zenrows account with browser endpoint access. Get your API key from the [Zenrows dashboard](https://app.zenrows.com/) and set it as the `ZENROWS_API_KEY` secret.

## Usage

### Local
```bash
python nesco.py
```

### GitHub Actions
The workflow runs automatically on:
- **Schedule**: Every Tuesday and Saturday at 4 PM Bangladesh time (UTC+6)
- **Manual**: Trigger via GitHub Actions → "Run workflow"

