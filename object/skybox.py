'''
skybox.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Diese Klasse ist eine Vorlage fuer eine Skybox.
Die Skybox besteht aus einem 6-seitigen Wuerfel,
dessen Groesse uebergeben wird.

Er wird texturiert dargestellt und es ist moeglich,
mehrere Skybox-Texturen zu laden und gleichzeitig zu benutzen
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from mathematic import *
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.shaders import *
from mathematic import *
from numpy import array
import Image
import os


class Skybox(object):

    def __init__(self, program, texturelocation, s):
        """ initalisiert Skybox
        @param program: image-shader fuer Wuerfel
        @param texturelocation: Dateisystem Pfad zu Texturen
        @param s: Groesse / 2 der Skybox
        """

        p = [[-s, s, s], [s, s, s], [-s, -s, s], [s, -s, s],
             [-s, s, -s], [s, s, -s], [-s, -s, -s], [s, -s, -s]]

        self.data = [p[1] + [0, 0], p[0] + [1, 0], p[2] + [1, 1], p[3] + [0, 1],  # front
                     p[0] + [0, 0], p[4] + [1, 0], p[6] + [1, 1], p[2] + [0, 1],  # left
                     p[4] + [0, 0], p[5] + [1, 0], p[7] + [1, 1], p[6] + [0, 1],  # back
                     p[5] + [0, 0], p[1] + [1, 0], p[3] + [1, 1], p[7] + [0, 1],  # right
                     p[5] + [0, 0], p[4] + [1, 0], p[0] + [1, 1], p[1] + [0, 1],  # top 
                     p[3] + [0, 0], p[2] + [1, 0], p[6] + [1, 1], p[7] + [0, 1]]  # bottom

        self.program = program
        self.actTex = 0
        self.initSkybox(texturelocation)

    def initSkybox(self, location):
        """
        lade Bilder der Skybox in OpenGL
        @param location: Pfad zu Skybox-Bildern
        """
        faces = ['front', 'left', 'back', 'right', 'top', 'bottom']
        paths = ['water', 'beach', 'clouds', 'sky_hell_512']

        self.fileLength = len(faces)

        self.pillar = vbo.VBO(array(self.data, 'f'))

        self.boxes = len(paths)
        self.textureList = []

        for path in paths:

            textureIDs = glGenTextures(self.fileLength)

            for c, pic in enumerate(faces):
                im = Image.open(os.path.join(location, path, pic + ".png"))
                width, height = im.size
                image = array(im).tostring()  # mirror image on y-axis

                glBindTexture(GL_TEXTURE_2D, textureIDs[c])
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
                                GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
                                GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                              GL_RGB, GL_UNSIGNED_BYTE, image)
                glGenerateMipmap(GL_TEXTURE_2D)

            self.textureList.append(textureIDs)

    def drawSkybox(self, pMatrix, mvMatrix):
        """
        Zeichne die Skybox mit Hilfe von Matrizen und Shadern
        @param pMatrix: Die perspektivische Matrix
        @param mvMatrix: Die modelviewMatrix
        """ 
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        mvpMatrix = pMatrix * mvMatrix

        glUseProgram(self.program)
        sendMat4(self.program, "mvMatrix", mvMatrix)
        sendMat4(self.program, "mvpMatrix", mvpMatrix)

        self.pillar.bind()

        glVertexPointer(3, GL_FLOAT, 20, self.pillar)
        glTexCoordPointer(2, GL_FLOAT, 20, self.pillar + 12)

        for e in range(0, self.fileLength):
            glBindTexture(GL_TEXTURE_2D, self.textureList[self.actTex][e])
            glDrawArrays(GL_QUADS, e * 4, 4)

        self.pillar.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def nextTexture(self):
        """ setze die naechste Textur """
        self.actTex = (self.actTex + 1) % self.boxes

    def preTexture(self):
        """ nehme die vorhergehende Textur """
        self.actTex = self.actTex - 1
        if self.actTex < 0:
            self.actTex = self.boxes - 1
