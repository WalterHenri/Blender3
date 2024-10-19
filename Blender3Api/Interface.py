import pygame
import sys

import requests
from pygame.locals import *

from ApiClient import MeshyAPI
from PygameObj import ModelViewer


class TextTo3DInterface:
    def __init__(self):
        self.screen = None
        self.width, self.height = 800, 600
        self.prompt = ""
        self.art_style = "realistic"
        self.negative_prompt = "low quality, low resolution, low poly, ugly"
        self.font = None
        self.input_box = pygame.Rect(50, 50, 700, 40)
        self.art_style_box = pygame.Rect(50, 120, 200, 40)
        self.negative_prompt_box = pygame.Rect(50, 190, 700, 40)
        self.create_button = pygame.Rect(550, 250, 100, 50)
        self.active_input = None
        self.progress_bar_width = 300
        self.progress_bar_height = 20
        self.progress_bar_x = (self.width - self.progress_bar_width) // 2
        self.progress_bar_y = self.height - self.progress_bar_height - 10
        self.progress = 0

    def initialize_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Text to 3D Interface')
        self.font = pygame.font.Font(None, 32)

    def draw_text(self, text, rect, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (rect.x + 5, rect.y + 5))

    def draw_input_boxes(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.art_style_box, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.negative_prompt_box, 2)
        pygame.draw.rect(self.screen, (0, 0, 255), self.create_button)

    def draw_progress_bar(self):
        pygame.draw.rect(self.screen, (128, 128, 128), (self.progress_bar_x, self.progress_bar_y, self.progress_bar_width, self.progress_bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (self.progress_bar_x, self.progress_bar_y, int(self.progress * self.progress_bar_width), self.progress_bar_height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if self.input_box.collidepoint(event.pos):
                    self.active_input = 'prompt'
                elif self.art_style_box.collidepoint(event.pos):
                    self.active_input = 'art_style'
                elif self.negative_prompt_box.collidepoint(event.pos):
                    self.active_input = 'negative_prompt'
                elif self.create_button.collidepoint(event.pos):
                    self.create_task()
            elif event.type == KEYDOWN:
                if self.active_input == 'prompt':
                    if event.key == K_RETURN:
                        self.active_input = None
                    elif event.key == K_BACKSPACE:
                        self.prompt = self.prompt[:-1]
                    else:
                        self.prompt += event.unicode
                elif self.active_input == 'art_style':
                    if event.key == K_RETURN:
                        self.active_input = None
                    elif event.key == K_BACKSPACE:
                        self.art_style = self.art_style[:-1]
                    else:
                        self.art_style += event.unicode
                elif self.active_input == 'negative_prompt':
                    if event.key == K_RETURN:
                        self.active_input = None
                    elif event.key == K_BACKSPACE:
                        self.negative_prompt = self.negative_prompt[:-1]
                    else:
                        self.negative_prompt += event.unicode

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.draw_text("Prompt:", pygame.Rect(50, 20, 100, 40))
        self.draw_text(self.prompt, self.input_box)
        self.draw_text("Art Style:", pygame.Rect(50, 90, 150, 40))
        self.draw_text(self.art_style, self.art_style_box)
        self.draw_text("Negative Prompt:", pygame.Rect(50, 160, 200, 40))
        self.draw_text(self.negative_prompt, self.negative_prompt_box)
        self.draw_text("Create", self.create_button)
        self.draw_input_boxes()
        self.draw_progress_bar()

    def create_task(self):
        try:
            meshy_api = MeshyAPI("msy_OId2it2tFV9QEMYG3mP4vu5nTgjrvjSIaMS7")

            # Criar uma tarefa de preview
            preview_task_id = meshy_api.create_preview_task(
                prompt=self.prompt,
                art_style=self.art_style,
                negative_prompt=self.negative_prompt
            )

            # Aguardar a conclusão da tarefa de preview
            if MeshyAPI.wait_for_task_completion(meshy_api, preview_task_id):
                # Criar uma tarefa de refinamento
                refined_task_id = meshy_api.create_refine_task(preview_task_id)

                # Aguardar a conclusão da tarefa de refinamento
                if MeshyAPI.wait_for_task_completion(meshy_api, refined_task_id):
                    model_path = MeshyAPI.fetch_model(meshy_api, refined_task_id)
                    self.display_3d_model(model_path)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the API request: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    @staticmethod
    def display_3d_model(model_path):
        viewer = ModelViewer("resource/", model_path)
        viewer.run()

