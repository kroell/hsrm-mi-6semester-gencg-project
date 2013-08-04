'''
objLoader.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

'''

from OpenGL.arrays import vbo
from numpy import array
from OpenGL.GL import *

import Image


class ObjLoader(object):
    """
    Diese Klasse laedt ein objFile inklusive des Materials files.
    Sie erzeugt ausserdem eine data List mit den Faces und Texture IDS
    der gegebenen Textur
    """

    def __init__(self, size=1, filename=None):
        """
        Konstruktor fuer objLoader
        @param size: groesse des objekts
        @param filename: Dateiname des objFiles
        """
        self.filename = filename
        self.objectVertices = []
        self.objectTextures = []
        self.objectNormals = []
        self.objectFaces = []

        self.facesDic = {}
        self.matDic = {}

        self.size = size  # object size

    def loadObjFile(self, filename=None):
        """
        Laedt ein obj File und returnt drei Listen mit object-vertices,
        objekt-normalen und objekt-faces
        """

        counterMatNames = 0
        matName, matFilePath = None, None

        if filename == None:
            filename = self.filename

        try:
            for lines in file(filename):
                temp1_objectFaces = []
                temp2_objectFaces = []

                # check if not empty
                if lines.split():
                    check = lines.split()[0]
                    if check == 'mtllib':
                        matFilePath = "".join(lines.split()[1:])
                    if check == 'v':
                        self.objectVertices.append(map(float,
                                                   lines.split()[1:]))
                    if check == 'vt':
                        self.objectTextures.append(map(float,
                                                   lines.split()[1:]))
                    if check == 'vn':
                        self.objectNormals.append(map(float,
                                                      lines.split()[1:]))
                    if check == 'usemtl':
                        matName = None
                        matName = "".join(lines.split()[1:])
                        counterMatNames += 1
                    if check == 'f':
                        first = lines.split()[1:]

                        # if face is a square
                        if len(first) == 4:
                            for face in first[:3]:
                                temp1_objectFaces.append(map(float,
                                                             face.split('/')))

                            for face in first[:-3] + first[2:4]:
                                temp2_objectFaces.append(map(float,
                                                             face.split('/')))

                        # if face is a triangle
                        if len(first) == 3:
                            for face in first:
                                temp1_objectFaces.append(map(float,
                                                             face.split('/')))

                    # Add everything to a dict
                    if not matName in self.facesDic.keys():
                        self.facesDic[matName] = self.facesDic.get(matName,
                                                            temp1_objectFaces)
                    else:
                        self.facesDic[matName].append(temp1_objectFaces)
                        self.facesDic[matName].append(temp2_objectFaces)

            # automatically start loading the material files if there is one
            if matFilePath:
                self.loadMaterial(matFilePath)

            bb = [map(min, zip(*self.objectVertices)),
                  map(max, zip(*self.objectVertices))]
            center = [(x[0] + x[1]) / 2.0 for x in zip(*bb)]
            scale = 2.0 / max([(x[0] - x[1]) for x in zip(*bb)])
            scale *= self.size * 0.0025625
            self.objectVertices = [[-1 * (p[0] - center[0]) * scale,
                                    -1 * (p[1] - center[1]) * scale,
                                    -1 * (p[2] - center[2]) * scale]
                                   for p in self.objectVertices]
            newBB = [map(min, zip(*self.objectVertices)),
                   map(max, zip(*self.objectVertices))]
            return self.objectVertices, self.facesDic, self.matDic, newBB

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Fehler beim Einlesen des obj Files"

    def loadMaterial(self, filename):
        '''
        Laedt das Material aus filename.mtl und speichert alle Informationen
        in einem Material-dictonairy
        Das Dictonairy sieht folgendermassen aus:
        matDic = {matName : [ambientColor], [diffusColor],
                            [ specularColor], [specularExponent],
                            [alphaValue], [textureFile] }
        '''

        matFile = file("heli_data/" + filename).readlines()

        for matName in self.facesDic.keys():
            matInfos = []
            nameCheck = False
            flag = 0

            for lines in matFile:
                if lines.split():
                    check = lines.split()[0]
                    if check != '#':
                        if lines.split()[1] == matName:
                            nameCheck = True
                    if nameCheck:
                        if check == 'Ka':
                            ambCol = []
                            ambCol += map(float, lines.split()[1::])
                        if check == 'Kd':
                            diffCol = []
                            diffCol += map(float, lines.split()[1::])
                        if check == 'Ks':
                            specCol = []
                            specCol += map(float, lines.split()[1::])
                        if check == 'Ns':
                            nsExp = None
                            nsExp = map(float, lines.split()[1::])
                        if check == 'd':
                            alphaValue = None
                            alphaValue = map(float, lines.split()[1::])
                        if check == 'map_Kd':
                            textureFile = None
                            textureFile = map(str, lines.split()[1::])
                            if not flag:
                                matInfos += ambCol, diffCol, specCol, nsExp,\
                                            alphaValue, textureFile
                                flag += 1
                        self.matDic[matName] = self.matDic.get(matName,
                                                               matInfos)

    def createData(self, faces):
        """
        Gibt eine Daten Liste mit v/vt/vn fuer die gegebenen Faces
        """
        data = []

        for face in faces:
            for vertex in face:
                vn = int(vertex[0]) - 1
                tn = int(vertex[1]) - 1
                nn = int(vertex[2]) - 1

                data.append(self.objectVertices[vn] + self.objectTextures[tn]
                            + self.objectNormals[nn])

        return data

    def createTextureId(self, imagePath):
        """
        Gibt eine Texture ID fuer gegebenen Texture-Bild-Pfad
        """
        textureId = None

        im = Image.open("./heli_data/" + "".join(imagePath))
        width, height = im.size
        image = array(im)[::-1, :].tostring()
        textureId = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, textureId)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, image)

        return textureId
