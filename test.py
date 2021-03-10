import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

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
ax = fig.gca(projection='3d')
ax.scatter(x.ravel(),
           y.ravel(),
           z.ravel(),
           s=400,
           c="grey")

ax.scatter(1, 2, 3, s=500, c="blue", marker="h")
ax.scatter(3, 3, 3, s=500, c="blue", marker="h")
plt.show()
