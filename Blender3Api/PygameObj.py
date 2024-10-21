import os
import sys
from chj.ogl import *
from chj.ogl.objloader import CHJ_tiny_obj, OBJ
from chj.ogl import light
import pickle


class Param(object):
    def __init__(self):
        self.obj = None
        self.sel_pos = False


class ModelViewer:
    def __init__(self, resource_dir="", model_path="", pkl_file=""):
        self.resource_dir = resource_dir
        self.model_file = model_path
        self.pkl_file = pkl_file
        self.param = Param()
        self.clock = None
        self.viewport = (800, 800)
        self.screen = None
        self.obj = None
        self.cam = None
        self.running = False
        self.voltar_width = 250
        self.voltar_height = 60
        self.voltar_x = 50
        self.voltar_y = 50
        self.voltar_button = pygame.Rect(self.voltar_x, self.voltar_y, self.voltar_width, self.voltar_height)

    def _load_model(self):
        self.obj = OBJ(self.resource_dir, self.model_file, swapyz=False)
        self.obj.create_bbox()
        if self.pkl_file != "":
            with open(os.path.join(self.resource_dir, self.pkl_file), 'wb') as f:
                pickle.dump(self.obj, f)

    def _setup_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.viewport, OPENGL | DOUBLEBUF)
        self.clock = pygame.time.Clock()

    def _setup_opengl(self):
        light.setup_lighting()
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 1000, 0))
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        self.obj.create_gl_list()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1, 0.1, 10000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 800, 0, 0, 0, 0, 1, 0)

    def _main_loop(self):
        rx, ry = (0, 0)
        tx, ty = (0, 0)
        zpos = 5
        rotate = move = False

        while self.running:
            self.clock.tick(30)
            for e in pygame.event.get():
                if e.type == QUIT:
                    sys.exit()
                elif e.type == KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif e.key == pygame.K_4:
                        self.param.sel_pos = not self.param.sel_pos

                elif e.type == MOUSEBUTTONDOWN:
                    if self.voltar_button.collidepoint(e.pos):
                        self.running = False
                    pressed_array = pygame.mouse.get_pressed()
                    if pressed_array[0]:
                        if self.param.sel_pos:
                            pos = pygame.mouse.get_pos()
                            self.pos_get_pos3d_show(pos)

                    if e.button == 4:
                        zpos = max(1, zpos - 1)
                    elif e.button == 5:
                        zpos += 1
                    elif e.button == 1:
                        rotate = True
                    elif e.button == 3:
                        move = True
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

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glLoadIdentity()

            glTranslate(tx / 20., ty / 20., -zpos)
            glRotate(ry / 5, 1, 0, 0)
            glRotate(rx / 5, 0, 1, 0)

            s = [2 / self.obj.bbox_half_r] * 3
            glScale(*s)

            t = -self.obj.bbox_center
            glTranslate(*t)

            glCallList(self.obj.gl_list)
            if hasattr(self.param, 'pos3d') and self.param.sel_pos:
                self.draw_pos(self.param.pos3d)

            pygame.draw.rect(self.screen, (0, 150, 255), self.voltar_button, border_radius=10)
            font = pygame.font.Font(None, 36)
            text = font.render("Voltar", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.voltar_button.center)
            self.screen.blit(text, text_rect)

            pygame.display.flip()

    def pos_get_pos3d(self, pos):
        x = pos[0]
        y = self.viewport[1] - pos[1]
        z = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        xyz = gluUnProject(x, y, z, modelview, projection, viewport)
        return xyz

    def pos_get_pos3d_show(self, pos):
        pos3d = self.pos_get_pos3d(pos)
        self.param.pos3d = pos3d

    def draw_pos(self, pos3d, size=10, color=[0, 1, 0]):
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor3f(*color)
        glVertex3f(*pos3d)
        glEnd()
        glColor3f(1, 1, 1)

    def run(self):
        os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])
        self._load_model()
        self._setup_pygame()
        self._setup_opengl()
        self.running = True
        self._main_loop()
