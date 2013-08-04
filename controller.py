"""
controller.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Helicopter-Simulation erstellt im Rahmen des Moduls
Generative Computergrafik an der Hochschule RheinMain
in Wiesbaden im Sommersemester 2013.

Das Programm erlaubt es, einen Helicopter durch eine
Welt bestehend aus einer Skybox und beliebig vielen
Helicopter-Pads zu bewegen.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.shaders import *
from mathematic import geometry as g
from mathematic import Vector
from object import Skybox, Helicopter,\
FreeCamera, HeliCamera, HeliPad, ActionCamera, Space
from util import ObjLoader

import numpy as np
import Image
import time
import sys
import math


GAMESIZE = 200
HELIPADPOS = GAMESIZE * 0.95
WIDTH, HEIGHT = 800, 600
SHADER_LOCATION = 'shader'
TEXTURE_LOCATION = 'textures'
NEARPLANE, FARPLANE = 0.1, GAMESIZE * 3

doRotation, doZoom = False, False
fixedPoint = 0
translate = 0
shaderList = ['heli', 'image']
shader = {}

skybox = None
helicopter = None
helipad = None
helipad2 = None
space = None

keystates = {'w': False, 's': False, 'a': False, 'd': False,
             'i': False, 'k': False, 'l': False, 'j': False}

# Initialize Cameras
camList = [FreeCamera((0, -1, -5), (0, -0.1, 0), (0, 1, 0)),
           HeliCamera(5, 1),  # back top cam
           HeliCamera(5, 0),  # back cam
           HeliCamera(-0.1, 0.6),  # rotor cam
           ActionCamera((0, 0, 0)),
           ActionCamera((-GAMESIZE * 0.1, GAMESIZE * 0.1, GAMESIZE * 0.1)),
           ActionCamera((-GAMESIZE * 0.04, 0, GAMESIZE * 0.04)),
           ActionCamera((1, GAMESIZE * 0.4, 1))]

actCam = 2  # counter for actual camera

perspectiveMatrix =\
g.perspectiveMatrix(45, WIDTH / HEIGHT, NEARPLANE, FARPLANE)

HELI_OBJ_FILE = 'heli_data/HELICOPTER500D.obj'

axis = [1, 0, 0]
actOri = g.identity()
angle = 0
moveP = (0.1, 0.1, 0.1)


def init():
    """ erstellt Spielobjekte und setzt OpenGL Zustaende """
    global skybox, helicopter, helipad, space, helipad2
    initShader()
    ### create objects for simulation
    skybox = Skybox(shader['image'], TEXTURE_LOCATION, GAMESIZE)
    helicopter = Helicopter(shader['heli'], ObjLoader(GAMESIZE),
                           Vector(-40, HELIPADPOS - GAMESIZE, -40),
                           HELI_OBJ_FILE)

    helipad = HeliPad(shader['image'], 2, GAMESIZE, HELIPADPOS, 10, -40, -40)
    helipad2 = HeliPad(shader['image'], 2, GAMESIZE, HELIPADPOS, 10, 40, 40)
    space = Space(helicopter, GAMESIZE, -1.)
    space.addObject(helipad)
    space.addObject(helipad2)
    glEnable(GL_DEPTH_TEST)

    # glass transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def reshape(width, height):
    """ passt Inhalt der Szene an Viewport an """
    global WIDTH, HEIGHT, perspectiveMatrix
    WIDTH, HEIGHT = width, height
    if height == 0:
        height = 1
    aspect = float(width) / height
    glViewport(0, 0, width, height)
    perspectiveMatrix = g.perspectiveMatrix(45, aspect, NEARPLANE, FARPLANE)


def display():
    """ Methode zum Zeichnen der Szene """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    mvMat = None
    space.step()  # Step the simulation one step forward
    camera = camList[actCam]

    if isinstance(camera, HeliCamera):
        mvMat = camera.getMvMat(helicopter.position, helicopter.actOri)

    elif isinstance(camera, FreeCamera):
        mvMat = camera.getMvMat()

    elif isinstance(camera, ActionCamera):
        mvMat = camera.getMvMat(space.getPosition())

    pMat = perspectiveMatrix
    skybox.drawSkybox(pMat, mvMat)

    keyOperations()

    helicopter.drawHelicopter(pMat, mvMat)
    helipad.drawHeliPad(pMat, mvMat)
    helipad2.drawHeliPad(pMat, mvMat)

    glutSwapBuffers()


def keyOperations():
    """
    Keybuffer Operationen, erlaubt es, mehrere Tasten
    auf einmal zu betaetigen
    """
    if keystates['w']:  # pitch, auftrieb vergroessern
        space.pitch(-1)

    if keystates['s']:  # pitch, auftrieb verkleinern
        space.pitch(1)

    if keystates['a']:  # nase dreht sich nach links
        space.gier(0.5)

    if keystates['d']:  # nase dreht sich nach rechts
        space.gier(-0.5)

    if keystates['j']:  # aileron, neigt sich nach links
        space.aileron(-0.3)

    if keystates['l']:  # ailteron, neigt sich nach rechts
        space.aileron(0.3)

    if keystates['i']:  # elevator, neigt sich nach vorne
        space.elevator(0.3)

    if keystates['k']:  # elevator, neigt sich nach hinten
        space.elevator(-0.3)


def keyPressed(key, x, y):
    """ wertet Tastaturanschlaege aus """
    global actCam, camList

    if key == chr(27):
        sys.exit(1)

    elif key == '+':  # next texture
        skybox.nextTexture()

    elif key == '-':
        skybox.preTexture()

    elif key in '1':
        actCam = (actCam + 1) % len(camList)
        while not isinstance(camList[int(actCam)], FreeCamera):
            actCam = (actCam + 1) % len(camList)

    elif key in '2':
        actCam = (actCam + 1) % len(camList)
        while not isinstance(camList[int(actCam)], HeliCamera):
            actCam = (actCam + 1) % len(camList)

    elif key in '3':
        actCam = (actCam + 1) % len(camList)
        while not isinstance(camList[int(actCam)], ActionCamera):
            actCam = (actCam + 1) % len(camList)

    elif key == 'r':
        space.reset()

    elif key == 'o':
        space.startHeli()

    elif key in keystates:
        keystates[key] = True

    glutPostRedisplay()


def keyReleased(key, x, y):
    """ setzt Status von key im Keybuffer auf False """
    keystates[key] = False
    glutPostRedisplay()


def mousebuttonpressed(button, state, x, y):
    """ Callback Funktion fuer Maustasten """
    global startP, actOri, angle, doRotation, fixedPoint, doZoom

    if isinstance(camList[actCam], FreeCamera):
        r = min(WIDTH, HEIGHT) / 2.0
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                doRotation = True
                startP = g.projectOnSphere(x, y, r, WIDTH, HEIGHT)
            if state == GLUT_UP:
                doRotation = False
                camList[actCam].changeOrientation(angle, axis)
                angle = 0

        if button == GLUT_RIGHT_BUTTON:  # zoom
            if state == GLUT_DOWN:
                doZoom = True
                fixedPoint = y
            if state == GLUT_UP:
                doZoom = False


def mousemoved(x, y):
    """
    Callback Funktion fuer Mausbewegung.
    Erlaubt Zoom und ArcBall Rotation
    """
    global angle, axis, startPoint, moveP, fixedPoint, translate

    if isinstance(camList[actCam], FreeCamera):
        if doRotation:
            r = min(WIDTH, HEIGHT) / 2.0
            moveP = g.projectOnSphere(x, y, r, WIDTH, HEIGHT)
            angle = math.acos(np.dot(startP, moveP))
            axis = np.cross(startP, moveP)
            axis = (axis[0], -axis[1], axis[2])
            camList[actCam].rotate(angle, axis)
            glutPostRedisplay()

        if doZoom:
            translate += (fixedPoint - y) / 1000.
            if translate < 0.1:
                translate = 0.1
            if translate > 2:
                translate = 2
            camList[actCam].zoom(translate)
            glutPostRedisplay()
            fixedPoint = y


def initShader():
    """ initialisiert die angegebenen Shader """
    global shader

    if not glUseProgram:
        print "Missing Shader Objects!"
        sys.exit(1)

    for prog in shaderList:
        v = open(os.path.join(SHADER_LOCATION, prog + ".vert"), 'r').read()
        f = open(os.path.join(SHADER_LOCATION, prog + ".frag"), 'r').read()
        shader[prog] = compileProgram(compileShader(v, GL_VERTEX_SHADER),
                                      compileShader(f, GL_FRAGMENT_SHADER))


def animateHelicopter(x):
    """ Animation von OpenGL """
    glutPostRedisplay()
    glutTimerFunc(1, animateHelicopter, 1)


def main():
    """
    Main-Methode. Initialisiert OpenGL mit allen
    zugehoerigen Callback-Funktionen
    """
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow("Helicockter Simulation")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyPressed)
    glutKeyboardUpFunc(keyReleased)
    glutReshapeFunc(reshape)
    glutMouseFunc(mousebuttonpressed)
    glutMotionFunc(mousemoved)
    glutTimerFunc(1, animateHelicopter, 1)
    init()
    glutMainLoop()

if __name__ == '__main__':
    print """
    Helicockter Simulation
    -------------------------------------------------
    Benutzungsanleitung:
    w,s:        pitch, Auftrieb aendern
    a,d:        gier, nach links oder rechts schauen
    i,k:        nick, nach unten oder oben neigen
    j,l:        roll, nach links oder rechts nicken
    1:          Freecameras durchschalten
    2:          Helicameras durchschalten
    3:          Actioncameras durchschalten
    r:          Helicopter zuruecksetzen
    +,-:        Skyboxen durchwechseln
    -------------------------------------------------
    linke Maustaste: Arcball-Rotation
    rechte Maustaste: Zoomen
    """
    main()
