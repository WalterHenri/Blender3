import requests
from datetime import datetime

from TaskModel import TextTo3DTask


class MeshyAPI:
    BASE_URL = "https://api.meshy.ai/v2"

    def __init__(self, api_key):
        self.api_key = api_key

    def _make_request(self, method, endpoint, data=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.request(method, url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Response content: {response.text}")
            raise

    def create_preview_task(self, prompt, art_style="realistic", negative_prompt="", seed=None):
        data = {
            "mode": "preview",
            "prompt": prompt,
            "art_style": art_style,
            "negative_prompt": negative_prompt,
        }
        if seed is not None:
            data["seed"] = seed
        result = self._make_request("POST", "/text-to-3d", data)
        return result["result"]

    def create_refine_task(self, preview_task_id, texture_richness="high"):
        data = {
            "mode": "refine",
            "preview_task_id": preview_task_id,
            "texture_richness": texture_richness,
        }
        result = self._make_request("POST", "/text-to-3d", data)
        return result["result"]

    def get_task(self, task_id):
        result = self._make_request("GET", f"/text-to-3d/{task_id}")
        return TextTo3DTask.from_dict(result)
