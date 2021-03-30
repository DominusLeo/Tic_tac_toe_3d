import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D


# Make this bigger to generate a dense grid.
N = 4

# Create some random data.
volume = np.zeros((4, 4, 4)).astype(int)

# Create the x, y, and z coordinate arrays.  We use
# numpy's broadcasting to do all the hard work for us.
# We could shorten this even more by using np.meshgrid.
x = np.arange(volume.shape[0])[:, None, None] + 1
y = np.arange(volume.shape[1])[None, :, None] + 1
z = np.arange(volume.shape[2])[None, None, :] + 1
x, y, z = np.broadcast_arrays(x, y, z)

# Turn the volumetric data into an RGB array that's
# just grayscale.  There might be better ways to make
# ax.scatter happy.
c = np.tile(volume.ravel()[:, None], [1, 3])
# if

# Do the plotting in a single call.

fig = plt.figure()
ax = Axes3D(fig)

plt.xticks(np.arange(1, 5, 1))
plt.yticks(np.arange(1, 5, 1))

ax.set_zticks(np.arange(1, 5, 1))

ax.scatter(x.ravel(),
           y.ravel(),
           z.ravel(),
           s=100,
           c="grey", linewidths=2)

plt.xlabel("x axis", fontsize=10, rotation=1)
plt.ylabel("y axis", fontsize=10, rotation=1)
ax.set_zlabel('z axis', fontsize=10, rotation=1)
# plt.zlabel("z axis")
# ax.scatter(1, 2, 3, s=500, c="blue", marker="h")
plt.show()
# input("1")
# ax.scatter(3, 3, 3, s=500, c="blue", marker="h")
# plt.show()
# input("2")
# ax.scatter(3, 3, 3, s=500, c="green", marker="h")
# plt.show()

# input("1")
# input("2")
