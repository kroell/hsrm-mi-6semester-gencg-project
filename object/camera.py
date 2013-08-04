'''
camera.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Die Anwendung erlaubt es, mehrere Kamerapositionen auszuwaehlen.
Es steht eine abstrakte Klasse Camera zur Verfuegung.

Als konkrete Auspraegungen gibt es
-FreeCamera: Steht an fixer Position, kann mit Arcball rotiert werden
-HeliCamera: Verfolgt den Heli aus der Ego-Perspektive
-ActionCamera: Steht an fixer Position und fokussiert Helicopter
'''

from mathematic import geometry as geo
import numpy as np
from mathematic import Vector


class Camera(object):
    """ Abstrakte Klasse fuer verschiedene Kamerapositionen """
    def __init__(self):
        pass


class FreeCamera(Camera):
    """
    Instanzen dieser Klassen stehen an einer festen Position
    haben nur mvMat und pMat als Transformationen
    """

    def __init__(self, e, c, up):
        """
        Konstruktor fuer FreeCamera mit Arcball rotation
        @param e: standpunkt der camera
        @param c: blickpunkt der camera
        @param up: up-vektor der camera
        """
        Camera.__init__(self)
        self.mvMat = geo.lookAtMatrix(e[0], e[1], e[2],  # position
                                      c[0], c[1], c[2],  # center
                                      up[0], up[1], up[2])  # up vector
        self.actOri = geo.identity()
        self.rotation = geo.identity()
        self.zoomMat = geo.identity()

    def changeOrientation(self, angle, axis):
        """
        aktualisiere die Orientierung der Arcball rotation
        @param angle: winkel um den gedreht wird
        @param axis: achse um die gedreht wurde
        """
        self.actOri = self.actOri * geo.rotate(angle, axis)

    def rotate(self, angle, axis):
        """
        rotiere die aktuelle Orientierung
        @param angle: winkel der Transformation
        @param axis: Achse um die gedreht wird
        """
        self.rotation = self.actOri * geo.rotate(angle, axis)

    def zoom(self, zoom):
        """
        Zoom der Camera, strekt die Matrix mit Zoomfaktor
        @param zoom: zoomfaktor
        """
        self.zoomMat = geo.scaleMatrix(zoom, zoom, zoom)

    def getMvMat(self):
        """
        gibt die Modelviewmatrix zurueck mit allen kumulierten matrizen
        """
        return self.mvMat * self.rotation * self.zoomMat


class HeliCamera(Camera):
    """
    Camera steht an Helicopter und bewegt sich entsprechend mit
    """
    def __init__(self, factor, height):
        """
        Konstruktor fuer HeliCamera
        @param factor: scale-Faktor fuer den Vektor f = c - e
        @param height: Hoehe, auf die auf Punkt e addiert wird
        """
        Camera.__init__(self)
        self.factor = factor
        self.height = height

    def getMvMat(self, e, actOri):
        """
        Errechnet ModelviewMatrixTransformation
        @param e: standpunkt helicopter
        @param actOri: aktuelle Ausrichtung des Helicopters
        """
        up = Vector(0, 1, 0).multMatrix(actOri.T).normalized()
        c = Vector(0, 0, 1).multMatrix(actOri.T)  # blickrichtung
        a = e.copy()
        a[1] += self.height
        ce = a + c
        a = a - c * self.factor
        return geo.lookAtMatrix(a[0], a[1], a[2],
                                ce[0], ce[1], ce[2],
                                up[0], up[1], up[2])


class ActionCamera(Camera):
    """ Kamera verfolgt Helicopter """
    def __init__(self, pos):
        """
        Initialisiere ActionCamera
        @param pos: Position an der Kamera steht. Punkt e
        """
        Camera.__init__(self)
        self.pos = Vector(pos[0], pos[1], pos[2])
        self.actOri = geo.identity()
        self.rotation = geo.identity()

    def getMvMat(self, center):
        """
        gibt Modelview-Matrix zurueck mit Hilfe von Helicopter Position
        @param center: Position an der helicopter steht
        """
        (x, y, z) = self.pos
        (a, b, c) = center
        return geo.lookAtMatrix(x, y, z, a, b, c, 0, 1, 0)
