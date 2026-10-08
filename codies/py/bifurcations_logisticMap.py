import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sp

### Input parameters
n = 2000  # Number of tested lambdas
N = 1000  # Number of iterations for each lambda
# Boundaries of lambda
lam_min = 0
lam_max = 4


def map(x, lam):
    return lam * x * (1 - x)
    # return lam / 4 * np.sin(x * np.pi)


###
def iterate(lam, init, N):
    l = np.zeros(N)
    l[0] = init
    i = 1
    while i < N:
        l[i] = map(l[i - 1], lam)
        i = i + 1
    return l


def isolate(l, epsilon, tol=10):
    m = [l[-1]]
    i = 2
    while i < tol:
        marker = 0
        for k in m:
            if l[-i] < k + epsilon and l[-i] > k - epsilon:
                marker = 1
        if marker == 0:
            m.append(l[-i])
        i = i + 1
    return m


initial = 0.6
epsilon = 0.01
lams = np.linspace(lam_min, lam_max, n)

out = list()
for lam in lams:
    m = isolate(iterate(lam, initial, N), epsilon)
    u = lam * np.ones(len(m))
    out = out + list(zip(u, m))
out2 = np.transpose(np.array([list(q) for q in out]))

f = plt.figure()

plt.scatter(out2[0], out2[1], s=0.1)
plt.plot([3.56995, 3.56995], [0, 1], "-r")

plt.xlabel(r"$\lambda$")
plt.ylabel(r"$x^*$, stable")
plt.ylim([0, 1])
plt.grid()

plt.show()
# plt.savefig("images/3.2_bifurcations.png", dpi=300)
