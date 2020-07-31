# obs_plotter.py


#==========================================================================
# E3. APPLY OBSERVATION MODEL
#==========================================================================
import analytical_error as err
import psm_obs_tiepoint as chron
from rpy2.robjects import FloatVector
from rpy2.robjects.vectors import StrVector
import rpy2.robjects as robjects
import scipy.interpolate as si
from rpy2.robjects.packages import importr
from scipy.stats.mstats import mquantiles
import matplotlib.patches as mpatches
import wwz

r = robjects.r


# apply chronological errors (imaginary U/Th dates)
# =================================================
d = 60.  # total length of core in cm
nyears = t.shape[0]  # number of years
ages = np.array([-55, 0, 55, 72, 105, 124, 145, 189, 236, 266, 304,
                 432, 500, 589, 643, 730, 835, 879, 900, 950])  # "U/Th" ages
sd = np.array([.1, 5, 10, 12, 13, 8, 15, 20, 17, 19, 23, 30, 37,
               27, 40, 50, 43, 60, 40, 34])  # age precision (1SD)
positions = np.array([0, 3, 6, 9, 12, 15, 18, 21, 23, 25, 28,
                      32, 35, 38, 41, 43, 47, 50, 55, 60])  # position in core in cm
nd = len(ages)
# export for R
ages_r = FloatVector(ages)
sd_r = FloatVector(sd)
pos_r = FloatVector(positions)
calCurves = StrVector(['normal' for i in range(nd)])
# note d= total depth of core (60cm)
predictPositions = r.seq(0, d, by=d / nyears)
# Specify extractDate (top-most age of the core, in years BP)
topDate = -55
year_CE = 1950 - np.array(ages)
# Call BCHRON observation model to return CHRONS (in years BP)
chronBP, depth_horizons = chron.Bchron(
    ages_r, sd_r, pos_r, calCurves, predictPositions, topDate)
# recast in years CE
chronCE = np.flipud(1950 - chronBP).transpose()

chronQ = mquantiles(chronCE, prob=[0.025, 0.5, 0.975], axis=1)
nchrons = chronCE.shape[1]


# PLOT IT OUT
sns.set(style='whitegrid', palette='Set2')
x = depth_horizons * 10
ax = plt.axes()
f2 = plt.figure(figsize=(10, 8))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()
# see http://stackoverflow.com/questions/14143092/why-does-matplotlib-fill-between-draw-edgelines-only-on-a-pdf
plt.fill_between(x, chronQ[:, 0], chronQ[:, 2],
                 facecolor='Silver', edgecolor='Silver', lw=0.0)
CI = mpatches.Patch(color='silver')  # create proxy artist for labeling
lbl = ('95\% CI', 'median', 'U/Th dates', 'sample paths')
dat = plt.errorbar(10 * positions, year_CE, 2 * sd, color='Purple', fmt='o')
# that comma is really important !! wouldn't work without it
med, = plt.plot(x, chronQ[:, 1], color='black', lw=3.0)
# plot a few random paths
nl = 10
idx = np.random.randint(nchrons + 1, size=nl)
l = plt.plot(x, chronCE[:, idx], lw=0.5, color='Purple')
lg = plt.legend((CI, med, dat, l[1]), lbl, loc='upper right')
lg.draw_frame(False)
plt.grid(axis='y')
plt.ylim(900, 2020)
plt.xlim(0, 600)
plt.xlabel(r'Depth (mm)', fontsize=14)
plt.ylabel(r'Year (CE)', fontsize=14)
plt.title(r'Borneo BChron sampling paths, 20 (imaginary) dates', fontsize=16)
f2.savefig('../figs/Borneo_synth_BChron.pdf', dpi=300)
