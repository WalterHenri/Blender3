import pygame
from Interface import TextTo3DInterface
from PygameObj import ModelViewer


def display_3d_model(model_path):
    viewer = ModelViewer("resource/", model_path)
    viewer.run()


def main():
    interface = TextTo3DInterface()
    interface.initialize_pygame()

    clock = pygame.time.Clock()
    running = True

    while running:
        interface.handle_events()
        interface.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()


