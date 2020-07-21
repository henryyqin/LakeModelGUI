import numpy as np
from rpy2.robjects import FloatVector
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
import matplotlib.pyplot as plt


utils = importr("utils")
utils.chooseCRANmirror(ind=1)
packnames = ('Bchron', 'stats', 'graphics')
utils.install_packages(StrVector(packnames))
Bchron = importr('Bchron')
r = robjects.r
data = np.genfromtxt('TEX86_cal.csv', delimiter=',', names=True, dtype=None)
year = data['AGE']
depth = data['DP']
sds = data['SD']
calCurves = np.repeat('normal', len(year))
nyears = year[-1]
d = depth[-1]
ages = FloatVector(year)
sd = FloatVector(sds)
positions = FloatVector(depth)
calCurves = StrVector(calCurves)
predictPositions = r.seq(0, d, by=d / nyears)
extractDate = year[0]
ages = Bchron.Bchronology(ages=ages, ageSds=sd, positions=positions,
                          calCurves=calCurves, predictPositions=predictPositions, extractDate=extractDate)
theta = ages[0]
theta = np.array(theta)
thetaPredict = ages[4]
thetaPredict = np.array(thetaPredict)
depths = np.array(predictPositions)
depth_horizons = depths[:-1]
chrons = thetaPredict[:, :-1]
# Plot the Ages and the 5,95% CI as a check (optional)


chronsQ = np.quantile(chrons.transpose(), [0.025, 0.5, 0.975], axis=1)


fig, ax = plt.subplots()
plt.fill_betweenx(depth_horizons, chronsQ[0], chronsQ[2],
                  facecolor='Silver', edgecolor='Silver', lw=0.0)
ax.plot(chronsQ[1], depth_horizons, color="black", lw=0.75)
ax.scatter(data['AGE'], data['DP'], marker="s")
ax.set_xlim(50000, 0)
ax.set_ylim(650, -50)
ax.set_xlabel('Age (cal years BP)')
ax.set_ylabel('Depth (mm)')
plt.savefig('line_plot.pdf')
"""
r.plot(chrons[0], depth_horizons, main="Tanganyika Age Uncertainties, LGM-Present", xlim=r.c(45000,
                                                                                             0), ylim=r.c(600, 0), xlab='Age (cal years BP)', ylab='Depth (mm)', las=1, lwd=1, col="blue")
for i in range(1, 1000):
	print(i)
	r.lines(chrons[i], depth_horizons, lwd=1, col="blue")
# r.plot(chrons[0], depth_horizons, main="Tanganyika Age Uncertainties, LGM-Present", xlim = r.c(45000,0),ylim = r.c(600,0),xlab='Age (cal years BP)', ylab='Depth (mm)', las=1)
r["dev.off"]()
"""
