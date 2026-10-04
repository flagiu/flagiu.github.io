import numpy as np
import scipy.integrate as intg

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import sys

class AztecDiamond:
    # The configuration of an AztecDiamond of size n (linear extension is 2*n)
    #  is encoded in the self.dual array, with shape (N,3), where N is the
    #  number of points, each with:
    #   x,y: cartesian coordinates;
    #   e: edge code;
    # Edge encoding is: 0 1 2 3 4 5 6
    #  0,1,2,3: 1 right,top,left,bottom edge
    #  4,5    : 2 right-left or top-bottom edges
    #  6      : 0 edges
    # and matters only for ACTIVE dual points (see self.cell_isActive()).
    # The Aztec diamond is grown starting from n=1 up to a desired n. 

    def get_random_edge(self):
        code = 4 if np.random.rand()<0.5 else 5
        return code
    
    def __init__(self, debug=False):
        self.debug = debug
        self.n = 1
        # a 2x2 square grid of points (not necessary)
        #self.points = np.array([[0,0],[1,0],[1,1],[0,1]])
        # its dual is the central point, embedded with the edge feature
        self.dual = np.array([[1/2,1/2,self.get_random_edge()]])
        self.dual_border_length = len(self.dual)
        #self.points_border_length = len(self.points)
        return
    
    def cell_isActive(self, x,y):
        n = self.n
        #cells with different parity of n are active
        return (int(np.abs(x-1/2) + np.abs(y-1/2) - n)%2 == 1)

    def get_equivalent_points(self, points):
        # symmetry equivalent by rotations of pi/4 * k (k=1,2,3) around (1/2,1/2)
        assert len(points.shape)==2 # Nx2 (points) or Nx3 (dual points + edge)
        N = points.shape[0]
        symmetrized_points = np.empty((4*N,points.shape[1]))
        symmetrized_points[:N] = points.copy()
        for k in [1,2,3]:
            # rotation by pi/4 around (1/2, 1/2)
            symmetrized_points[k*N:(k+1)*N, 0] = symmetrized_points[(k-1)*N:k*N, 1]
            symmetrized_points[k*N:(k+1)*N, 1] = 1-symmetrized_points[(k-1)*N:k*N, 0]
        return symmetrized_points

    def update_edge(self, eRig,eTop,eLef,eBot):
        # local dynamic rule to update the edges from neighboring dual cells
        #  0,1,2,3: 1 right,top,left,bottom edge
        #  4,5    : 2 right-left or top-bottom edges
        #  6      : 0 edges
        right=( not eRig is None and eRig in [2,4])
        top=(   not eTop is None and eTop in [3,5])
        left=(  not eLef is None and eLef in [0,4])
        bottom=(not eBot is None and eBot in [1,5])
        if   right and not top and not left and not bottom:
            code=0
        elif not right and top and not left and not bottom:
            code=1
        elif not right and not top and left and not bottom:
            code=2
        elif not right and not top and not left and bottom:
            code=3
        elif right and not top and left and not bottom:
            code=4
        elif not right and top and not left and bottom:
            code=5
        elif not right and not top and not left and not bottom:
            code=6
        else:
            print("Error: unpredicted configuration of neighbor edges")
            sys.exit(1)
        return code

    def evolve_edge(self, code):
        # local dynamic rule to move edges around a dual cell
        if code==0:
            return 2
        elif code==2:
            return 0
        elif code==1:
            return 3
        elif code==3:
            return 1
        elif code==4 or code==5:
            return 6
        elif code==6:
            return self.get_random_edge()

    def update_and_evolve_edges(self):
        #n = int(1/2 + dual.T[0].max())
        dual = self.dual # update in-place
        # update status of non-active cells
        # first: build a coordinate dictionary
        edgeAt={}
        for i in range(len(dual)):
            x,y,edge = dual[i]
            edgeAt[(x,y)] = edge
        # update active cells' (i.e. new border cells or former
        #  Inactive cells) status from their neighbors
        for i in range(len(dual)):
            x,y,edge = dual[i]
            if self.cell_isActive(x,y):
                try:
                    eRig = edgeAt[(x+1,y)]
                except KeyError:
                    eRig = None
                try:
                    eTop = edgeAt[(x,y+1)]
                except KeyError:
                    eTop = None
                try:
                    eLef = edgeAt[(x-1,y)]
                except KeyError:
                    eLef = None
                try:
                    eBot = edgeAt[(x,y-1)]
                except KeyError:
                    eBot = None
                dual[i,2] = self.update_edge(eRig, eTop, eLef, eBot)
        # evolve active edges
        for i in range(len(dual)):
            x,y,edge = dual[i]
            if self.cell_isActive(x,y):
                dual[i,2] = self.evolve_edge(edge)
        return

    def grow(self):
        print(f"Growing n from {self.n} to {self.n+1} ...",end='')
        self.n += 1
        xob = 1/2 if self.n>2 else 0 #at first iteration, include the central dual point (xob=0)
        add_to_dual = []
        #add_to_points = [] #not necessary
        for i in range(self.dual_border_length):
            xo,yo,eo = self.dual[-1-i] #run along the last dual points: the border of n-1
            if xo>xob and yo>0: #use pi/4 rotation symmetry around (1/2,1/2)
                if yo==1/2: # the most eastern tile: extend also along x
                    add_to_dual.append( [xo+1,yo, -1] ) #put a foo -1 edge
                    #add_to_points += [[xo+1+1/2,yo-1/2],[xo+1+1/2,yo+1/2]] # 2 corners of the dual square
                #other tiles: extend only along y
                if self.n>2:
                    add_to_dual.append( [xo,yo+1, -1] ) #put a foo -1 edge
                    #add_to_points.append( [xo+1/2,yo+1+1/2] ) # 1 corner of the dual square
        add_to_dual = self.get_equivalent_points(np.array(add_to_dual)) #get symmetry-equivalent points
        self.dual_border_length = len(add_to_dual)
        self.dual = np.concatenate([self.dual, add_to_dual])
        #add_to_points = self.get_equivalent_points(np.array(add_to_points)) #get symmetry-equivalent points
        #self.points_border_length = len(add_to_points)
        #self.points = np.concatenate([self.points, add_to_points])
        self.update_and_evolve_edges()
        print(" done")
        return

    def grow_upto_n(self, n):
        while self.n < n:
            self.grow()
        return

    def plot_edges_lines(self, ax, draw_squares=False):
        dual = self.dual
        n = int(1/2 + dual.T[0].max())
        for i in range(dual.shape[0]):
            x,y,edge = dual[i]
            if self.cell_isActive(x,y,n):
                if draw_squares:
                    rect = Rectangle((x-1/2,y-1/2),1,1,fc='gray',ec='none',zorder=-1)
                    ax.add_patch(rect)
            else:
                if draw_squares:
                    rect = Rectangle((x-1/2,y-1/2),1,1,fc='lightgray',ec='none',zorder=-1)
                    ax.add_patch(rect)
                continue #draw only the boundaries of active cells!
            if edge==6: #no edge
                continue
            elif edge<4:
                if edge==0: #right
                    line = [[x+1/2,x+1/2],[y-1/2,y+1/2]]
                elif edge==1: # top
                    line = [[x-1/2,x+1/2],[y+1/2,y+1/2]]
                elif edge==2: # left
                    line = [[x-1/2,x-1/2],[y-1/2,y+1/2]]
                elif edge==3: # bottom
                    line = [[x-1/2,x+1/2],[y-1/2,y-1/2]]
                ax.plot(*line,'r')
            elif edge==4: #right-left
                line = [[x+1/2,x+1/2],[y-1/2,y+1/2]]
                ax.plot(*line,'r')
                line = [[x-1/2,x-1/2],[y-1/2,y+1/2]]
                ax.plot(*line,'r')
            elif edge==5: #top-bottom
                line = [[x-1/2,x+1/2],[y+1/2,y+1/2]]
                ax.plot(*line,'r')
                line = [[x-1/2,x+1/2],[y-1/2,y-1/2]]
                ax.plot(*line,'r')
        return

    def plot_edges_rectangles(self, ax,
                              colorsRTLB = ("red","blue","green","yellow")):
        dual = self.dual
        cRight,cTop,cLeft,cBottom = colorsRTLB
        for i in range(dual.shape[0]):
            x,y,edge = dual[i]
            if not self.cell_isActive(x,y):
                continue #draw only the boundaries of active cells!
            if edge==6: #no edge
                continue
            elif edge<4:
                if edge==0: #right
                    xy,w,h,c = (x,y-1),1,2,cRight
                elif edge==1: # top
                    xy,w,h,c = (x-1,y),2,1,cTop
                elif edge==2: # left
                    xy,w,h,c = (x-1,y-1),1,2,cLeft
                elif edge==3: # bottom
                    xy,w,h,c = (x-1,y-1),2,1,cBottom
                rect = Rectangle(xy,w,h,fc=c,ec='none')
                ax.add_patch(rect)
            elif edge==4: #right-left
                xy,w,h,c = (x,y-1),1,2,cRight
                rect = Rectangle(xy,w,h,fc=c,ec='none')
                ax.add_patch(rect)
                xy,w,h,c = (x-1,y-1),1,2,cLeft
                rect = Rectangle(xy,w,h,fc=c,ec='none')
                ax.add_patch(rect)
            elif edge==5: #top-bottom
                xy,w,h,c = (x-1,y),2,1,cTop
                rect = Rectangle(xy,w,h,fc=c,ec='none')
                ax.add_patch(rect)
                xy,w,h,c = (x-1,y-1),2,1,cBottom
                rect = Rectangle(xy,w,h,fc=c,ec='none')
                ax.add_patch(rect)
        return

    def plot_edges_nonOverlappingPath(self,ax):
        dual = self.dual
        for i in range(dual.shape[0]):
            x,y,edge = dual[i]
            if not self.cell_isActive(x,y):
                continue #draw only the boundaries of active cells!
            if edge==6: #no edge
                continue
            elif edge<4:
                if edge==0: #right
                    line = [[x, x+1], [y+1/2, y-1/2]]
                elif edge==1: # top
                    continue
                elif edge==2: # left
                    line = [[x-1, x], [y-1/2, y+1/2]]
                elif edge==3: # bottom
                    line = [[x-1, x+1], [y-1/2, y-1/2]]
                ax.plot(*line, 'k-')
            elif edge==4: #right-left
                line = [[x, x+1], [y+1/2, y-1/2]]
                ax.plot(*line, 'k-')
                line = [[x-1, x], [y-1/2, y+1/2]]
                ax.plot(*line, 'k-')
            elif edge==5: #top-bottom
                line = [[x-1, x+1], [y-1/2, y-1/2]]
                ax.plot(*line, 'k-')
        return

    def run(self):
        self.grow()
        return self.dual

###################################################

seed=1234
np.random.seed(seed)
system = AztecDiamond()
