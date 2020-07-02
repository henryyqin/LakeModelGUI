# ======================================================================================
# Sylvia Dee <sylvia_dee@brown.edu>
# PRYSM
# PSM for Lacustrine Sedimentary Archives
# ARCHIVE MODEL: Compaction of Sediments based on porosity
# Function 'porosity'
# Modified 03/8/2016 <sylvia_dee@brown.edu>
# Modified 04/2/2018 <sylvia@ig.utexas.edu>

import numpy as np

def porosity(depth_profile, phi_0=0.95):
    import numpy as np
    # assuming no excess pore pressure (Pe = 0) and that grain density is constant for quartz:
    z = np.linspace(0, depth_profile, num=100)  # depth, meters
    ps = 2650.  # kg/m^3 (grain density of quartz, valid for most sands/seds)
    pw = 1000.  # kg/m^3
    g = 9.8  # m/s^2 (gravity)
    phi = np.zeros(len(z))
    # phi_0  # surface porosity, set by user (for reference, shale ~ 0.6, 0.3 to 0.5 for sands, 0.2-0.5 for silts and shales)
    k1 = (1 - phi_0) / phi_0
    c = 3.68E-8
    for i in range(len(phi)):
        phi[i] = (np.exp(-c * g * (ps - pw) * z[i])) / (np.exp(-c * g * (ps - pw) * z[i]) + k1)
    return phi, z

def compaction(Sbar, T, phi_0):
    S = Sbar / 1000.  # Sedimentation rate, cm/yr   ** USER
    # Without compaction:
    H = S * T  # meters (DEPTH OF CORE)   ** USER
    h = np.linspace(0, H, num=100)  ## NOTE THAT IF YOU HAVE DEPTH MEASUREMENTS THIS SHOULD BE SPECIFIED HERE
    ## ALTERNATIVELY, ASSUME UNIFORM SPACING / UNIFORM SED LAYER HEIGHTS
    depth_profile = H  # total depth of core
    # porosity of sediments (phi_0) at site (typical value for lake seds = 0.99)
    phi, z = porosity(depth_profile, phi_0)
    # np.save('phi.npy', phi)
    # np.save('z.npy',z)
    # Now adjust the compacted sediment depth scale based on porosity
    h_prime = np.zeros(len(phi))
    for i in range(len(phi)):
        h_prime[i] = h[i] * (1.0 - phi_0) / (1.0 - phi[i])
    return z, phi, h, h_prime
