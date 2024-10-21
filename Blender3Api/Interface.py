import math
import threading

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
        self.IsLoading = False
        self.angle = 0

    def handle_model_display(self):
        self.model_ready = False
        self.display_3d_model(self.model_path)

    def loading_animation(self):
        radius = 50
        thickness = 2
        color = (255, 255, 255)  # Branco
        # Calcular o centro do círculo
        center_x = self.width // 2
        center_y = self.height // 2
        # Desenhar o círculo girando
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius, thickness)
        # Atualizar o ângulo
        self.angle += 1
        if self.angle >= 360:
            self.angle = 0

        # Atualizar a posição do círculo
        x = center_x + radius * math.cos(math.radians(self.angle))
        y = center_y + radius * math.sin(math.radians(self.angle))

        # Desenhar o ponto central
        pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)

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

    @staticmethod
    def draw_gradient_rect(surface, rect, color1, color2):
        for i in range(rect.height):
            color = (
                color1[0] + (color2[0] - color1[0]) * i / rect.height,
                color1[1] + (color2[1] - color1[1]) * i / rect.height,
                color1[2] + (color2[2] - color1[2]) * i / rect.height,
            )
            pygame.draw.line(surface, color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))

    def draw_input_boxes(self):
        # Alterar o gradiente para tons mais suaves de cinza claro
        self.draw_gradient_rect(self.screen, self.prompt_box, (250, 250, 250), (230, 230, 230))
        self.draw_gradient_rect(self.screen, self.negative_prompt_box, (250, 250, 250), (230, 230, 230))
        self.draw_gradient_rect(self.screen, self.art_style_box, (250, 250, 250), (230, 230, 230))

        # Botão com sombra e efeito hover
        if self.create_button.collidepoint(pygame.mouse.get_pos()):
            self.draw_rounded_rect(self.screen, self.create_button, (0, 150, 255), 10)  # Mudança de cor no hover
        else:
            self.draw_rounded_rect(self.screen, self.create_button, (0, 120, 255), 10)

    def draw_combobox(self):
        if self.show_art_style_options:
            option_rects = []
            for i, style in enumerate(self.art_styles):
                rect = pygame.Rect(self.art_style_box.x, self.art_style_box.bottom + i * 50, self.art_style_box.width,
                                   50)
                self.draw_gradient_rect(self.screen, rect, (240, 240, 240), (200, 200, 200))
                self.draw_text(style, rect)
                option_rects.append(rect)

            return option_rects
        else:
            self.draw_text(self.selected_art_style, self.art_style_box)
            return []

    def draw_title(self):
        title_text = self.font.render("Texto para 3D", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.width // 2, 50))

        # Desenhar uma sombra
        shadow_text = self.font.render("Texto para 3D", True, (150, 150, 150))
        self.screen.blit(shadow_text, (title_rect.x + 2, title_rect.y + 2))  # Sombra um pouco deslocada
        self.screen.blit(title_text, title_rect)  # Desenhar o título

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
                    self.IsLoading = True
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

    def draw_background_gradient(self):
        for i in range(self.height):
            color = (255 - i // 3, 255 - i // 3, 255)  # Gradiente de fundo
            pygame.draw.line(self.screen, color, (0, i), (self.width, i))

    def draw_response_box(self):
        response_box_rect = pygame.Rect(50, 60, self.width - 80, 260)  # Ajustada para subir um pouco

        # Criar um gradiente azul do fundo para a caixa de resposta
        for i in range(response_box_rect.height):
            color = (0, 255 - (i * 200 // response_box_rect.height), 255)  # Gradiente azul para a caixa
            pygame.draw.line(self.screen, color, (response_box_rect.x, response_box_rect.y + i),
                             (response_box_rect.x + response_box_rect.width, response_box_rect.y + i))

        # Criar um gradiente para a borda igual ao fundo
        border_thickness = 3  # Espessura da borda ajustada
        for i in range(border_thickness):  # Ajuste a largura da borda
            border_rect = response_box_rect.inflate(i * 2, i * 2)  # Aumentar o tamanho do retângulo da borda
            border_color = (0, 255 - (i * 200 // border_thickness), 255)  # Gradiente da borda igual ao fundo
            pygame.draw.rect(self.screen, border_color, border_rect, border_radius=15)

        # Cor da borda mais interna (opcional)
        inner_border_color = (0, 0, 0)  # Preto para a borda interna
        pygame.draw.rect(self.screen, inner_border_color, response_box_rect, 2,
                         border_radius=15)  # Borda interna mais fina

    def draw(self):
        self.draw_background_gradient()
        self.draw_title()
        self.draw_response_box()

        input_x = (self.width - self.input_box_width) // 3
        input_y = 62

        self.draw_text("Descreva o que deseja:", pygame.Rect(input_x, input_y, 100, 40))
        self.draw_text("Condições:", pygame.Rect(input_x, input_y + 70, 200, 40))
        self.draw_text("Estilo Artístico:", pygame.Rect(input_x, input_y + 140, 150, 40))
        self.draw_combobox()
        self.draw_combobox()
        self.draw_input_boxes()
        self.draw_button(self.create_button, "Criar", (255, 255, 255))

        # Destacar o campo ativo com uma borda cinza clara
        if self.active_input == 'prompt':
            self.draw_rounded_rect(self.screen, self.prompt_box, (200, 200, 200), 10)
        elif self.active_input == 'negative_prompt':
            self.draw_rounded_rect(self.screen, self.negative_prompt_box, (200, 200, 200), 10)
        elif self.active_input == 'art_style':
            self.draw_rounded_rect(self.screen, self.art_style_box, (200, 200, 200), 10)

        # Desenhar o texto digitado nas caixas de entrada
        self.draw_text(self.prompt, self.prompt_box)
        self.draw_text(self.negative_prompt, self.negative_prompt_box)
        self.draw_text(self.selected_art_style, self.art_style_box)

        # Desenhar o logo no canto superior direito
        if self.logo:
            logo_rect = self.logo.get_rect(topleft=(self.width - 100, 10))
            self.screen.blit(self.logo, logo_rect)

    def draw_button(self, button_rect, text, text_color):
        # Mudar cor do botão ao passar o mouse (hover)
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (0, 120, 255), button_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (0, 0, 255), button_rect, border_radius=10)

        # Desenhar o texto do botão
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def create_task(self):
        try:
            # Criar a tarefa de preview via API Meshy
            meshy_api = MeshyAPI("msy_JMa5zO0qgX0DlWttd8ZjtzA1o5jwhs0DURBY")
            preview_task_id = meshy_api.create_preview_task(
                prompt=self.prompt,
                art_style=self.selected_art_style,
                negative_prompt=self.negative_prompt
            )

            # Aguardar a conclusão da tarefa de preview
            if MeshyAPI.wait_for_task_completion(meshy_api, preview_task_id):
                # Criar a tarefa de refinamento
                refined_task_id = meshy_api.create_refine_task(preview_task_id)

                # Aguardar a conclusão da tarefa de refinamento
                if MeshyAPI.wait_for_task_completion(meshy_api, refined_task_id):
                    model_path = MeshyAPI.fetch_model(meshy_api, refined_task_id)
                    self.IsLoading = False
                    self.model_ready = True
                    self.model_path = model_path

        except requests.exceptions.RequestException as e:
            print(f"Ocorreu um erro ao fazer a requisição à API: {e}")
            self.IsLoading = False  # Desativar animação em caso de erro
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {str(e)}")
            self.IsLoading = False  # Desativar animação em caso de erro

    @staticmethod
    def display_3d_model(model_path):
        viewer = ModelViewer("resource/", model_path)
        viewer.run()
