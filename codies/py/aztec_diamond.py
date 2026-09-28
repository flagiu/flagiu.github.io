import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import sys


def cell_isActive(x,y,n):
    return (int(np.abs(x-1/2) + np.abs(y-1/2) - n)%2 == 1) #cells with different parity of n are active

def get_equivalent_points(points):
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

def generate_dual_and_real(n):
    if n<1:
        print("Error: n must be a positive integer")
        sys.exit(1)
    elif n==1:
        dual = np.array([[1/2,1/2]])
        points = np.array([[0,0],[1,0],[1,1],[0,1]])
        dual_border_length = len(dual)
        points_border_length = len(points)
        return dual,points,dual_border_length,points_border_length
    else:
        dual,points,dual_border_length,points_border_length = generate_dual_and_real(n-1)
        xob = 1/2 if n>2 else 0 #at first iteration, include the central dual point (xob=0)
        add_to_dual = []
        add_to_points = []
        for i in range(dual_border_length):
            xo,yo = dual[-1-i] #run along the last dual points: the border of n-1
            if xo>xob and yo>0: #use pi/4 rotation symmetry around (1/2,1/2)
                if yo==1/2: # the most eastern tile: extend also along x
                    add_to_dual.append( [xo+1,yo] )
                    add_to_points += [[xo+1+1/2,yo-1/2],[xo+1+1/2,yo+1/2]] # 2 corners of the dual square
                #other tiles: extend only along y
                add_to_dual.append( [xo,yo+1] )
                add_to_points.append( [xo+1/2,yo+1+1/2] ) # 1 corner of the dual square
        add_to_dual = get_equivalent_points(np.array(add_to_dual)) #get symmetry-equivalent points
        add_to_points = get_equivalent_points(np.array(add_to_points)) #get symmetry-equivalent points
        dual_border_length,points_border_length = len(add_to_dual), len(add_to_points)
        dual = np.concatenate([dual, add_to_dual])
        points = np.concatenate([points, add_to_points])
        return dual,points, dual_border_length,points_border_length

#Dual shape: (N,3) with x,y,e coordinates: 2D cartesian + edge code
# Edge encoding around an active dual point: 0 1 2 3 4 5 6
#  0,1,2,3: 1 right,top,left,bottom edge
#  4,5    : 2 right-left or top-bottom edges
#  6      : 0 edges
def plot_edges_lines(ax,dual, draw_squares=False):
    assert len(dual.shape)==2
    assert dual.shape[1]==3
    n = int(1/2 + dual.T[0].max())
    for i in range(dual.shape[0]):
        x,y,edge = dual[i]
        if cell_isActive(x,y,n):
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

def plot_edges_rectangles(ax,dual):
    cRight,cTop,cLeft,cBottom = "red","blue","green","yellow"
    assert len(dual.shape)==2
    assert dual.shape[1]==3
    n = int(1/2 + dual.T[0].max())
    for i in range(dual.shape[0]):
        x,y,edge = dual[i]
        if not cell_isActive(x,y,n):
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

def plot_edges_nonOverlappingPath(ax,dual):
    assert len(dual.shape)==2
    assert dual.shape[1]==3
    n = int(1/2 + dual.T[0].max())
    for i in range(dual.shape[0]):
        x,y,edge = dual[i]
        if not cell_isActive(x,y,n):
            continue #draw only the boundaries of active cells!
        if edge==6: #no edge
            continue
        elif edge<4:
            if edge==0: #right
                line = [[x, x+1], [y-1/2, y+1/2]]
            elif edge==1: # top
                continue
            elif edge==2: # left
                line = [[x-1, x], [y+1/2, y-1/2]]
            elif edge==3: # bottom
                line = [[x-1/2, x+1/2], [y-1/2, y-1/2]]
            ax.plot(*line, 'k-')
        elif edge==4: #right-left
            line = [[x, x+1], [y-1/2, y+1/2]]
            ax.plot(*line, 'k-')
            line = [[x-1, x], [y+1/2, y-1/2]]
            ax.plot(*line, 'k-')
        elif edge==5: #top-bottom
            line = [[x-1/2, x+1/2], [y-1/2, y-1/2]]
            ax.plot(*line, 'k-')
    return

def get_random_edge():
    if np.random.rand()<0.5:
        code=4
    else:
        code=5
    return code

def update_edge(eRig,eTop,eLef,eBot):
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

def evolve_edge(code):
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
        return get_random_edge()

