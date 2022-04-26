import numpy as np
import matplotlib.pyplot as plt




plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
x = [4,4,5,6,3,4,6,7]
y = [3,4,2,5,6,8,3,2]
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.grid()
plt.plot(x, y, marker="o", markersize=20, markeredgecolor="red")
plt.show()
