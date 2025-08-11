from typing import Optional, Dict, Any, List
import requests


class ApiClient:
    def __init__(self, base_url: str = ""):
        self._base_url = base_url.strip()

    def set_base_url(self, base_url: str):
        self._base_url = base_url.strip()

    def _url(self, path: str) -> str:
        if not self._base_url:
            raise RuntimeError("API base URL is not set")
        return f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"

    def list_tasks(self) -> List[Dict[str, Any]]:
        resp = requests.get(self._url("/tasks"), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def create_task(self, title: str, description: str = "") -> Dict[str, Any]:
        resp = requests.post(self._url("/tasks"), json={"title": title, "description": description}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def update_task(self, task_id: int, **fields) -> Dict[str, Any]:
        resp = requests.patch(self._url(f"/tasks/{task_id}"), json=fields, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def delete_task(self, task_id: int) -> None:
        resp = requests.delete(self._url(f"/tasks/{task_id}"), timeout=10)
        resp.raise_for_status()
        return None