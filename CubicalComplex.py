
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 20:17:28 2016

@author: Stefano
"""

import time as t
import pickle
import gzip
import random
import multiprocessing as mp

# Dimesion of cells
DIM_VERTEX = 0
DIM_EDGE = 1
DIM_SQUARE = 2  

class CubicalComplex:
      
    def __init__(self, x, y):
        # Some possible useful data
        self.x = x
        self.y = y
        self.xCells = x*2 + 1
        self.yCells = y*2 + 1
        self.cellsNumber = self.xCells * self.yCells
        self.properSet = {}
        self.createDim()
        self.createNeighboursMap()
        self.createEdgeVertexMap()
     
    def createDim(self):
        # Constructs an array containing the dimension of the elements
        self.dim = [0 for i in range(0, self.cellsNumber)]
        self.dim[0] = DIM_VERTEX
        for i in range(1, self.cellsNumber):
            # Only edge has odd index
            if( i%2 == 1):
                self.dim[i] = DIM_EDGE
            else:
                # Both vertex and square has even index.
                # But vertex are on even index rows
                if( int((i/self.xCells) % 2) == 0):
                    self.dim[i] = DIM_VERTEX
                # Squares are on odd index rows
                else:
                    self.dim[i] = DIM_SQUARE

    def createNeighboursMap(self):
        # Constructs the list of neighbours to whom a cell could connect                
        self.neighbours = {}
        for i in range(0, self.cellsNumber):
            self.neighbours[i] = [] # Squares will have an empty list
            # Vertex has 8 possible connections
            if( self.dim[i] == DIM_VERTEX ):
                # The square on the top-left
                if( 0 <= (i - self.xCells) - 1 
                and self.dim[(i - self.xCells) - 1] == DIM_SQUARE):
                    self.neighbours[i].append( (i - self.xCells) - 1)
                # The edge on the top
                if( 0 <= (i - self.xCells) ):
                    self.neighbours[i].append( i - self.xCells)
                # The square on the top-right
                if( 0 <= (i - self.xCells) + 1 
                and self.dim[(i - self.xCells) + 1] == DIM_SQUARE):
                    self.neighbours[i].append( (i - self.xCells) + 1)
                # The edge on the left (it should be on the same row)
                if( 0 <= (i - 1) 
                and int(i / self.xCells) == int((i-1) / self.xCells)):
                    self.neighbours[i].append( i - 1)
                # The edge on the right (it should be on the same row)
                if( (i + 1) < self.cellsNumber 
                and int(i / self.xCells) == int((i+1) / self.xCells)):
                    self.neighbours[i].append( i + 1)
                # The square on the bottom-left
                if( (i + self.xCells) - 1 < self.cellsNumber 
                and self.dim[(i + self.xCells) - 1] == DIM_SQUARE):
                    self.neighbours[i].append( (i + self.xCells) - 1)
                # The edge on the bottom
                if( 0 <= (i + self.xCells) < self.cellsNumber):
                    self.neighbours[i].append( i + self.xCells)
                # The square on the bottom-right
                if( (i + self.xCells) + 1 < self.cellsNumber
                and self.dim[(i + self.xCells) + 1] == DIM_SQUARE):
                    self.neighbours[i].append( (i + self.xCells) + 1)
            # Each edge has 2 possible connections
            # But as we don't know if it's and horizontal edge or vertical
            # we should check all the 4 possibilities
            elif( self.dim[i] == DIM_EDGE ):
                # Horizontal edge, the square on the top
                if( 0 <= i - self.xCells
                and self.dim[i-self.xCells] == DIM_SQUARE):
                    self.neighbours[i].append( i-self.xCells )
                # Horizontal edge, the square on the bottom
                if( self.cellsNumber > i + self.xCells 
                and self.dim[i+self.xCells] == DIM_SQUARE):
                    self.neighbours[i].append( i+self.xCells )
                # Vertical edge, the square on the left
                if( self.dim[i-1] == DIM_SQUARE):
                    self.neighbours[i].append( i-1 )
                # Vertical edge, the square on the right
                if( self.dim[i+1] == DIM_SQUARE):
                    self.neighbours[i].append( i+1 )
        
    def createEdgeVertexMap(self):
        # Construct a map in which each edge has associated its end vertices
        self.edgeVertex = {}
        for i in range(0, self.cellsNumber):
            if (self.dim[i] == DIM_EDGE):
                self.edgeVertex[i] = []
                if( 0 <= i - self.xCells and self.dim[i-self.xCells] == DIM_VERTEX):
                    self.edgeVertex[i].append(i-self.xCells)
                    self.edgeVertex[i].append(i+self.xCells)
                else:
                    self.edgeVertex[i].append(i-1)
                    self.edgeVertex[i].append(i+1)
                    
                  
    def isProperSet(self, multiVector):
        # Check if the multiVector is a proper set
        # We'll keep trace of the set already checked to improve the performance
        if(tuple(multiVector) not in self.properSet):
            mouth = self.cl(multiVector).difference(multiVector)
            if (mouth == self.cl(mouth)):
                self.properSet[tuple(multiVector)] = True
            else:
                self.properSet[tuple(multiVector)] = False
                
        return self.properSet[tuple(multiVector)]
            

    def cl(self, cells):
        # Define the closure of a set
        closure = set(cells)
        for cell in cells:
            if(self.dim[cell] == DIM_EDGE):
                closure.add(self.edgeVertex[cell][0])
                closure.add(self.edgeVertex[cell][1])
            if(self.dim[cell] == DIM_SQUARE):
                closure.add(cell+1)
                closure.add(cell-1)
                closure.add(cell - self.xCells)
                closure.add(cell - self.xCells - 1)
                closure.add(cell - self.xCells + 1)
                closure.add(cell + self.xCells)
                closure.add(cell + self.xCells + 1)
                closure.add(cell + self.xCells - 1)
        return closure