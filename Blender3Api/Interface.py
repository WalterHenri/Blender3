import pygame
import sys
import requests
import threading
import math
import time
from pygame.locals import *
from ApiClient import MeshyAPI
from PygameObj import ModelViewer

import pygame
import sys
import requests
from pygame.locals import *
from ApiClient import MeshyAPI
from PygameObj import ModelViewer


class TextTo3DInterface:
    def __init__(self):
        self.progress = 0
        self.screen = None
        self.width, self.height = 800, 600
        self.prompt = ""
        self.art_styles = ["realistic", "sculpture"]
        self.selected_art_style = self.art_styles[0]
        self.negative_prompt = "low quality, low resolution, low poly, ugly"
        self.font = None
        self.input_box_width = 600
        self.input_box_height = 40
        self.create_button_width = 250
        self.create_button_height = 60
        self.active_input = None
        self.show_art_style_options = False
        input_x = (self.width - self.input_box_width) // 2
        input_y = 100
        self.prompt_box = pygame.Rect(input_x, input_y, self.input_box_width, self.input_box_height)
        self.negative_prompt_box = pygame.Rect(input_x, input_y + 70, self.input_box_width, self.input_box_height)
        self.art_style_box = pygame.Rect(input_x, input_y + 140, self.input_box_width, self.input_box_height)
        create_button_x = (self.width - self.create_button_width) // 2
        create_button_y = self.height - 150
        self.create_button = pygame.Rect(create_button_x, create_button_y, self.create_button_width,
                                         self.create_button_height)
        self.logo = None
        self.model_ready = False
        self.model_path = ""
        self.loading = False

    def initialize_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Text to 3D Interface')
        self.font = pygame.font.Font(None, 32)
        self.load_logo()

    def load_logo(self):
        try:
            self.logo = pygame.image.load('assets/logo.png').convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (100, 100))  # Ajuste o tamanho conforme necessário
        except FileNotFoundError:
            print("Logo file not found. Skipping logo display.")

    def draw_text(self, text, rect, color=(0, 0, 0)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (rect.x + 10, rect.y + 10))

    @staticmethod
    def draw_rounded_rect(surface, rect, color, radius=10):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_input_boxes(self):
        self.draw_rounded_rect(self.screen, self.prompt_box, (255, 255, 255), 10)
        self.draw_rounded_rect(self.screen, self.negative_prompt_box, (255, 255, 255), 10)
        self.draw_rounded_rect(self.screen, self.art_style_box, (255, 255, 255), 10)
        self.draw_rounded_rect(self.screen, self.create_button, (0, 0, 255), 10)

    def draw_combobox(self):
        if self.show_art_style_options:
            option_rects = []
            for i, style in enumerate(self.art_styles):
                rect = pygame.Rect(self.art_style_box.x, self.art_style_box.bottom + i * 50, self.art_style_box.width,
                                   50)
                self.draw_rounded_rect(self.screen, rect, (255, 255, 255), 10)
                self.draw_text(style, rect)
                option_rects.append(rect)

            return option_rects
        else:
            self.draw_text(self.selected_art_style, self.art_style_box)
            return []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if self.prompt_box.collidepoint(event.pos):
                    self.active_input = 'prompt'
                    self.show_art_style_options = False
                elif self.negative_prompt_box.collidepoint(event.pos):
                    self.active_input = 'negative_prompt'
                    self.show_art_style_options = False
                elif self.art_style_box.collidepoint(event.pos):
                    self.active_input = 'art_style'
                    self.show_art_style_options = not self.show_art_style_options
                elif self.create_button.collidepoint(event.pos):
                    self.model_ready = False
                    self.loading = True
                    threading.Thread(target=self.create_task).start()

                if self.show_art_style_options:
                    option_rects = self.draw_combobox()
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_art_style = self.art_styles[i]
                            self.show_art_style_options = False
                            break
            elif event.type == KEYDOWN:
                if self.active_input == 'prompt':
                    if event.key == K_RETURN:
                        self.active_input = None
                    elif event.key == K_BACKSPACE:
                        self.prompt = self.prompt[:-1]
                    else:
                        self.prompt += event.unicode
                elif self.active_input == 'negative_prompt':
                    if event.key == K_RETURN:
                        self.active_input = None
                    elif event.key == K_BACKSPACE:
                        self.negative_prompt = self.negative_prompt[:-1]
                    else:
                        self.negative_prompt += event.unicode
                elif self.active_input == 'art_style':
                    pass

    def handle_model_display(self):
        self.model_ready = False
        self.display_3d_model(self.model_path)

    def draw(self):
        self.screen.fill((30, 30, 30))

        input_x = (self.width - self.input_box_width) // 2
        input_y = 62

        self.draw_text("Prompt:", pygame.Rect(input_x, input_y, 100, 40))
        self.draw_text("Negative Prompt:", pygame.Rect(input_x, input_y + 70, 200, 40))
        self.draw_text("Art Style:", pygame.Rect(input_x, input_y + 140, 150, 40))
        self.draw_combobox()

        self.draw_input_boxes()
        self.draw_text("Create", self.create_button)

        # Mostrar que o input está selecionado
        if self.active_input == 'prompt':
            self.draw_rounded_rect(self.screen, self.prompt_box, (0, 255, 0), 10)
        elif self.active_input == 'negative_prompt':
            self.draw_rounded_rect(self.screen, self.negative_prompt_box, (0, 255, 0), 10)
        elif self.active_input == 'art_style':
            self.draw_rounded_rect(self.screen, self.art_style_box, (0, 255, 0), 10)

        self.draw_text(self.prompt, self.prompt_box)
        self.draw_text(self.negative_prompt, self.negative_prompt_box)
        self.draw_text(self.selected_art_style, self.art_style_box)

        # Desenhar o logo
        if self.logo:
            logo_rect = self.logo.get_rect(topleft=(self.width - 120, 20))
            self.screen.blit(self.logo, logo_rect)

    def loading_animation(self):
        clock = pygame.time.Clock()

        angle = 0
        radius = 50
        thickness = 2
        color = (255, 255, 255)  # Branco

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Limpar a tela
            self.screen.fill((30, 30, 30))

            # Calcular o centro do círculo
            center_x = self.width // 2
            center_y = self.height // 2

            # Desenhar o círculo girando
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius, thickness)

            # Atualizar o ângulo
            angle += 1
            if angle >= 360:
                angle = 0

            # Atualizar a posição do círculo
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))

            # Desenhar o ponto central
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)

            # Atualizar a tela
            pygame.display.flip()

            # Controlar a taxa de quadros
            clock.tick(60)

    def create_task(self):
        try:
            meshy_api = MeshyAPI("msy_15LD1QdOqkN5fClmDDnPA7ozbcyWxfKKaAhI")

            preview_task_id = meshy_api.create_preview_task(
                prompt=self.prompt,
                art_style=self.selected_art_style,
                negative_prompt=self.negative_prompt
            )

            progress = MeshyAPI.wait_for_task_completion(meshy_api, preview_task_id)
            if progress[1]:
                refined_task_id = meshy_api.create_refine_task(preview_task_id)
                refined_progress = MeshyAPI.wait_for_task_completion(meshy_api, refined_task_id)
                if refined_progress[1]:
                    self.model_path = MeshyAPI.fetch_model(meshy_api, refined_task_id)
                    self.loading = False
                    self.model_ready = True
                else:
                    self.progress = 50 + progress[0] / 2
                    print("Tarefa de refinamento não concluída")
            else:
                self.progress = progress[0] / 2
                print("Tarefa de preview não concluída")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the API request: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    @staticmethod
    def display_3d_model(model_path):
        viewer = ModelViewer("resource/", model_path)
        viewer.run()
