#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import math
import numpy

class Wavefront():

    def __init__(self, path, triangulateQuads = True):

        # These are the arrays we're going to produce, and which might 
        # make sense to manipulate from the outside:

        self.vertexCoords = None  # XYZ coordinated for each vertex
        self.vertexNormals = None # Normal (in XYZ form) for each vertex
        self.faces = None         # Faces, specified by listing indexes for participating vertices

        # These are internal work arrays

        self._rawVertices = []
        self._rawTexCo = []        
        self._rawVertexTexCo = [];
        self._rawFaces = []
        self._vertexBelongsToFaces = None
        self._faceVertCache = None

        self.triangulateQuads = triangulateQuads

        if not os.path.exists(path):
            raise IOError(path + " does not exist")

        self.content = []

        with open(path,'r') as file:
            self.content = file.readlines()

        # self._mode can be:
        #   ONLYTRIS:    The incoming mesh only contains tris (so no need to do anything)
        #   TRIANGULATE: The incoming mesh contains quads (and may contain tris). Triangulate to get only tris.
        #   ONLYQUADS:   The incoming mesh contains only quads. Keep these rather than triangulating

        self._mode = None

        # Check if mesh contains quads and/or tris
        self._scanForMode()

        # Make a sweep for vertices as faces need that information
        self._extractVertices()

        # Make a sweep for texture coordinates, as faces need that too
        self._extractTextureCoordinates()

        # Make a sweep for faces
        self._extractFaces()

        # TODO: Find texture coordinates for vertices

        # create numpy arrays to contain vertices, faces and normals
        self._createVerticesNumpyArray()
        self._createFacesNumpyArray()

        # These two operations need to be redone if vertex coordinates
        # are changed
        self.recalculateFaceNormals()
        self.recalculateVertexNormals()

    def _scanForMode(self):

        containsTris = False
        containsQuads = False

        for line in self.content:
            strippedLine = line.strip()
            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 4:
                    containsQuads = True
                if len(parts) == 4:
                    containsTris = True
                if len(parts) > 5:
                    raise ValueError("Found a face with more than four vertices. N-gons are not supported.")
                # TODO: Check for n-gons?

        if containsQuads:
            if self.triangulateQuads:
                self._mode = "TRIANGULATE"
            else:
                if containsTris:
                    raise ValueError("Since the mesh contains both tris and quads, requesting the mesh to not be triangulated is illegal")
                else:
                    self._mode = "ONLYQUADS"
        else:
            if containsTris:
                self._mode = "ONLYTRIS"
            else:
                raise ValueError("The mesh didn't contain tris nor quads!?")

        if self._mode == "ONLYQUADS":
            raise ValueError("The ONLYQUADS mode is not implemented yet")

        print("Tris " + str(containsTris))
        print("Quads " + str(containsQuads))
        print(self._mode)
    

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
                        self._rawVertexTexCo.append([0,0])


    def _extractTextureCoordinates(self):

        self.hasTexCo = False

        for line in self.content:
            strippedLine = line.strip()
            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]
                    if command == "vt":
                        x = float(parts[1])
                        y = float(parts[2])
                        texco = [x, y]
                        self._rawTexCo.append(texco)


    def _distanceBetweenVerticesByIdx(self, idx1, idx2):

        vert1 = numpy.array(self._rawVertices[idx1])
        vert2 = numpy.array(self._rawVertices[idx2])    

        difference = vert2 - vert1

        x = difference[0]
        y = difference[1]
        z = difference[2]

        distance = math.sqrt( x*x + y*y + z*z )
        return distance


    def _extractFaces(self):

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

                        # Find indexes of vertices making up the face. Note "-1" since wavefront indexes start
                        # at 1 rather than 0
                        vidx1 = int(vInfo1[0]) - 1
                        vidx2 = int(vInfo2[0]) - 1
                        vidx3 = int(vInfo3[0]) - 1
                        
                        if len(parts) == 4:
                            if self._mode == "ONLYQUADS":
                                raise ValueError("Found tri although mode was ONLYQUADS")
                            face = [vidx1, vidx2, vidx3]
                            self._rawFaces.append(face)
                        else:
                            vInfo4 = parts[4].split('/')
                            vidx4 = int(vInfo4[0]) - 1
                            if self._mode == "ONLYTRIS":
                                raise ValueError("Found quad although mode was ONLYTRIS")
                            if self._mode == "ONLYQUADS":
                                raise ValueError("ONLYQUADS mode not implemented yet")

                            # Perform triangulation by splitting quad into two tris, using the shortest diagonal
                            distance13 = self._distanceBetweenVerticesByIdx(vidx1, vidx3)
                            distance24 = self._distanceBetweenVerticesByIdx(vidx2, vidx4)

                            if distance13 > distance24:
                                face = [vidx1, vidx2, vidx4]
                                self._rawFaces.append(face)
                                face = [vidx3, vidx4, vidx2]
                                self._rawFaces.append(face)
                            else:
                                face = [vidx1, vidx3, vidx4]
                                self._rawFaces.append(face)
                                face = [vidx2, vidx3, vidx1]
                                self._rawFaces.append(face)

                        i = 1
                        while i < len(parts):

                            f = parts[i].split('/')
                            if len(f) > 1:
                                vidx = int(f[0]) - 1 # Vertex index
                                tidx = int(f[1]) - 1 # Texture coordinate index

                                texco = self._rawTexCo[tidx] # Actual texture coordinats, x/y

                                #print("TEXCO: " + str(i) + " " + str(tidx) + " " + str(texco))
                                self._rawVertexTexCo[vidx] = texco

                                self.hasTexCo = True

                            i = i + 1


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

        if numberOfVertices != len(self._rawVertexTexCo):
            raise ValueError("Not same number of elements in texco array")

        # Convert raw coords from wavefront into a 2d numpy array
        self.vertexCoords = numpy.array( self._rawVertices, dtype=float )

        # Create a two-dimensional float array with shape (numVerts/3) and 
        # fill it with zeros. This will contain vertex normals.
        self.vertexNormals = numpy.zeros( (numberOfVertices, 3), dtype=float )

        # Create a two-dimensional float array with shape (numVerts/2) and 
        # fill it with texture coordinates. 
        self.vertexTexCo = numpy.array( self._rawVertexTexCo, dtype=float )

    


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

        zeroNormal = numpy.array([0.0, 0.0, 0.0], dtype=float)

        while currentVert < numberOfVertices:
            faces = self._vertexBelongsToFaces[currentVert]
            numberOfFaces = len(faces)
            currentNormal = numpy.array([0,0,0], dtype=float)
            currentFace = 0
            firstNormal = None
            while currentFace < numberOfFaces:
                fidx = faces[currentFace]
                fnormal = self.faceNormals[fidx]
                if firstNormal is None:
                    firstNormal = fnormal
                currentNormal = currentNormal + fnormal
                currentFace = currentFace + 1
            if numberOfFaces < 1:
                raise ValueError("Found a vertex (" + str(currentVert) + ") which did not belong to any face")

            averageNormal = currentNormal / numberOfFaces

            if numpy.array_equal(averageNormal, zeroNormal):
                print("WARNING: found zero vertex normal for vertex " + str(currentVert))
                averageNormal = firstNormal

            self.vertexNormals[currentVert] = self._unitVector(averageNormal)

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

            cross = numpy.cross(U,V)
            N = self._unitVector(cross)

            self.faceNormals[currentFace] = N
            currentFace = currentFace + 1


    def _unitVector(self, normal):

        # There is probably a numpy version of doing this calculation 

        x = normal[0] * normal[0]
        y = normal[1] * normal[1]
        z = normal[2] * normal[2]

        magnitude = math.sqrt(x + y + z)

        if magnitude == 0.0:
            print("\nINVALID MAGNITUDE:\n")
            print("Normal was: " + str(normal))
            raise ValueError("Invalid magnitude")
            sys.exit(1)

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

    def getVertexAndNormalAndTexCoArray(self):
        # This should possibly be cached
        return numpy.hstack( (self.vertexCoords, self.vertexNormals, self.vertexTexCo) )


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



