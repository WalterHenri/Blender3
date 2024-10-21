import pygame
from Interface import TextTo3DInterface
from PygameObj import ModelViewer


def main():
    interface = TextTo3DInterface()
    interface.initialize_pygame()

    clock = pygame.time.Clock()
    running = True

    while running:
        interface.handle_events()
        if interface.model_ready:
            interface.handle_model_display()
        elif interface.IsLoading:
            interface.loading_animation()
        else:
            interface.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()


