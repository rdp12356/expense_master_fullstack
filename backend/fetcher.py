# fetcher.py
import requests
from datetime import datetime
from models import ExchangeRate, db

PROVIDERS = [
    {"name":"exchangerate.host", "url":"https://api.exchangerate.host/latest?base={base}"}
]

def fetch_and_store(base="USD"):
    for p in PROVIDERS:
        try:
            r = requests.get(p["url"].format(base=base), timeout=15)
            if r.status_code != 200:
                continue
            j = r.json()
            rates = j.get("rates", {})
            ts = datetime.utcnow()
            saved = 0
            for target, rate in rates.items():
                try:
                    rate_f = float(rate)
                except:
                    continue
                ex = ExchangeRate.query.filter_by(base=base.upper(), target=target.upper()).first()
                if ex:
                    ex.rate = rate_f
                    ex.fetched_at = ts
                else:
                    nr = ExchangeRate(base=base.upper(), target=target.upper(), rate=rate_f, fetched_at=ts)
                    db.session.add(nr)
                saved += 1
            db.session.commit()
            return {"ok":True, "provider":p["name"], "saved":saved}
        except Exception as e:
            print("Provider error:", p["name"], e)
            continue
    return {"ok":False, "error":"all providers failed"}
