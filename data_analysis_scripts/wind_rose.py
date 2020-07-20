import matplotlib
#matplotlib.use('Agg')

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd 
import act
import glob
import sys
import operator
import scipy.stats as stats
import datetime as dt


sdate = '20180815'
#sdate = '20190301'
edate = '20190415'
#edate = '20190401'

# Say, "the default sans-serif font is COMIC SANS"
matplotlib.rcParams['font.sans-serif'] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams['font.family'] = "sans-serif"

dates = act.utils.datetime_utils.dates_between(sdate,edate)

meso_fields = ['wspd_10m','wdir_10m']
wxt_fields = ['windspeed_mean', 'wdir_vec_mean']
ytitle = ['m $s^{-1}$','$^\circ$']
xtitle = ['m $s^{-1}$','$^\circ$']

# Set up empty arrays to append to
time = []
wxt_wspd = []
wxt_wdir = []
mes_wspd = []
mes_wdir= []
for d in dates:
    # Get all files for the day
    wxst_file = glob.glob('./cimmswxstX1.b1/master/*'+d.strftime('%Y%m%d')+'.csv')
    meso_file = glob.glob('./sgp05okmX1.b1/*'+d.strftime('%Y%m%d')+'*.cdf')
    wind_file = glob.glob('./cimmswxstX1.b1/wind/wind_'+d.strftime('%Y%m%d')+'.csv')

    if len(meso_file) == 0 or len(wxst_file) == 0:
        continue

    # Open mesonet files for the norman site
    meso = act.io.armfiles.read_netcdf(meso_file)
    meso = meso.sortby('time')
    meso = meso.where(meso['platform'] == b'NRMN',drop=True)

    # Get 3D weather station data
    if len(wxst_file) == 0:
        continue
    headers = ['windspeed_mean','windspeed_max','windspeed_min','windspeed_std',
               'windspeed_med','windspeed_ct',
               'wdir_vec_mean','wdir_max','wdir_min','wdir_std','wdir_ct','raw_min',
               'raw_max','dummy_wind']
    wind = act.io.csvfiles.read_csv(wind_file[0],column_names=headers,engine='c')
    wind = wind.assign_coords({'index': pd.to_datetime(wind['index'].values)})
    wind = wind.sortby('index')
    wind = wind.rename({'index': 'time'})


    wind = wind.where(wind['wdir_vec_mean'] > 0.)

    for v in wind:
        wind[v] = wind[v].where(wind[v] != -9999.)

    if d >= dt.datetime(2019,2,16):
        wind = wind.where(wind['windspeed_mean'] > 0.)

    wind = wind.resample(time='5min').mean()

    new_obj = xr.merge([meso,wind])


    # Append all data
    time += list(new_obj['time'].values)
    wxt_wspd += list(new_obj['windspeed_mean'].values)
    wxt_wdir += list(new_obj['wdir_vec_mean'].values)

    mes_wspd += list(new_obj['wspd_10m'].values[:,0])
    mes_wdir += list(new_obj['wdir_10m'].values[:,0])


mp = 4.87 / np.log(67.8 * 10. - 5.42)
mes_wspd = np.array(mes_wspd) * mp

obj = xr.Dataset({'wspd': ('time', np.array(wxt_wspd)), 'wdir': ('time', np.array(wxt_wdir)),
                  'mes_wspd': ('time', np.array(mes_wspd)), 'mes_wdir': ('time', np.array(mes_wdir))},
                 {'time': np.array(time)})

obj = obj.where(obj['wdir'].values < 359.)
obj = obj.where(obj['wdir'].values > 1.)
obj = obj.where(obj['wspd'].values != -9999.)
obj = obj.dropna('time')

WindDisplay = act.plotting.WindRoseDisplay(obj, figsize=(8, 10), subplot_shape=(2,))
title = '3D Weather Station Wind Rose'
fig = WindDisplay.plot('wdir', 'wspd', spd_bins=np.linspace(0, 10, 6), num_dirs=36, tick_interval=5,
                 set_title=title, subplot_index=(0,), legend_loc=0, legend_bbox=(1.3, 1.1),
                 legend_title=ytitle[0])
ttl = fig.axes.title
ttl.set_position([.5, 1.07])

title = 'Mesonet Wind Rose'
fig2 = WindDisplay.plot('mes_wdir', 'mes_wspd', spd_bins=np.linspace(0, 10, 6), num_dirs=36, tick_interval=5,
                 set_title=title, subplot_index=(1,), legend_loc=0, legend_bbox=(1.3, 1.1),
                 legend_title=ytitle[0])
ttl = fig2.axes.title
ttl.set_position([.5, 1.07])
plt.show()

wind.close()
meso.close()
new_obj.close()
