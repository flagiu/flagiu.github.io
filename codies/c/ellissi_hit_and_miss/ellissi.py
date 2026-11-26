import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

x, y, label = np.loadtxt("ellissi.punti.out", unpack=True)
# hit
hx = x[label==1]
hy = y[label==1]
# miss
mx = x[label==0]
my = y[label==0]

with open("ellissi.in","r") as f:
	lines=f.readlines()
	words = lines[0].split(' ')
	a = float(words[0])
	b = float(words[1])
	assert a>=b

ax = plt.subplot(1,1,1, aspect='equal')
ax.add_patch( Ellipse((0,0), 2*a,2*b, 0, fill=False) )
ax.add_patch( Ellipse((0,0), 2*b,2*a, 0, fill=False) )
plt.xlabel('x')
plt.xlabel('y')
plt.grid()
#plt.xlim((-b,b))
#plt.ylim((-b,b))
plt.xlim((-a,a))
plt.ylim((-a,a))

plt.scatter(hx,hy,s=1, alpha=0.7)
plt.scatter(mx,my,s=1, alpha=0.7)

plt.show()
