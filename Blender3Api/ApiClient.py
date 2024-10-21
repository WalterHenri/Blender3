import os
import time

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

    @staticmethod
    def fetch_model(meshy_api, refine_task_id):
        # Baixar o modelo 3D refinado
        try:
            # Obter a tarefa refinada
            task = meshy_api.get_task(refine_task_id)

            # Acessar a URL do modelo 3D
            model_urls = task.model_urls
            model_url = model_urls.get("obj")
            mtl_url = model_urls.get("mtl")
            texture_img = task.texture_urls[0]

            if model_url is None:
                print("Model URL not found.")
                return None

            # Fazer o download do modelo
            response = requests.get(model_url)
            response.raise_for_status()

            # Fazer o download do mtl
            response_mtl = requests.get(mtl_url)
            response_mtl.raise_for_status()

            # Fazer o donwload da textura
            response_texture = requests.get(texture_img.base_color)
            response_texture.raise_for_status()

            # Ensure the resource directory exists
            resource_dir = "resource"
            os.makedirs(resource_dir, exist_ok=True)

            model_file_name = "model.obj"
            # Save the file in the resource directory
            model_file = os.path.join(resource_dir, model_file_name)
            with open(model_file, 'wb') as file:
                file.write(response.content)

            # Save the mtl file in the resource directory
            mtl_file = os.path.join(resource_dir, "model.mtl")
            with open(mtl_file, 'wb') as file:
                file.write(response_mtl.content)

            # Save the texture file in the resource directory
            texture_file = os.path.join(resource_dir, "Image_0.jpg")
            with open(texture_file, 'wb') as file:
                file.write(response_texture.content)

            return model_file_name
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the model: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    @staticmethod
    def wait_for_task_completion(meshy_api, task_id, timeout=300, check_interval=5):
        """
        Aguarda a conclusão de uma tarefa.

        Args:
            meshy_api: Instância da API Meshy.
            task_id: ID da tarefa a ser verificada.
            timeout: Tempo máximo de espera em segundos (padrão: 300 segundos).
            check_interval: Intervalo de verificação em segundos (padrão: 5 segundos).

        Returns:
            Retorna True se a tarefa foi concluída, False caso contrário.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            task_info = meshy_api.get_task(task_id)
            status = task_info.status

            if status == "SUCCEEDED":
                print(f"Task {task_id} completed successfully.")
                return True
            elif status == "FAILED":
                print(f"Task {task_id} failed.")
                return False

            # Aguardando antes de verificar novamente
            time.sleep(check_interval)
            print(f"Waiting for task {task_id} to complete. Current status: {status}")

        print(f"Task {task_id} did not complete within the timeout period.")
        return False

