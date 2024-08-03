import requests
import time
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def post_media_hook(self, url: str, iphone: bool = False) -> Dict[str, Any]:
        json_data = {"url": url, "iphone": iphone}
        response = requests.post(f"{self.base_url}/hooks/media", headers=self.headers, json=json_data)
        response.raise_for_status()
        return response.json()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/v1/job_status/{job_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_job_completion(self, job_id: str, check_interval: int = 5) -> Dict[str, Any] | None:
        while True:
            job_status_response = self.get_job_status(job_id)
            status = job_status_response.get("status")
            if status == "complete":
                return job_status_response["payload"]
            elif status != "working":
                break
            time.sleep(check_interval)
        return None