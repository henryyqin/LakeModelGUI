! Version 1.0
! Declarations ********************************************************
      real dz,dt,readdt,basedep,zo,z_screen,delta,rhowat,rhoice,rhosnow
      real Le,Lei,fusion,surf,fracmin,fraclim,qwtau,cpw_ice,condw,beta
      real snocrit,kv,dm,pi,tsurfp,mixing,trace,depth_begin,salty_begin
      real trace_i,trace_a,d_frac,tempi_a,hice_a,hsnow_a,xlat,xlon,gmt
      real b_area,runout_sum,alb_slush,alb_snow,fsol1,fsol2,sical0,sical1
      real salty_a,eta,fraci_a,temp_a,d_fraca,snowcut,o18air,f,ti_a
      real deutair,dexch,alphak,lamisw,lamilw,ca,cb,c70,c71,c72,c73
      real lamssw,lamslw,afrac1,afrac2,condi,conds,cpair,emis
      real o18snow_a,deutsnow_a,psum_a,surfarea_a,hsnow_ave,temp_ave
      real tsurf_ave,fice_ave,evap_ave,hice_ave,o18_ave,deut_ave
      real oblq,cdrn,raddeg,dpd,grav,sigma,rair,rvap,cvap
      real co18prec,co18run,cdeutprec,cdeutrun,xt,mix_ave

      integer max_dep,ix1,iy1,n_trace,i_area,lcount,nspin
      integer iin,iout,numpts,num_tra,ktau,iupto,ilake,jlake
      integer depth,depth_a,ktauwan,mixmax_a

      logical bndry_flag,iceflag,s_flag,o18flag,deutflag,ar_flag
      logical snow_flag_a,wb_flag,melt_flag_a

!**********************************************************************
! Lake specific parameters ********************************************

      parameter (oblq = 23.4)           ! obliquity
      parameter (xlat = -6.30)          ! latitude (negative for South)
      parameter (xlon = 29.5)           ! longitude (negative for West)
    parameter (oblq = 23.4)   ! obliquity
    parameter (xlat = -6.30)   ! latitude (negative for South)
    parameter (xlon = 29.5)   ! longitude (negative for West)
    parameter (gmt = +3)   ! local time relative to gmt in hours
    parameter (max_dep = 570)   ! depth of lake at sill in meters
    parameter (basedep = 733.)   ! Elevation of Basin Bottom in Meters
    parameter (b_area = 3290000.)   ! Area of Catchment+Lake in Hectares
    parameter (cdrn = 2.0e-3)   ! neutral drag coefficient 1.8 HAD 1.7GISS 1.2CCSM
    parameter (eta = 0.04)   ! shortwave extinction coefficient (1/m)
    parameter (f = 0.1)   ! fraction of advected air over lake
    parameter (alb_slush = 0.4)   ! albedo of melting snow
    parameter (alb_snow = 0.7)   ! albedo of non-melting snow

    parameter (depth_begin = 570)   ! prescribed depth in meters
    parameter (salty_begin = 0.0)   ! prescribed salinity in ppt
      co18prec(xt) = 0.3562*xt-21.079   ! function to calc o18prec
    parameter (o18air = -5.)   ! d18O of air above lake
    parameter (deutair = -130.)   ! dD of air above lake
      cdeutrun(xt) = 2.5915*xt-161.35   ! function to calc deutrun

      real area(max_dep)
      data area/570*3290000./ ! lake area in hectares by depth 

! Simulation specific parameters **************************************

      parameter (nspin = 10)              ! number of years for spinup
      parameter (bndry_flag = .false.)    ! true for explict boundry layer computations; presently only for sigma coord climate models
      parameter (sigma = 0.9925561)       ! sigma level for boundary flag
      parameter (wb_flag = .false.)       ! true for variable lake depth
      parameter (iceflag = .true.)        ! true for variable ice cover
      parameter (s_flag = .false.)        ! true for variable salinity
      parameter (o18flag = .false.)       ! true for variable d18O 
      parameter (deutflag = .false.)      ! true for variable dD
    character(38) :: datafile='/Users/henryqin/Desktop/LakeModelGUI/ERA_INTERIM_climatology_Tang_2yr.txt' ! the data file to open in FILE_OPEN subroutine

