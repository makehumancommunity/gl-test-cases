#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import math
import numpy

class Wavefront():

    def __init__(self, path):

        # These are the arrays we're going to produce, and which might 
        # make sense to manipulate from the outside:

        self.vertexCoords = None  # XYZ coordinated for each vertex
        self.vertexNormals = None # Normal (in XYZ form) for each vertex
        self.faces = None         # Faces, specified by listing indexes for participating vertices

        # These are internal work arrays

        self._rawVertices = []
        self._rawFaces = []        
        self._vertexBelongsToFaces = None
        self._faceVertCache = None

        if not os.path.exists(path):
            raise IOError(path + " does not exist")

        self.content = []

        with open(path,'r') as file:
            self.content = file.readlines()

        # Make a first sweep for vertices as faces need that information
        self._extractVertices()

        # Make a second sweep for faces
        self._extractFaces()

        # TODO: Find texture coordinates for vertices

        # create numpy arrays to contain vertices, faces and normals
        self._createVerticesNumpyArray()
        self._createFacesNumpyArray()

        # These two operations need to be redone if vertex coordinates
        # are changed
        self.recalculateFaceNormals()
        self.recalculateVertexNormals()


    def _extractVertices(self):
        for line in self.content:
            strippedLine = line.strip()
            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]
                    if command == "v":
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        vertex = [x, y, z]
                        self._rawVertices.append(vertex)


    def _extractFaces(self, assumeQuads = False):

        # Note that wavefront lists starts at 1, not 0

        for line in self.content:
            strippedLine = line.strip()
            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]
                    if command == "f":

                        # Face info is vertIdx / texCoIdx / faceNormalIdx  OR  vertIdx / texCoIdx  OR  vertIdx

                        vInfo1 = parts[1].split('/')
                        vInfo2 = parts[2].split('/')
                        vInfo3 = parts[3].split('/')

                        vInfo4 = None
                        if assumeQuads:
                            vInfo4 = parts[4].split('/')
                
                        # Find indexes of vertices making up the face. Note "-1" since wavefront indexes start
                        # at 1 rather than 0
                        vidx1 = int(vInfo1[0]) - 1
                        vidx2 = int(vInfo2[0]) - 1
                        vidx3 = int(vInfo3[0]) - 1

                        vidx4 = -1
                        if assumeQuads:
                            vidx4 = int(vInfo4[0]) - 1

                        # TODO: Extract texture coordinates

                        if assumeQuads:
                            face = [vidx1, vidx2, vidx3, vidx4]
                        else:
                            face = [vidx1, vidx2, vidx3]

                        self._rawFaces.append(face)


    def _createFacesNumpyArray(self, assumeQuads = False):

        numberOfFaces = len(self._rawFaces)

        vertsPerFace = 3
        if assumeQuads:
            vertsPerFace = 4

        # Create a two-dimensional int array with shape (numFace/vertsPerFace) and 
        # fill it values from the wavefront obj. This will contain vert indices.

        self.faces = numpy.array( self._rawFaces, dtype=int ) # Values will be copied from self._rawFaces

        # Create a two-dimensional float array with shape (numFace/ 3 ) and 
        # fill it with zeros. This will contain faces normals, but needs to
        # be recalculated.

        self.faceNormals = numpy.zeros( (numberOfFaces, 3), dtype=float )


    def _createVerticesNumpyArray(self):

        numberOfVertices = len(self._rawVertices)

        # Convert raw coords from wavefront into a 2d numpy array
        self.vertexCoords = numpy.array( self._rawVertices, dtype=float )

        # Create a two-dimensional float array with shape (numVerts/3) and 
        # fill it with zeros. This will contain vertex normals.
        self.vertexNormals = numpy.zeros( (numberOfVertices, 3), dtype=float )

        # Create a two-dimensional float array with shape (numVerts/2) and 
        # fill it with zeros. This will contain vertex texture coordinates.
        self.vertexTexCo = numpy.zeros( (numberOfVertices, 2), dtype=float )


    def recalculateVertexNormals(self, assumeQuads = False):

        # Build a cache where we, per vertex, list which faces are relevant
        # for it. We need this in order to calculate the vertex normal later,
        # as an average of the face normals surrounding it
        if self._vertexBelongsToFaces is None:

            self._vertexBelongsToFaces = []

            numberOfFaces = len(self.faces)
            numberOfVertices = len(self.vertexCoords)

            vertsPerFace = 3
            if assumeQuads:
                vertsPerFace = 4

            currentVert = 0
            while currentVert < numberOfVertices:
                self._vertexBelongsToFaces.append([])
                currentVert = currentVert + 1 

            currentFace = 0
            while currentFace < numberOfFaces:
                fv = self.faces[currentFace]
                currentVert = 0
                while currentVert < vertsPerFace:
                    vertexIndex = fv[currentVert]
                    self._vertexBelongsToFaces[vertexIndex].append(currentFace)
                    currentVert = currentVert + 1
                currentFace = currentFace + 1
        
        # Calculate vertex normals as an average of the surrounding face
        # normals. 
        currentVert = 0
        while currentVert < numberOfVertices:
            faces = self._vertexBelongsToFaces[currentVert]
            numberOfFaces = len(faces)
            currentNormal = numpy.array([0,0,0], dtype=float)
            currentFace = 0
            while currentFace < numberOfFaces:
                fidx = faces[currentFace]
                fnormal = self.faceNormals[fidx]
                currentNormal = currentNormal + fnormal
                currentFace = currentFace + 1
            self.vertexNormals[currentVert] = self._unitVector(currentNormal / numberOfFaces)

            currentVert = currentVert + 1


    def recalculateFaceNormals(self):

        self._copyVertCoordsToCache()

        # Calculate the face normal from the first three vertices. This might produce 
        # strange results if using quads. In that case we should probably triangulate and
        # and weight together the face normals of the resulting two tris. 
        numberOfFaces = len(self.faces)

        currentFace = 0
        while currentFace < numberOfFaces:

            U = self._faceVertCache[currentFace][1] - self._faceVertCache[currentFace][0]
            V = self._faceVertCache[currentFace][2] - self._faceVertCache[currentFace][0]
            N = self._unitVector(numpy.cross(U,V))
            self.faceNormals[currentFace] = N
            currentFace = currentFace + 1


    def _unitVector(self, normal):

        # There is probably a numpy version of doing this calculation 

        x = normal[0] * normal[0]
        y = normal[1] * normal[1]
        z = normal[2] * normal[2]

        magnitude = math.sqrt(x + y + z)

        return normal / magnitude


    def _copyVertCoordsToCache(self, assumeQuads = False):

        # Create a two-dimensional float array with shape ( numFace / vertsPerFace / 3 ) and 
        # fill it with the coordinates for each vertex participating  in each face
        #
        # This cache is used when recalculating face normals

        numberOfFaces = len(self.faces)

        vertsPerFace = 3
        if assumeQuads:
            vertsPerFace = 4

        if self._faceVertCache is None:
            self._faceVertCache = numpy.zeros( (numberOfFaces, vertsPerFace, 3), dtype=float )

        currentFace = 0
        while currentFace < numberOfFaces:
            currentVertex = 0
            while currentVertex < vertsPerFace:
                vertexIndex = self.faces[currentFace][currentVertex]
                self._faceVertCache[currentFace][currentVertex] = self.vertexCoords[vertexIndex]
                currentVertex = currentVertex + 1
            currentFace = currentFace + 1


    def getVertexArray(self):
        return self.vertexCoords


    def getVertexNormals(self):
        return self.vertexNormals


    def getVertexAndNormalArray(self):
        # This should possibly be cached
        return numpy.hstack( (self.vertexCoords, self.vertexNormals) )


    def getFaceArray(self):
        return self.faces


    def debugVertices(self):

        vertices = self.getVertexAndNormalArray()

        for vertex in vertices:
            out = "["
            for i in vertex:
                out = out + " " + str(round(i,4))
            out = out + " ]"
            print(out)



