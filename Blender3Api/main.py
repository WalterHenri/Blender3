import os
import tempfile
import numpy as np
import requests
import time
from ApiClient import MeshyAPI
import pygame
from OpenGL.GL import *
from PygameObj import ModelViewer


def fetch_model(meshy_api, refine_task_id):
    # Baixar o modelo 3D refinado
    try:
        # Obter a tarefa refinada
        task = meshy_api.get_task(refine_task_id)

        # Acessar a URL do modelo 3D
        model_urls = task.model_urls
        # Se precisar de um modelo específico, como GLB, FBX, etc.
        model_url = model_urls.get("obj")  # Substitua "glb" por "fbx", "obj", etc., conforme necessário

        if model_url is None:
            print("Model URL not found.")
            return None

        # Fazer o download do modelo
        response = requests.get(model_url)
        response.raise_for_status()

        # Ensure the resource directory exists
        resource_dir = "resource"
        os.makedirs(resource_dir, exist_ok=True)

        # Save the file in the resource directory
        model_file = os.path.join(resource_dir, "model.obj")
        with open(model_file, 'wb') as file:
            file.write(response.content)

        return model_file
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the model: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def display_3d_model(model_path):
    viewer = ModelViewer(model_path)
    viewer.run()


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


# Exemplo de uso
try:
    meshy_api = MeshyAPI("msy_OId2it2tFV9QEMYG3mP4vu5nTgjrvjSIaMS7")

    # Criar uma tarefa de preview
    preview_task_id = meshy_api.create_preview_task(
        prompt="a monster mask",
        art_style="realistic",
        negative_prompt="low quality, low resolution, low poly, ugly"
    )

    refined_task_id = '01929d49-5a44-7d76-b865-420e5f5ec0c8'
    model_path = fetch_model(meshy_api, refined_task_id)
    display_3d_model(model_path)

except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the API request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")