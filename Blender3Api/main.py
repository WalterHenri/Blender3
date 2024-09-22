import requests

from ApiClient import MeshyAPI

try:
    meshy_api = MeshyAPI("msy_OId2it2tFV9QEMYG3mP4vu5nTgjrvjSIaMS7")

    # Create a preview task
    preview_task_id = meshy_api.create_preview_task(
        prompt="a monster mask",
        art_style="realistic",
        negative_prompt="low quality, low resolution, low poly, ugly"
    )

    print(f"Preview task created: {preview_task_id}")

    # Create a refine task
    refine_task_id = meshy_api.create_refine_task(preview_task_id, texture_richness="medium")
    print(f"Refine task created: {refine_task_id}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the API request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
