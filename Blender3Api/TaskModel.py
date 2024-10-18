import datetime


class TextureUrl:
    def __init__(self, base_color):
        self.base_color = base_color


class TaskError:
    def __init__(self, message=""):
        self.message = message


class TextTo3DTask:
    def __init__(
            self,
            id,
            model_urls=None,
            prompt="",
            art_style="",
            negative_prompt="",
            progress=0,
            started_at=0,
            created_at=0,
            finished_at=0,
            status="PENDING",
            task_error=None,
            texture_urls=None,
            thumbnail_url="",
            video_url="",
            preceding_tasks=0
    ):
        self.id = id
        self.model_urls = model_urls if model_urls else {}
        self.prompt = prompt
        self.art_style = art_style
        self.negative_prompt = negative_prompt
        self.progress = progress
        self.started_at = started_at
        self.created_at = created_at
        self.finished_at = finished_at
        self.status = status
        self.task_error = task_error if task_error else TaskError()
        self.texture_urls = texture_urls if texture_urls else []
        self.thumbnail_url = thumbnail_url
        self.video_url = video_url
        self.preceding_tasks = preceding_tasks

    def to_dict(self):
        return {
            "id": self.id,
            "model_urls": self.model_urls,
            "prompt": self.prompt,
            "art_style": self.art_style,
            "negative_prompt": self.negative_prompt,
            "progress": self.progress,
            "started_at": self.started_at,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "task_error": {"message": self.task_error.message},
            "texture_urls": [{"base_color": url.base_color} for url in self.texture_urls],
            "thumbnail_url": self.thumbnail_url,
            "video_url": self.video_url,
            "preceding_tasks": self.preceding_tasks,
        }

    @classmethod
    def from_dict(cls, data):
        # Garantindo que task_error seja um TaskError válido
        task_error_data = data.get("task_error")
        if task_error_data and isinstance(task_error_data, dict):
            task_error = TaskError(task_error_data.get("message", ""))
        else:
            task_error = TaskError()  # Cria um TaskError vazio se não houver dados

        # Garantindo que texture_urls seja sempre uma lista
        texture_urls_data = data.get("texture_urls")
        if texture_urls_data is None:
            texture_urls = []  # Se for None, inicializa como lista vazia
        elif isinstance(texture_urls_data, list):
            texture_urls = [TextureUrl(url.get("base_color", "")) for url in texture_urls_data]
        else:
            texture_urls = []  # Se não for uma lista, inicializa como lista vazia

        return cls(
            id=data.get("id", ""),  # Usando string vazia como padrão se 'id' não estiver presente
            model_urls=data.get("model_urls", {}),
            prompt=data.get("prompt", ""),
            art_style=data.get("art_style", ""),
            negative_prompt=data.get("negative_prompt", ""),
            progress=data.get("progress", 0),
            started_at=data.get("started_at", 0),
            created_at=data.get("created_at", 0),
            finished_at=data.get("finished_at", 0),  # Pode ser 0 ou None, dependendo do uso
            status=data.get("status", "PENDING"),
            task_error=task_error,
            texture_urls=texture_urls,
            thumbnail_url=data.get("thumbnail_url", ""),
            video_url=data.get("video_url", ""),
            preceding_tasks=data.get("preceding_tasks", 0),
        )
