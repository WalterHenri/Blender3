import pickle
import sys
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Aqui você precisa importar seu módulo de luz e carregador de OBJ
import light
from objLoader import CHJ_tiny_obj

# Caminho do arquivo OBJ

fobj_pkl = "obj.pkl"


class Param:
    pass


def run(path_file):
    fobj = path_file
    #caminho do arquivo obj
    run_ogl(fobj)


def run_ogl(fobj):
    # Carrega o objeto OBJ
    obj = CHJ_tiny_obj("", fobj, swapyz=False)
    obj.create_bbox()

    # Salva o objeto usando pickle
    with open(fobj_pkl, 'wb') as f:
        pickle.dump(obj, f)

    # Inicializa parâmetros
    Param.obj = obj
    Param.sel_pos = False

    # Inicializa Pygame e OpenGL
    pygame.init()
    viewport = (800, 800)
    Param.viewport = viewport
    screen = pygame.display.set_mode(viewport, DOUBLEBUF | OPENGL)

    # Configuração de luz
    light.setup_lighting()
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 1000, 0))
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    obj.create_gl_list()

    clock = pygame.time.Clock()

    # Configura a perspectiva
    gluPerspective(60, 1, 0.1, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 800, 0, 0, 0, 0, 1, 0)

    rx, ry = (0, 0)
    tx, ty = (0, 0)
    zpos = 5
    rotate = move = False

    while True:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:  # Left mouse button
                    rotate = True
                elif e.button == 3:  # Right mouse button
                    move = True
                elif e.button == 4:  # Scroll up
                    zpos = max(1, zpos - 1)
                elif e.button == 5:  # Scroll down
                    zpos += 1
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    rotate = False
                elif e.button == 3:
                    move = False
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                if rotate:
                    rx -= i
                    ry -= j
                if move:
                    tx += i
                    ty -= j

        # Limpa a tela
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Transforma e renderiza o objeto
        glTranslate(tx / 20., ty / 20., -zpos)
        glRotate(ry / 5, 1, 0, 0)
        glRotate(rx / 5, 0, 1, 0)

        s = [2 / obj.bbox_half_r] * 3
        glScale(*s)

        t = -obj.bbox_center
        glTranslate(*t)

        glCallList(obj.gl_list)
        pygame.display.flip()

