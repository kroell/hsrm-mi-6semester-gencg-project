"""
rotor.py

@author: Justin Albert, Tino Landmann, Soeren Kroell

Klasse fuer Rotoren-Objekte. Ein Rotor gehoert zu genau
einem Helicopter. Jeder Helicopter hat mindestens zwei
dieser Rotorenobjekte.
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.shaders import *
from OpenGL.arrays import vbo
from mathematic import geometry as geo
from numpy import linalg, array, eye
import Image
from mathematic.geometry import rotationAroundAxis


class Rotor(object):
    '''
    Defines the Helicopter Rotor
    '''

    rotorType = {"main": (0, 1, 0), "heck": (1, 0, 0)}

    def __init__(self, rotorVbo, rotorTextureID, rotorDataLen, rotorData,
                 matDic, program, rotorMat, rotorType, dist, maximum=5):
        """
        Konstruktor fuer Rotorobjekt
        @param rotorVbo: vbo-file fuer rotor
        @param rotorTextureID: texturID fuer rotor
        @param rotorDataLen: Laenge der vertices des rotors
        @param rotorData: die Objektvertices des rotors
        @param matDic: Dictionairy mit allen Materialien
        @param program: shader fuer iamges
        @param rotorMat: Material des Rotors
        @param rotorType: Art vom Rotors, entweder heck oder main
        @param dist: boundingbox groesse zu mittelpunkt
        @param maximum: Maximale Umdrehungen
        """
        self.rotorVbo = rotorVbo
        self.rotorTextureId = rotorTextureID
        self.rotorDataLen = rotorDataLen
        self.mainRotorData = rotorData
        self.matDic = matDic
        self.program = program
        self.rotorMat = rotorMat
        self.actOri = eye(4)  # =vll gar nicht gebraucht...
        self.axis = self.rotorType[rotorType]
        self.rotationMatrix = eye(4)
        self.r = 1
        self.maximum = maximum
        self.dist = dist
        self.start = False

    def drawRotor(self, pMat, mvMat, rotMat, transMat, speed):
        """
        Zeichne den Rotor mit allen Matrizen. Berechne Drehungen
        korrekt
        @param pMat: perspektivische Matrix des Helis
        @param mvMat: modelviewMatrix der Camera
        @param rotMat: vorberechnete Rotationsmatrix des Rotors
        @param transMat: translationsmatrix des Helicopters
        @param speed: aktueller Auftrieb des Helicopters
        """
        if self.start and self.r < self.maximum:
            if speed < 1:
                if self.r < self.maximum + 4:
                    self.r += 0.009
            elif speed > 1:
                if self.r > self.maximum - 1:
                    self.r -= 0.009
            else:
                if self.r < self.maximum - 1:
                    self.r += 0.009
        else:
            if self.r > 1:
                self.r -= 0.009

        (a, b, c) = self.dist
        t = geo.translationMatrix(a, b, c)
        tb = geo.translationMatrix(-a, -b, -c)
        f = geo.rotationMatrix(self.r, self.axis)
        self.rotationMatrix = self.rotationMatrix * t * f * tb

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glEnable(GL_TEXTURE_2D)

        modelMatrix = mvMat * transMat * rotMat * self.rotationMatrix
        mvpMatrix = pMat * modelMatrix

        normalMat = linalg.inv(modelMatrix[0:3, 0:3]).transpose()
        glUseProgram(self.program)
        geo.sendMat4(self.program, "mvMatrix", modelMatrix)
        geo.sendMat4(self.program, "mvpMatrix", mvpMatrix)
        geo.sendMat3(self.program, "normalMatrix", normalMat)

        self.useRotorGeometry()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def useRotorGeometry(self):
        '''
        Lese farben, texturen und geometrie ein
        '''
        lightPos = [0, 1, 1]

        # matDic[material][0] = diffColor, matDic[material][4] = alphaValue
        geo.sendVec4(self.program, "diffuseColor",\
                     self.matDic[self.rotorMat][0]\
                     + self.matDic[self.rotorMat][4])
        geo.sendVec4(self.program, "ambientColor",
                     self.matDic[self.rotorMat][1]\
                     + self.matDic[self.rotorMat][4])
        geo.sendVec4(self.program, "specularColor",
                     [x ** self.matDic[self.rotorMat][3][0]\
                      for x in self.matDic[self.rotorMat][2]\
                      + self.matDic[self.rotorMat][4]])
        geo.sendVec3(self.program, "lightPosition", lightPos)

        self.rotorVbo.bind()

        glVertexPointer(3, GL_FLOAT, 36, self.rotorVbo)
        glNormalPointer(GL_FLOAT, 36, self.rotorVbo + 24)
        glTexCoordPointer(3, GL_FLOAT, 36, self.rotorVbo + 12)

        if self.rotorTextureId:
            glBindTexture(GL_TEXTURE_2D, self.rotorTextureId)
        else:
            glBindTexture(GL_TEXTURE_2D, 1)
        glDrawArrays(GL_TRIANGLES, 0, self.rotorDataLen)

        self.rotorVbo.unbind()