!**********************************************************************
! Other parameters DO NOT CHANGE without good reason for doing so******

      parameter (dz=1.0)                ! vertical layer thickness in m
      parameter (dt = 1.*60.*30.)       ! model time step in seconds
      parameter (zo=0.0004)             ! water surface roughness length
    parameter (nspin = 20)   ! number of years for spinup
    parameter (bndry_flag = .true.)   ! true for explict boundry layer computations
    parameter (sigma = 0.9925561)   ! sigma level for boundary flag
    parameter (wb_flag = .true.)   ! true for variable lake depth
    parameter (iceflag = .true.)   ! true for variable ice cover
    parameter (s_flag = .true.)   ! true for variable salinity
    parameter (o18flag = .true.)   ! true for variable d18O
    parameter (deutflag = .true.)   ! true for variable dD
    parameter (z_screen = 5.0)   ! height of met inputs
      parameter (cvap = 1.81e3)         ! specific heat capacity water vapor
      parameter (Le = 2.45e6)           ! latent heat of vaporization water
      parameter (Lei = 2.5e6)           ! latent heat of vaporization ice
      parameter (ca = 6.11e2)           ! constant for Teten's formula
      parameter (cb = 273.16)           ! constant for Teten's formula
      parameter (c72 = 17.269)          ! constant for Teten over water
      parameter (c73 = 35.86)           ! constant for Teten over water
      parameter (c70 = 21.874)          ! constant for Teten over ice
      parameter (c71 = 7.66)            ! constant for Teten over ice
      parameter (emis = 0.97)           ! longwave emmisivity
      parameter (fusion=3.34e5)         ! latent heat of fusion
      parameter (surf = 1.0)            ! surface thickness over which the flux exchange occurs in water
      parameter (fracmin= 0.01)         ! min ice thick in meters
      parameter (fraclim = 0.02)        ! min ice fraction
      parameter (qwtau = 86400.)        ! D. Pollard sub-ice time constant
      parameter (cpw_ice = 4200.)       ! heat capacity of ice
      parameter (condw = .58)           ! conduction coefficinet for water
      parameter (beta=0.4)              ! frac of solar rad abs in water surface layer
      parameter (fsol1=0.5)             ! sw weighting for surface albedo
      parameter (fsol2=0.5)             ! lw weighting for surface albedo
      parameter (sical0=0.6)            ! sw albedo for sea ice
      parameter (sical1=0.4)            ! lw albedo for sea ice
      parameter (kv=0.4)                ! vonkarman constant
      parameter (dm=1.38889E-07)        ! thermal molecular diffusivity of water
      parameter (pi=3.141592654)        !
      parameter (snocrit = 0.05)        ! for albedo, in m
      parameter (dexch  =1.0)           ! fixed depth (m) over which isotope exchange occurs
      parameter (alphak = 0.994)        ! fractionation coeff
      parameter (lamisw = 3.0)          ! extinction coef for sw thru ice
      parameter (lamilw = 20.)          ! extinction coef for lw thru ice
      parameter (lamssw = 3.0)          ! extinction coef for sw thru snow
      parameter (lamslw = 20.)          ! extinction coef for lw thru snow
      parameter (afrac1 = 0.7)          ! fraction of light in visible band for ice model
      parameter (afrac2 = 0.3)          ! fraction of light in infrared band for ice model
      parameter (condi = 2.3)           ! thermal conductivity of ice
      parameter (conds = 0.31)          ! thermal conductivity of snow
      parameter (raddeg = 0.0174533)    ! radians per degree
      parameter (dpd = 360./365.)       ! degrees per day
      parameter (grav = 9.80616)        ! gravity

!**********************************************************************

! Common definitions
      common /ldata/ lcount, iin, iout, numpts , num_tra, ktau, iupto
      common mixing, o18snow_a,deutsnow_a
      common psum_a, depth_a
      common trace(max_dep,n_trace), trace_i(max_dep,n_trace)
      common trace_a (max_dep, n_trace),surfarea_a
      common d_fraca, tempi_a, hice_a, hsnow_a
      common salty_a, mixmax_a, fraci_a 
      common temp_a (max_dep), snow_flag_a, melt_flag_a
      common ktauwan (12),ti_a(max_dep)
      common mix_ave, tsurf_ave, fice_ave
      common evap_ave, hice_ave, hsnow_ave, o18_ave
      common deut_ave, runout_sum, temp_ave(max_dep)

!**********************************************************************
