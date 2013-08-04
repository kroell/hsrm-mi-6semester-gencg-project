'''
geometry.py
@author: Justin Albert

Dieses PythonSkript bildet die Mathematik-api.
Sie beinhaltet alle wichtigen Matrizenfunktionen
'''

import numpy as np
from OpenGL.GL import *
import math


def identity():
    """
    erstelle eine Einheitsmatrix
    """
    return np.matrix([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])


def lookAtMatrix(ex, ey, ez, cx, cy, cz, ux, uy, uz):
    """
    erstelle eine Lookat-Modelview Matrix fuer die Kamera
    @param e: standpunkt der Kamera
    @param c: blickpunkt der Kamera
    @param up: upvektor der Kamera
    """
    e = np.array([ex, ey, ez])  # eye position
    c = np.array([cx, cy, cz])  # center
    up = np.array([ux, uy, uz])  # up vector

    # normalize UpVector
    lup = np.sqrt(np.dot(up, up))
    up = up / lup
    # get the view direction
    f = c - e
    lf = np.sqrt(np.dot(f, f))
    f = f / lf
    # calculate s
    s = np.cross(f, up)
    ls = np.sqrt(np.dot(s, s))
    s = s / ls
    # calculate u
    u = np.cross(s, f)
    # create LookAtMatrix
    l = np.matrix([
                [s[0], s[1], s[2], -np.dot(s, e)],
                [u[0], u[1], u[2], -np.dot(u, e)],
                [-f[0], -f[1], -f[2], np.dot(f, e)],
                [0, 0, 0, 1]])
    return l


def rotationMatrix(angle, axis):
    """
    Rotationsmatrix um beliebige Achse im R3 als homogene Darstellung
    """
    angle = angle * np.pi / 180.
    c, mc = np.cos(angle), 1 - np.cos(angle)
    s = np.sin(angle)
    l = np.sqrt(np.dot(np.array(axis), np.array(axis)))
    x, y, z = np.array(axis) / l
    r = np.matrix([
                [x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
                [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
                [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
                [0, 0, 0, 1]])
    return r


def scaleMatrix(sx, sy, sz):
    """
    Matrix zum Skalieren
    @param s: scaleFactor
    """
    s = np.matrix([[sx, 0, 0, 0],
                [0, sy, 0, 0],
                [0, 0, sx, 0],
                [0, 0, 0, 1]])
    return s


def translationMatrix(tx, ty, tz):
    """
    Verschiebungsmatrix fuer Objekte
    @param t: vector um den verschoben wird
    """
    t = np.matrix([[1, 0, 0, tx],
                [0, 1, 0, ty],
                [0, 0, 1, tz],
                [0, 0, 0, 1]])
    return t


def perspectiveMatrix(fovy, aspect, zNear, zFar):
    """
    perspektivische Projektionsmatrix fuer Kamera
    @param fovy: Oeffnungswinkel der Kamera
    @param aspect: Seitenverhaeltnis der Kamera
    @param zNear: Nearplane der Kamera
    @param zFar: Farplane der Kamera
    """
    f = 1.0 / np.tan(fovy / 2.0)
    aspect = float(aspect)
    zNear = float(zNear)
    zFar = float(zFar)

    p = np.matrix([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (zFar + zNear) / (zNear - zFar),
         (2 * zFar * zNear) / (zNear - zFar)],
        [0, 0, -1, 0]
        ])
    return p


def rotate(angle, axis):
    """
    Rotationsmatrix um beliebige Achse und Winkel
    """
    c, mc = np.cos(float(angle)), 1 - np.cos(float(angle))
    s = np.sin(angle)
    l = np.sqrt(np.dot(np.array(axis), np.array(axis)))
    x, y, z = np.array(axis) / l
    r = np.matrix(
               [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],\
                [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],\
                [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
                [0, 0, 0, 1]])
    return r.transpose()


def projectOnSphere(x, y, r, width, height):
    """
    Projektion auf Einheitskugel fuer Arcball rotation
    @param x, y: abmessungen des viewports
    @param r: radius der Kugel
    @param width, height: Hoehe und breite den Viewports
    """
    x, y = x - width / 2.0, height / 2.0 - y
    a = min(r * r, x ** 2 + y ** 2)
    z = np.sqrt(r * r - a)
    l = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    return x / l, y / l, z / l


def rotationAroundAxis(angle, axis):
    """
    Rotaionsmatrix um beliebige Achse und Winkel
    """
    angle = angle * np.pi / 180.  # angle in bogenmass
    x, y, z = axis
    # norm vector x, y, z
    l = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    x, y, z = x / l, y / l, z / l
    # create matrix
    r = np.matrix([
                # zeile 1
                [x ** 2 * (1 - np.cos(angle)) + np.cos(angle),
                 x * y * (1 - np.cos(angle)) - z * np.sin(angle),
                          x * z * (1 - np.cos(angle)) + y * np.sin(angle), 0],
                # zeile 2
                [x * y * (1 - np.cos(angle)) + z * np.sin(angle),
                 y ** 2 * (1 - np.cos(angle)) + np.cos(angle),
                 y * z * (1 - np.cos(angle)) - x * np.sin(angle), 0],
                # zeile 3
                [x * z * (1 - np.cos(angle)) - y * np.sin(angle),
                 y * z * (1 - np.cos(angle)) + x * np.sin(angle),
                 z ** 2 * (1 - np.cos(angle)) + np.cos(angle), 0],
                #zeile 4
                [0, 0, 0, 1]
                ])
    return r


def sendValue(shaderProgram, varName, value):
    """
    sendet Wert an Shader der Grafikkarte
    @param shaderProgram: shader
    @param varName: Name der Variablen im shader
    @param value: zu setzender Wert im shader
    """
    varLocation = glGetUniformLocation(shaderProgram, varName)
    glUniform1f(varLocation, value)


def sendVec3(shaderProgram, varName, value):
    varLocation = glGetUniformLocation(shaderProgram, varName)
    glUniform3f(varLocation, *value)


def sendVec4(shaderProgram, varName, value):
    varLocation = glGetUniformLocation(shaderProgram, varName)
    glUniform4f(varLocation, *value)


def sendMat3(shaderProgram, varName, matrix):
    varLocation = glGetUniformLocation(shaderProgram, varName)
    glUniformMatrix3fv(varLocation, 1, GL_TRUE, matrix.tolist())


def sendMat4(shaderProgram, varName, matrix):
        varLocation = glGetUniformLocation(shaderProgram, varName)
        glUniformMatrix4fv(varLocation, 1, GL_TRUE, matrix.tolist())

if __name__ == '__main__':
#     actOri = eye(4)
#
#     trafo = rotationAroundAxis(45, (0, 0, 1))
#     actOri = trafo * actOri
#     #print actOri
#
#     trafo = rotationMatrix(-45, (1, 0, 0))
#     actOri = trafo * actOri
#     #print actOri
#
#     trafo = rotationMatrix(45, (1, 0, 0))
#     actOri = trafo * actOri
#     #print actOri
#
#     trafo = rotationMatrix(-45, (0, 0, 1))
#     actOri = trafo * actOri
    #print actOri
    #print actOri.astype(int)

    a = np.array([2, 2, 2, 1]) * rotationAroundAxis(45, (0, 0, 1))
