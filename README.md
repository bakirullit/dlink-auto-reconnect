# D-Link WiFi Reconnect Automation

This script automates connecting a **D-Link router (Beeline OS firmware)** to a Wi-Fi hotspot using Selenium.  

## Features
- Auto-login to router admin panel
- Detect if Wi-Fi is disconnected
- Refresh network list
- Reconnect automatically
- Headless mode (no browser UI)

## Installation
```bash
git clone https://github.com/<your-username>/dlink-wifi-reconnect.git
cd dlink-wifi-reconnect
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