def update_and_evolve_edges(dual):
    n = int(1/2 + dual.T[0].max())
    # update status of non-active cells
    # first: build a coordinate dictionary
    edgeAt={}
    for i in range(len(dual)):
        x,y,edge = dual[i]
        edgeAt[(x,y)] = edge
    # update active cells' (i.e. new border cells or former Inactive cells) status from their neighbors
    for i in range(len(dual)):
        x,y,edge = dual[i]
        if cell_isActive(x,y,n):
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
            dual[i,2] = update_edge(eRig, eTop, eLef, eBot)
    # evolve active edges
    for i in range(len(dual)):
        x,y,edge = dual[i]
        if cell_isActive(x,y,n):
            dual[i,2] = evolve_edge(edge)
    return


def generate_dual_and_real_and_edges(n):
    if n<1:
        print("Error: n must be a positive integer")
        sys.exit(1)
    elif n==1:
        dual = np.array([[1/2,1/2,get_random_edge()]])
        points = np.array([[0,0],[1,0],[1,1],[0,1]])
        dual_border_length = len(dual)
        points_border_length = len(points)
        return dual,points, dual_border_length,points_border_length
    else:
        dual,points,dual_border_length,points_border_length = generate_dual_and_real_and_edges(n-1)
        xob = 1/2 if n>2 else 0 #at first iteration, include the central dual point (xob=0)
        add_to_dual = []
        add_to_points = []
        for i in range(dual_border_length):
            xo,yo,eo = dual[-1-i] #run along the last dual points: the border of n-1
            if xo>xob and yo>0: #use pi/4 rotation symmetry around (1/2,1/2)
                if yo==1/2: # the most eastern tile: extend also along x
                    add_to_dual.append( [xo+1,yo, -1] ) #put a foo -1 edge
                    add_to_points += [[xo+1+1/2,yo-1/2],[xo+1+1/2,yo+1/2]] # 2 corners of the dual square
                #other tiles: extend only along y
                if n>2:
                    add_to_dual.append( [xo,yo+1, -1] ) #put a foo -1 edge
                    add_to_points.append( [xo+1/2,yo+1+1/2] ) # 1 corner of the dual square
        add_to_dual = get_equivalent_points(np.array(add_to_dual)) #get symmetry-equivalent points
        add_to_points = get_equivalent_points(np.array(add_to_points)) #get symmetry-equivalent points
        dual_border_length,points_border_length = len(add_to_dual), len(add_to_points)
        dual = np.concatenate([dual, add_to_dual])
        points = np.concatenate([points, add_to_points])
        update_and_evolve_edges(dual)
        return dual,points, dual_border_length,points_border_length
                

def get_points(n):
    N = 2*n*(n+1) #number of points
    points = np.empty((N,2))
    i=int(0)
    for x in np.arange(-n+1,n+1):
        dx=np.abs(x-1/2)
        for y in np.arange(-n+1,n+1):
            dy=np.abs(y-1/2)
            if dx+dy<=n:
                points[i,0] = x
                points[i,1] = y
                i+=1
    points = np.array(points)
    return points




seed=int(12345)
n=1
if len(sys.argv)>1:
    n=int(sys.argv[1])
    if len(sys.argv)>2:
        seed=int(sys.argv[2])
else:
    print(f"Usage: <n> [seed={seed}]")
    sys.exit(1)
np.random.seed(seed)
#points = get_points(n)
print(f"Generating aztec diamond with n={n}, seed={seed}")
dual,points, dual_border_length,points_border_length = generate_dual_and_real_and_edges(n)

print("Plotting as colored tiles")
fig,ax = plt.subplots(figsize=(8,8), dpi=300)
plot_edges_rectangles(ax, dual)
ax.set(xlim=(-n,n+1), ylim=(-n,n+1))
ax.axis("off")
ax.set(facecolor='none', aspect='equal')
fig.savefig(f"images/aztec_n{n}_seed{seed}.png", bbox_inches='tight', pad_inches=0)

sys.exit()

print("Plotting as NOP")
fig,ax = plt.subplots(figsize=(8,8), dpi=300)
plot_edges_nonOverlappingPath(ax,dual)
ax.set(xlim=(-n,n+1), ylim=(-n,n+1))
ax.axis("off")
ax.set(facecolor='none', aspect='equal')
fig.savefig(f"images/aztec-NOP_n{n}_seed{seed}.png", bbox_inches='tight', pad_inches=0)

sys.exit()

print("Plotting as lines")
fig,ax = plt.subplots(figsize=(8,8), dpi=300)
#ax.scatter(points.T[0],points.T[1], color='k', marker='.')
#ax.scatter(dual.T[0],dual.T[1], color='b', marker='s')
plot_edges_lines(ax, dual, draw_squares=True)
ax.set(xlim=(-n,n+1), ylim=(-n,n+1))
ax.axis("off")
ax.set(facecolor='none', aspect='equal')
fig.savefig(f"images/aztec-lines_n{n}_seed{seed}.png", bbox_inches='tight', pad_inches=0)

#plt.show()

