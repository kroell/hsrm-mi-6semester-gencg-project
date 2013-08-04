

import math
from numpy import matrix, array


class Vector(object):
    ''' Vektorklasse fuer Vektoren im R3 '''
    def __init__(self, a, b, c):
        object.__init__(self)
        self.a = a
        self.b = b
        self.c = c

    def normalized(self):
        ''' bringe Vektor auf Laenge 1 '''
        l = self.length()
        if l != 0:
            self.a /= l
            self.b /= l
            self.c /= l
        return Vector(self.a, self.b, self.c)

    def length(self):
        ''' berechne Norm des Vektors '''
        return math.sqrt(self.a ** 2 + self.b ** 2 + self.c ** 2)

    def __repr__(self):
        ''' String-Repraesentation des Vektors '''
        return "Vector (%.9f, %.9f, %.9f)\n" % (self.a, self.b, self.c)

    def __add__(self, v):
        ''' komponentenweise addieren '''
        return Vector(self.a + v.a, self.b + v.b, self.c + v.c)

    def __sub__(self, v):
        ''' komponentenweise subtrahieren '''
        return Vector(self.a - v.a, self.b - v.b, self.c - v.c)

    def __rsub__(self, v):
        ''' rechtsseiter Operator - wird an __sub__ delegiert '''
        return self.__sub__(v)

    def __div__(self, v):
        ''' dividiere komponentenweise durch skalar '''
        return Vector(self.a / v, self.b / v, self.c / v)

    def __mul__(self, v):
        ''' komponentenweise multiplizieren '''
        if type(v) == type(self):
            return Vector(self.a * v.a, self.b * v.b, self.c * v.c)
        if type(v) in [float, int]:  # skalares multiplizieren
            return Vector(self.a * v, self.b * v, self.c * v)
        return None

    def __rmul__(self, v):
        ''' rechtsseitiger Operator, delegiert Befehl an linksseitigen '''
        return self.__mul__(v)

    def dot(self, v):
        ''' normales skalarprodukt mit Vektorinstanz und Operand '''
        return self.a * v.a + self.b * v.b + self.c * v.c

    def scale(self, number):
        ''' skaliert einen Vektor komponentenweise mit einem skalar '''
        return Vector(self.a * number, self.b * number, self.c * number)

    def cross(self, v):
        ''' normales kreuzprodukt zwischen Vektorinstanz und v '''
        a = self.b * v.c - self.c * v.b
        b = self.c * v.a - self.a * v.c
        c = self.a * v.b - self.b * v.a
        return Vector(a, b, c)

    def reflect(self, normal):
        ''' reflektiert einen vektor: einfallswinkel = ausfallswinkel '''
        return self - 2 * normal.dot(self) * normal

    def __getitem__(self, index):
        if index == 0:
            return self.a
        elif index == 1:
            return self.b
        elif index == 2:
            return self.c

    def __setitem__(self, key, value):
        if key == 0:
            self.a = value
        elif key == 1:
            self.b = value
        elif key == 2:
            self.c = value

    def angle(self, v1):
        a = self.dot(v1) / (self.length() * v1.length())
        return math.degrees(math.acos(a))

    def sqrt(self):
        a = math.sqrt(self.a)
        b = math.sqrt(self.b)
        c = math.sqrt(self.c)
        return Vector(a, b, c)

    def multMatrix(self, mat):
        v = (array([self.a, self.b, self.c, 1]) * mat).tolist()[0][:3]
        return Vector(v[0], v[1], v[2])

    def copy(self):
        return Vector(self.a, self.b, self.c)

    def __iter__(self):
        return (x for x in [self.a, self.b, self.c])

if __name__ == '__main__':
    v1 = Vector(0, -1, 0)
    v2 = Vector(0, 0, 1)
    v3 = Vector(0, 1, 0)
    v4 = Vector(1, 2, 3)
    x, y, z = v4
    print x, y, z
    #print v1.result(v2)
