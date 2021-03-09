import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

sns.set(style='darkgrid')


tic_toc_field = np.zeros((4, 4, 4)).astype(int)

coordArray = np.stack([x for x in np.ndindex(4, 4, 4)])
coordArray = coordArray.reshape(192).reshape(4, 4, 4, 3)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(4):
    ax.scatter(coordArray[i, :, :], coordArray[:, i, :], coordArray[:, :, i], c="black")
plt.show()
