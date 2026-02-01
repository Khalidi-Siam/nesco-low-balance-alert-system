# NESCO Bill Checker

A Python script that automatically checks prepaid electricity balance from [NESCO (Northern Electricity Supply Company)](https://customer.nesco.gov.bd/pre/panel) and sends Telegram alerts when the balance is low. Runs automatically via GitHub Actions on a schedule.

## Features

- 🔍 Fetches prepaid meter balance using Playwright browser automation
- 📱 Sends Telegram notifications for low balance alerts
- 👥 Supports multiple customer IDs
- ⚡ Configurable low balance threshold (default: 100 TK)
- 🕐 **Scheduled Runs** via GitHub Actions (Tuesdays & Saturdays at 4 PM Bangladesh time)
- 🔧 Manual trigger support via `workflow_dispatch`

## How It Works

1. GitHub Actions runs the script on schedule (or manually triggered)
2. The script uses Playwright to visit the NESCO customer portal
3. Fetches the remaining balance for each configured customer ID
4. If balance is below threshold (100 TK), sends a Telegram alert

## Requirements

- Python 3.11+
- Playwright
- Telegram Bot Token & Chat ID

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
| `CONSUMER_IDS` | Comma-separated list of NESCO customer IDs |

For GitHub Actions, add these as repository secrets.

## Usage

### Local
```bash
python nesco.py
```

### GitHub Actions
The workflow runs automatically on:
- **Schedule**: Every Tuesday and Saturday at 4 PM Bangladesh time (UTC+6)
- **Manual**: Trigger via GitHub Actions → "Run workflow"

