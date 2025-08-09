# ExpenseMaster — Full Stack (Flask backend + Kivy frontend)

## Overview
This project provides:
- Flask backend with magic-link email login, API key issuance, exchange rate fetcher
- Kivy frontend to request magic link and open dashboard
- Outlook SMTP integration (use `.env` to configure)

## Quick start
1. Backend:
   - `cd backend`
   - create `.env` from `.env.template` and fill values (SMTP_PASSWORD must be your Outlook app password)
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `python db_init.py`
   - `python app.py`
2. Frontend:
   - `cd frontend_kivy`
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `python main.py`

## Notes
- Do not commit `.env` or secrets to Git
- Revoke the temporary Outlook app password you exposed in chat; generate a new one & use it locally
- For production, use HTTPS, configure SPF/DKIM if sending from custom domain, and consider SendGrid/Mailgun for deliverability
