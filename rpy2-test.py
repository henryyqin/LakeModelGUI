import numpy as np

import csv
from numpy import genfromtxt
from rpy2.robjects import *
from rpy2.robjects import FloatVector
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
# require rpy2 installed

# test
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()

import lake_obs_bchron2 as bchron

data = genfromtxt('TEX86_cal.csv',
                  delimiter=',',
                  names=True,
                  dtype=None
                  # mask module may be used when better understood
                  #,usemask=True
                  )

# example input file: user have to provide their own input

year = data['AGE']
depth = data['DP']
sds = data['SD']

r = robjects.r  # robjective
calCurves = np.repeat('normal', len(year))

nyears = year[-1]  # that should fixed from the input
d = depth[-1]   # same as H in the sendimentation.

ages = FloatVector(year)    # age estimate
sd = FloatVector(sds)  # SD of ages
positions = FloatVector(depth)     # position in core in cm
calCurves = StrVector(calCurves)
# note d= total depth of core (60cm)
predictPositions = r.seq(0, d, by=d / nyears)
# Specify extractDate (top-most age of the core, in years BP. 1950=0BP)
extractDate = year[0]

# Call BCHRON observation model to return CHRONS (in years BP)

# NOTE: long run time waming
chronBP, depth_horizons = bchron.chron(
    ages, sd, positions, calCurves, predictPositions, extractDate)


# recast in years CE
# chronCE = np.flipud(1950 - chronBP).transpose()

r.pdf("sampleplot")
r.plot(chronBP, main="Tanganyika Age Uncertainties, LGM-Present",
       xlab='Age (cal years BP)', ylab='Depth (mm)', las=1)
r["dev.off"]()
"""
# PLOT IT OUT
sns.set(style='whitegrid', palette='Set2')
x = depth_horizons * 10
ax = plt.axes()
f2 = plt.figure(figsize=(10, 8))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.get_xaxis().tick_bottom()
"""
