"""
space.py
@author: Justin Albert, Tino Landmann, Soeren Kroell

Diese Klasse ist das Herzstueck der Anwendung.
Der Space ist der Simulator des Programms und errechnet
fuer jedes Objekt die neue Positions pro Tick.
Da es in dieser Anwendung nur ein beweglichen Objekt gibt,
wird auch nur fuer dieses Objekt eine neue Position berechnet.
Es ist moeglich dem space neue Spielobjekte hinzuzufuegen,
die dann mit in die Collision Detection uebernommen werden.
"""


from mathematic import Vector
from mathematic import geometry as geo


class Space(object):
    """ Space-Class contains all objects for the simulation """

    def __init__(self, heli, size, g):
        """
        Konstruktor fuer den Space
        @param heli: das main-spiel objekt des spaces
        @param size: die groesse, festgelegt von skybox
        @param g: gravity, die Schwerkraft die im Raum wirkt
        """
        self.heli = heli
        self.size = size  # always a cube
        self.objs = []
        self.gravity = Vector(0, g, 0)
        self.collision = False
        self.padCollision = False

    def intersectBB(self, heliBB):
        """
        prueft, ob es eine Kollision mit einer aussenwand
        der skybox gegeben hat
        """
        (x1, y1, z1), (x2, y2, z2) = heliBB[0], heliBB[1]
        size = self.size - 10
        if -size < x1 and x2 < size:  # check x
            if -size < y1 and y2 < size:  # check y
                if -size < z1 and z2 < size:  # check z
                    return False
        return True

    def intersect(self, a, b):
        """
        Testet auf Schnittpunkt von zwei BoundingBoxen im R3
        """
        (ax1, ay1, az1), (ax2, ay2, az2) = a[0], a[1]
        (bx1, by1, bz1), (bx2, by2, bz2) = b[0], b[1]
        if not(bx1 > ax2 or bx2 < ax1):  # intersection x
            if not(by1 > ay2 or by2 < ay1):  # intersection y
                if not(bz1 > az2 or bz2 < az1):  # intersection z
                    return True
        return False

    def step(self):
        """
        Berechnet fuer alle Objekten die neue Position im neuen step
        Fuer den Helicopter wird eine Vorberechnung der moeglichen
        neuen Position durchgefuehrt und bei Erfolg diese Position
        uebernommen
        """
        detection, padDetection = False, False  # flag for collision detection
                                                # with all objects

        up = Vector(0, 1, 0).multMatrix(self.heli.actOri.T)
        temp = self.heli.position + (up + self.gravity) * 0.15  # kraftvektor
        temp += Vector(0, 1, 0) + self.gravity * self.heli.speed  # auftrieb
        tempBB = map(lambda x: x + temp, self.heli.bb)
        if self.intersectBB(tempBB):
            detection = True
        else:
            for obj in self.objs:
                if self.intersect(tempBB, obj.bb):
                    padDetection = True
                    self.heli.speed = 1

        self.collision = True if detection else False
        self.padCollision = True if padDetection else False

        if not self.collision and not self.padCollision:
            self.heli.position = temp
            (x, y, z) = self.heli.position
            self.heli.translationMatrix = geo.translationMatrix(x, y, z)

    def gier(self, angle):
        """
        rotiere den Helicopter um die y-Achse
        """
        t = geo.rotationAroundAxis(angle, (0, 1, 0))
        self.heli.actOri = self.heli.actOri * t

    def elevator(self, angle):
        """
        nicke den Helicopter nach vorne um die x-Achse
        """
        t = geo.rotationAroundAxis(angle, (1, 0, 0))
        self.heli.actOri = self.heli.actOri * t

    def aileron(self, angle):
        """
        neige den Helicopter nach links oder rechts um z-Achse
        """
        t = geo.rotationAroundAxis(angle, (0, 0, 1))
        self.heli.actOri = self.heli.actOri * t

    def pitch(self, direction):
        """
        setze den Faktor fuer Auftrieb des Hubschraubers
        """
        if self.heli.mainRotor.start:
            self.heli.speed += 0.0001 * direction

    def getPosition(self):
        """
        gibt die aktuelle Position des Helicopters als Tupel zurueck
        """
        return Vector(0, 0, 0).multMatrix(self.heli.translationMatrix.T)

    def reset(self):
        """
        setzt helicopter an Ursprung zurueck
        """
        self.heli.position = self.heli.startPosition
        self.heli.translationMatrix =\
        geo.translationMatrix(self.heli.position[0],
                              self.heli.position[1],
                              self.heli.position[2])
        self.heli.speed = 1
        self.heli.actOri = geo.identity()
        self.heli.collision = False

    def startHeli(self):
        """
        Starte die Rotoren des Helicopters.
        Kann nicht ohne gestartete Rotoren abheben.
        """
        if self.padCollision:
            self.heli.mainRotor.start ^= True
            self.heli.tailRotor.start ^= True

    def __repr__(self):
        return """
        Spaceobject for Helicopter-Simulation:
        playerObject: %s
        gameObjects: %s
        """ % (str(self.heli), str(self.objs))

    def addObject(self, obj):
        """
        Fuege dem Space ein neues Objekt hinzu
        """
        self.objs.append(obj)
