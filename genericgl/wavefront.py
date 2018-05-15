#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import array

class Wavefront():

    def __init__(self, path):

        self.vertices = []
        self.faces = []        
        self.vertexNormals = []

        self._vertexAndNormalArray = None
        self._faceArray = None
        
        if not os.path.exists(path):
            raise IOError(path + " does not exist")

        self.content = []

        with open(path,'r') as file:
            self.content = file.readlines()

        for line in self.content:

            strippedLine = line.strip()

            if not strippedLine is None and not strippedLine == "" and not strippedLine[0] == "#":
                parts = strippedLine.split(' ')
                if len(parts) > 1:
                    command = parts[0]

                    if command == "v":
                        self._parse_vertex(parts)

                    if command == "vn":
                        self._parse_vertex_normals(parts)

                    if command == "f":
                        self._parse_face(parts)


    def _parse_vertex(self,parts):
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        vertex = [x,y,z]
        #print("VERTEX: " + json.dumps(vertex))
        self.vertices.append(vertex)

    def _parse_face(self,parts):

        # Wavefront lists starts at 1, not 0

        v1 = int( parts[1].split('/')[0] ) - 1
        v2 = int( parts[2].split('/')[0] ) - 1
        v3 = int( parts[3].split('/')[0] ) - 1
        face = [v1,v2,v3]
        #print("FACE: " + json.dumps(face))
        self.faces.append(face)

    def _parse_vertex_normals(self,parts):
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        vertexNormal = [x,y,z]
        print("VERTEXNORMAL: " + json.dumps(vertexNormal))
        self.vertexNormals.append(vertexNormal)

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
            normal = self.vertexNormals[i]
            data.append(vertex[0])
            data.append(vertex[1])
            data.append(vertex[2])
            data.append(normal[0])
            data.append(normal[1])
            data.append(normal[2])
            i = i + 1

        self._vertexAndNormalArray = array.array('f',data)
        return self._vertexAndNormalArray

    def getFaceArray(self):

        if self._faceArray is not None:
            return self._faceArray

        data = []

        for f in self.faces:
            data.append(f[0])
            data.append(f[1])
            data.append(f[2])

        self._faceArray = array.array('H',data)
        return self._faceArray


