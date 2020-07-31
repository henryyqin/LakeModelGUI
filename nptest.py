import numpy as np

a = [1, 2, 3]
b = [4, 5, 6]



data = np.array([a, b]).T

print(data)

fmt = ",".join(["%s"] * (data.shape[1]-1))
np.savetxt("temp.csv", data, fmt=fmt, header="x,y", comments='', delimiter=',')
