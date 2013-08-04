'''
helipad.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Diese Klasse ist Vorlage fuer ein HeliPad Spielobjekt

Durch eingebaute Collision Detection ist es moeglich,
den Helicopter im Spiel auf dem Helipad zu landen
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from mathematic import *
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.shaders import *
from numpy import array, linalg
from mathematic import geometry as geo
import Image
import os
import math


class HeliPad(object):

    def __init__(self, program, radius, gamesize, height, faces, x, z):
        """
        Konstruktor fuer Helipad
        @param program: image-Shader fuer Helipad
        @param radius: Radius fuer die Saeule des Helipads
        @param gamesize: Groesse / 2 der Skybox
        @param height: Absolute Hoehe des Helipads
        @param faces: Flaechen der Saeule, Approximativer Kreis
        @param x: Verschiebung auf der Welt nach x
        @param z: Verschiebung auf der Welt nach z
        """
        self.radius = radius
        self.height = height
        self.faces = faces
        self.program = program
        self.x = x
        self.z = z
        self.gamesize = gamesize
        self.tMat = geo.translationMatrix(x, -gamesize, z)

        self.initHeliPad()

    def initHeliPad(self):
        """
        berechne den Umfang der Saeule fuer das Helipad
        und erstelle Rechteck fuer die Landeplattform
        """
        images = ['pillar', 'top']

        texCoords = [[0, 0], [1, 0], [0, 1], [1, 1]]

        r = self.faces / 2.

        points = []
        for i in range(self.faces + 1):
            x, z = math.cos(i * math.pi / r) * 1.5, math.sin(i * math.pi / r) * 1.5
            points.append([x, 0, z])
            points.append([x, self.height, z])

        dataList = []
        for i in range(0, self.faces * 2, 2):
            for e in range(4):
                dataList.append(points[i + e] + texCoords[e])

        self.len = len(dataList)

        self.pillar = vbo.VBO(array(dataList, 'f'))

        ### plattform

        r = self.radius * 1.5
        s = self.height
        size = self.height * 0.001
        p = [[-r, s, r], [r, s, r], [-r, s - size, r], [r, s - size, r],
             [-r, s, -r], [r, s, -r], [-r, s - size, -r], [r, s - size, -r]]

        top = [p[5] + [0, 0], p[4] + [1, 0], p[0] + [1, 1], p[1] + [0, 1],  # top
               p[1] + [0, 0], p[0] + [1, 0], p[2] + [1, 1], p[3] + [0, 1],  # front
               p[0] + [0, 0], p[4] + [1, 0], p[6] + [1, 1], p[2] + [0, 1],  # left
               p[4] + [0, 0], p[5] + [1, 0], p[7] + [1, 1], p[6] + [0, 1],  # back
               p[5] + [0, 0], p[1] + [1, 0], p[3] + [1, 1], p[7] + [0, 1],  # right  
               p[3] + [0, 0], p[2] + [1, 0], p[6] + [1, 1], p[7] + [0, 1]]  # bottom

        self.top = vbo.VBO(array(top, 'f'))
        self.bb = [(-r + self.x, -self.gamesize, -r + self.z),
                   (r + self.x, self.height - self.gamesize, r + self.z)]
        self.textureID = glGenTextures(2)

        # load image
        for c, im in enumerate(images):
            image = Image.open(os.path.join("textures/helipad", im + '.png'))
            width, height = image.size
            imagedata = array(image)
            imagedata = imagedata[::-1, :]
            imagedata = imagedata.tostring()

            glBindTexture(GL_TEXTURE_2D, self.textureID[c])

            glBindTexture(GL_TEXTURE_2D, self.textureID[c])
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB,
                                 GL_UNSIGNED_BYTE, imagedata)
            glGenerateMipmap(GL_TEXTURE_2D)

    def drawHeliPad(self, pMatrix, mvMatrix):
        """
        zeichne das HeliPad mit Hilfe von Shadern und Matrizen
        @param pMatrix: perspektivische Matrix der Camera
        @param mvMatrix: modelview Matrix der Camera
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        mvMatrix = mvMatrix * self.tMat
        mvpMatrix = pMatrix * mvMatrix

        glUseProgram(self.program)
        sendMat4(self.program, "mvMatrix", mvMatrix)
        sendMat4(self.program, "mvpMatrix", mvpMatrix)

        self.pillar.bind()

        glVertexPointer(3, GL_FLOAT, 20, self.pillar)
        glTexCoordPointer(2, GL_FLOAT, 20, self.pillar + 12)

        for e in range(0, self.faces):
            glBindTexture(GL_TEXTURE_2D, self.textureID[0])
            glDrawArrays(GL_TRIANGLE_STRIP, e * 4, 4)

        self.pillar.unbind()

        self.top.bind()

        glVertexPointer(3, GL_FLOAT, 20, self.pillar)
        glTexCoordPointer(2, GL_FLOAT, 20, self.pillar + 12)

        for e in range(6):
            if e == 0:
                glBindTexture(GL_TEXTURE_2D, self.textureID[1])
            else:
                glBindTexture(GL_TEXTURE_2D, self.textureID[0])
            glDrawArrays(GL_QUADS, e * 4, 4)

        self.top.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def __repr__(self):
        """ String Repraesentation des Helipads """
        return "Helipad at %s" % str(self.position)
