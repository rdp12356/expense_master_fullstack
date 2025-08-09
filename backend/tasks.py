# tasks.py
import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.beat_schedule = {
    "fetch-rates-every-30-minutes": {
        "task": "tasks.fetch_rates_task",
        "schedule": int(os.getenv("FETCH_INTERVAL_SECONDS",1800)),
        "args": (os.getenv("FETCH_BASE","USD"),)
    }
}
celery.conf.timezone = "UTC"

@celery.task(name="tasks.fetch_rates_task")
def fetch_rates_task(base="USD"):
    # defer to fetcher.fetch_and_store
    from fetcher import fetch_and_store
    res = fetch_and_store(base)
    return res
