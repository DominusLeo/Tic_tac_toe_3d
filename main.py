import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

sns.set(style='darkgrid')


class myarray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(myarray)

    def index(self, value):
        return np.where(self == value)


tic_toc_field = np.zeros((4, 4, 4)).astype(int)
# coordinates = np.array(np.meshgrid([0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2]))
# coordList = [x for x in np.ndindex(4, 4, 4)]
coordArray = np.stack([x for x in np.ndindex(4, 4, 4)])
coordArray = coordArray.reshape(192).reshape(4, 4, 4, 3)
# for i in range(3):
#     for ii in range(3):
#         for iii in range(3):
#             coordinates[i, ii, iii]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(coordArray[0, :, :], coordArray[1, :, :], coordArray[2, :, :])
plt.show()
