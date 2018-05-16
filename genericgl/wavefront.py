#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import array

class _Vertex():

    def __init__(self, vertexIndex, x, y, z):

        self.index = vertexIndex 

        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        self.faces = [];

        self.calculatedNormal = None

    def recalculateNormal(self):
        normals = []

        x = 0.0
        y = 0.0
        z = 0.0
        num = 0

        for face in self.faces:
            normal = face.getNormalByVert(self)
            if not normal is None:
                x = x + normal.x
                y = y + normal.y
                z = z + normal.z
                num = num + 1

        if num is None:
            raise ValueError("Normal is None")

        self.calculatedNormal = _Normal(-1, x / num, y / num, z / num)
        return self.calculatedNormal

    def addFace(self, face):
        self.faces.append(face)

    def __str__(self):
        return "{VERTEX: " + str(round(self.x,4)) + " " + str(round(self.y,4)) + " " + str(round(self.z,4)) + "}"


class _Normal():

    def __init__(self, normalIndex, x, y, z):

        self.index = normalIndex

        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return "{NORMAL: " + str(round(self.x,4)) + " " + str(round(self.y,4)) + " " + str(round(self.z,4)) + "}"

class _Face():

    def __init__(self, faceIndex, vert1, vert2, vert3, normal1, normal2, normal3):

        self.index = faceIndex

        self.vertex1 = vert1
        self.vertex2 = vert2
        self.vertex3 = vert3

        self.normal1 = normal1
        self.normal2 = normal2
        self.normal3 = normal3

        self.indicatedAverageNormal = None

        if (not normal1 is None) and (not normal2 is None) and (not normal3 is None):

            x = (normal1.x + normal2.x + normal3.x) / 3
            y = (normal1.y + normal2.y + normal3.y) / 3
            z = (normal1.z + normal2.z + normal3.z) / 3

            self.indicatedAverageNormal = _Normal(-1, x, y, z)

        self.vertex1.addFace(self)
        self.vertex2.addFace(self)
        self.vertex3.addFace(self)

    def getFaceNormal(self):

        return self.indicatedAverageNormal

    def getNormalByVert(self, vertex):

        if vertex == self.vertex1:
            return self.normal1

        if vertex == self.vertex2:
            return self.normal2

        if vertex == self.vertex3:
            return self.normal3

        return None

    def recalculateNormal(self):

        # TODO: Calculate the face normal from vertex positions. The approach with 
        # using the indicated face normal will only work when using an unmodified
        # wavefront obj loaded from a file that had normals specified, which 
        # isn't required.


class Wavefront():

    def __init__(self, path):

        self.vertices = []
        self.faces = []        
        self.normals = []

        self._vertexAndNormalArray = None
        self._faceArray = None
        self._detachedTris = None
        
        if not os.path.exists(path):
            raise IOError(path + " does not exist")

        self.content = []

        with open(path,'r') as file:
            self.content = file.readlines()

        # Make a first sweep for vertices and normals, as faces need that information

        vertexIndex = 0
        normalIndex = 0

        for line in self.content:

            strippedLine = line.strip()

            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]

                    if command == "v":
                        self._parse_vertex(vertexIndex, parts)
                        vertexIndex = vertexIndex + 1

                    if command == "vn":
                        self._parse_normals(normalIndex, parts)
                        normalIndex = normalIndex + 1

        # Make a second sweep for faces

        faceIndex = 0;

        for line in self.content:

            strippedLine = line.strip()

            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]

                    if command == "f":
                        self._parse_face(faceIndex, parts)
                        faceIndex = faceIndex + 1

        for vertex in self.vertices:
            vertex.recalculateNormal()


    def _parse_vertex(self, vertexIndex, parts):
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        vertex = _Vertex(vertexIndex, x, y, z)
        self.vertices.append(vertex)

    def _parse_normals(self, normalIndex, parts):
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        normal = _Normal(normalIndex, x, y, z)
        self.normals.append(normal)

    def _parse_face(self, faceIndex, parts):

        # Wavefront lists starts at 1, not 0

        vInfo1 = parts[1].split('/')
        vInfo2 = parts[2].split('/')
        vInfo3 = parts[3].split('/')

        vidx1 = int(vInfo1[0]) - 1
        vidx2 = int(vInfo2[0]) - 1
        vidx3 = int(vInfo3[0]) - 1

        vertex1 = self.vertices[vidx1]
        vertex2 = self.vertices[vidx2]
        vertex3 = self.vertices[vidx3]

        tidx1 = None
        tidx2 = None
        tidx3 = None

        nidx1 = None
        nidx2 = None
        nidx3 = None

        normal1 = None
        normal2 = None
        normal3 = None
        
        # Extract normals from information, if at all set

        if len(vInfo1) > 2:
            nidx1 = int(vInfo1[2]) - 1
            normal1 = self.normals[nidx1]

        if len(vInfo2) > 2:
            nidx2 = int(vInfo2[2]) - 1
            normal2 = self.normals[nidx2]

        if len(vInfo3) > 2:
            nidx3 = int(vInfo3[2]) - 1
            normal3 = self.normals[nidx3]

        face = _Face(faceIndex, vertex1, vertex2, vertex3, normal1, normal2, normal3)
        self.faces.append(face)

    def getVertexArray(self):
        return None

    def getVertexAndNormalArray(self):

        if self._vertexAndNormalArray is not None:
            return self._vertexAndNormalArray

        data = []

        l = len(self.vertices)
        i = 0        

        while i < l:
            vertex = self.vertices[i]
            normal = vertex.calculatedNormal

            data.append(vertex.x)
            data.append(vertex.y)
            data.append(vertex.z)
            data.append(normal.x)
            data.append(normal.y)
            data.append(normal.z)
            i = i + 1

        self._vertexAndNormalArray = array.array('f',data)
        return self._vertexAndNormalArray

    def getFaceArray(self):

        if self._faceArray is not None:
            return self._faceArray

        data = []

        for f in self.faces:
            data.append(f.vertex1.index)
            data.append(f.vertex2.index)
            data.append(f.vertex3.index)

        self._faceArray = array.array('H',data)
        return self._faceArray

    def debugVertices(self):

        for vertex in self.vertices:

            print(str(vertex) + " " + str(vertex.calculatedNormal))

            for face in vertex.faces:

                print("  " + str(face.indicatedAverageNormal) )
