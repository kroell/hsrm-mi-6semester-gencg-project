'''
helicopter.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Diese Klasse ist eine Vorlage fuer einen Helicopter der
im .obj fileformat gegeben ist. Er besteht aus 13 Materialien und
wird texturiert dargestellt

'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.shaders import *
from OpenGL.arrays import vbo
from mathematic import geometry as geo
from mathematic import Vector
import Image
from mathematic.geometry import rotationAroundAxis, translationMatrix
from object.rotor import Rotor
import random
import numpy as np


class Helicopter(object):

    def __init__(self, program, objLoader, pos, filename):
        """
        initialisiere den Helicopter
        @param program: Shader fuer Helicopter inklusive Schattierung
        @param objLoader: Obj-File Loader fuer die Objektdatei
        @pos: Startposition des Helicopters
        @filename: Name der Objektdatei
        """
        self.filename = filename
        self.startPosition = Vector(pos[0], pos[1], pos[2])
        self.position = pos
        self.objLoader = objLoader

        self.facesDic = {}
        self.matDic = {}
        self.vboList = []
        self.textureIdList = []
        self.vboTextureDic = {}

        self.mainRotorMat = "500-D_Negro1"
        self.tailRotorMat = "500-D_Blanco"
        self.program = program

        # init Heli
        self.initHelicopter()

        self.speed = 1

    def initHelicopter(self):
        """
        initialisiere Helicopter mit Hilfe von Obj-Loader
        """
        # load obj File
        self.objectVertices, self.facesDic, self.matDic, self.bb =\
        self.objLoader.loadObjFile(self.filename)
        (a, b, c), (d, e, f) = self.bb[0], self.bb[1]
        self.bb = [Vector(a, b, c), Vector(d, e, f)]
        self.startPosition[1] += abs(b)  # vector
        self.position = self.startPosition
        self.translationMatrix = geo.translationMatrix(self.position[0],
                                                       self.position[1],
                                                       self.position[2])
        # initial Helicopter Geometry
        self.initHelicopterGeometry()

        rojoData = self.objLoader.createData(self.facesDic["500-D_Rojo"])

        maxRotor = [max([x[0] for x in rojoData]),
                    max([x[1] for x in rojoData]),
                    max([x[2] for x in rojoData])]

        minRotor = [min([x[0] for x in rojoData]),
                    min([x[1] for x in rojoData]),
                    min([x[2] for x in rojoData])]

        mittel = map(lambda x, y: x + (y - x) / 2, minRotor, maxRotor)

        #### MAIN
        self.mainRotor = Rotor(self.vboTextureDic[self.mainRotorMat][0],
                               self.vboTextureDic[self.mainRotorMat][1],
                               self.vboTextureDic[self.mainRotorMat][2],
                               self.objLoader.createData(self.facesDic[
                               self.mainRotorMat]),
                               self.matDic, self.program,
                               self.mainRotorMat, "main", mittel)

        #### TAIL und FrontLine separieren
        tailRotorFaces = []
        frontLine = []

        for facesList in self.facesDic[self.tailRotorMat]:
            for faces in facesList:
                if [singleFace for singleFace in faces if singleFace > 2720]\
                    != []:
                    tailRotorFaces.append([singleFace for singleFace in faces\
                                            if singleFace > 2720])
                if [singleFace for singleFace in faces if singleFace < 2720]\
                    != []:
                    frontLine.append([singleFace for singleFace in faces])

        self.tailRotorData = self.objLoader.createData([tailRotorFaces])
        self.tailRotorDataLen = len(self.tailRotorData)
        self.tailRotorVbo = vbo.VBO(np.array(self.tailRotorData, 'f'))
        self.tailRotorTextureId = self.vboTextureDic[self.tailRotorMat][1]

        frontLineData = self.objLoader.createData([frontLine])
        frontLineDataLen = len(frontLineData)
        self.frontLineDataLenList = []
        self.frontLineDataLenList.append(frontLineDataLen)
        frontLineVbo = vbo.VBO(np.array(frontLineData, 'f'))
        self.frontLineVboList = []
        self.frontLineVboList.append(frontLineVbo)
        frontLineTextureId = self.vboTextureDic[self.tailRotorMat][1]
        self.frontLineTextureIdList = []
        self.frontLineTextureIdList.append(frontLineTextureId)

        maxRotor = [max([x[0] for x in self.tailRotorData]),
                    max([x[1] for x in self.tailRotorData]),
                    max([x[2] for x in self.tailRotorData])]

        minRotor = [min([x[0] for x in self.tailRotorData]),
                    min([x[1] for x in self.tailRotorData]),
                    min([x[2] for x in self.tailRotorData])]

        mittel = map(lambda x, y: x + (y - x) / 2, minRotor, maxRotor)

        self.tailRotor = Rotor(vbo.VBO(np.array(self.tailRotorData, 'f')),
                               self.vboTextureDic[self.tailRotorMat][1],
                               len(self.tailRotorData),
                               self.objLoader.createData([tailRotorFaces]),
                               self.matDic, self.program, self.tailRotorMat,
                               "heck", mittel, 12)

        self.actOri = geo.identity()

        # Frontline zum vboTextureDic hinzufuegen
        del(self.vboTextureDic[self.tailRotorMat])
        if not self.tailRotorMat in self.vboTextureDic.keys():
            self.vboTextureDic[self.tailRotorMat] =\
            self.vboTextureDic.get(self.tailRotorMat,
                                   self.frontLineVboList\
                                   + self.frontLineTextureIdList\
                                   + self.frontLineDataLenList)
        else:
            self.vboTextureDic[self.tailRotorMat].append(self.frontLineVboList\
                                                 + self.frontLineTextureIdList\
                                                 + self.frontLineDataLenList)

    def initHelicopterGeometry(self):
        '''
        Rendere den Helicopter
        '''
        for material, faces in self.facesDic.items():
            if material:
                dataList, lenDataList, vboList, textureIdList = [], [], [], []
                temp_vbo, temp_textureId = None, None

                # create data
                dataList = self.objLoader.createData(self.facesDic[material])

                # create vbo
                temp_vbo = vbo.VBO(np.array(dataList, 'f'))

                # create textureId
                if "".join(self.matDic[material][5]) != 'Null':
                    temp_textureId =\
                    self.objLoader.createTextureId(self.matDic[material][5])
                else:
                    temp_textureId = 0

                vboList.append(temp_vbo)
                textureIdList.append(temp_textureId)
                lenDataList.append(len(dataList))

                # make dict with vbo,textureId and len(data)
                if not material in self.vboTextureDic.keys():
                    self.vboTextureDic[material] =\
                    self.vboTextureDic.get(material,
                                           vboList + textureIdList\
                                           + lenDataList)
                else:
                    print "else"
                    self.vboTextureDic[material].append(vboList + textureIdList
                                                        + lenDataList)

    def drawHelicopter(self, pMatrix, mvMatrix):
        '''
        Zeichne den Helicopter pro Step
        @param pMatrix: die Perspektivische Matrix der Camera
        @param mvMatrix: die Modelviewmatrix der Camera
        '''
        self.mainRotor.drawRotor(pMatrix, mvMatrix, self.actOri,
                                 self.translationMatrix, self.speed)
        self.tailRotor.drawRotor(pMatrix, mvMatrix, self.actOri,
                                 self.translationMatrix, self.speed)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glEnable(GL_TEXTURE_2D)

        mvMat = mvMatrix * self.translationMatrix * self.actOri
        mvpMatrix = pMatrix * mvMat

        normalMat = np.linalg.inv(mvMat[0:3, 0:3]).T

        glUseProgram(self.program)
        geo.sendMat4(self.program, "mvMatrix", mvMat)
        geo.sendMat4(self.program, "mvpMatrix", mvpMatrix)
        geo.sendMat3(self.program, "normalMatrix", normalMat)

        self.useHelicopterGeometry()

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def useHelicopterGeometry(self):
        '''
        Zeichne fuer jedes VBO farben, Texturen und Daten
        '''
        lightPos = [0, 1, 1]

        # vboTextureDic = {matName:[vbo],[textureId],[len(data)]}
        for material, value in self.vboTextureDic.items():
            if material != self.mainRotorMat:
                act_vbo = value[0]
                act_textureId = value[1]
                lenData = value[2]

                # colors to shader
                geo.sendVec4(self.program, "diffuseColor",
                             self.matDic[material][0]\
                             + self.matDic[material][4])

                # if texture, use white as ambient color
                if act_textureId:
                    geo.sendVec4(self.program, "ambientColor",
                                 [1.0, 1.0, 1.0] + self.matDic[material][4])
                else:
                    geo.sendVec4(self.program, "ambientColor",
                                self.matDic[material][1]\
                                + self.matDic[material][4])

                geo.sendVec4(self.program, "specularColor",
                            [x ** self.matDic[material][3][0]\
                             for x in self.matDic[material][2]\
                             + self.matDic[material][4]])
                geo.sendVec3(self.program, "lightPosition", lightPos)

                # use vbo
                act_vbo.bind()

                glVertexPointer(3, GL_FLOAT, 36, act_vbo)
                glNormalPointer(GL_FLOAT, 36, act_vbo + 24)
                glTexCoordPointer(3, GL_FLOAT, 36, act_vbo + 12)

                if act_textureId:
                    glBindTexture(GL_TEXTURE_2D, act_textureId)
                elif material == self.tailRotorMat:
                    glBindTexture(GL_TEXTURE_2D, 8)
                else:
                    glBindTexture(GL_TEXTURE_2D, 1)
                glDrawArrays(GL_TRIANGLES, 0, lenData)

                act_vbo.unbind()

    def __repr__(self):
        """ String repreasentation des Helicopters """
        return "Helicopter at %s " % str(self.position)
