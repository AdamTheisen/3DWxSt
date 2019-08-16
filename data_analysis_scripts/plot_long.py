import matplotlib
matplotlib.use('Agg')
import xarray as xr
import pandas as pd
import numpy as np
import datetime
import glob
import matplotlib.pyplot as plt
import itertools
import sys
import act

#date = datetime.datetime.now().strftime('%Y%m%d')
#date = '20180826'

if __name__ == "__main__":
    sdate = '20180815'
    edate = '20190416'
    date = '*'
    master = './cimmswxstX1.b1/master/cimms_wxst_*'+date+'*.csv'
    wind = './cimmswxstX1.b1/wind/wind_*'+date+'*.csv'
    rain = './cimmswxstX1.b1/rain/rain_*'+date+'*.csv'
    meso_file = glob.glob('./sgp05okmX1.b1/*'+date+'*.cdf')


    meso = act.io.armfiles.read_netcdf(meso_file)
    meso = meso.sortby('time')
    meso = meso.where(meso['platform'] == b'NRMN',drop=True)
    meso = meso.squeeze(dim='platform')
    for i,v in enumerate(meso):
        if v == 'rh' or v == 'wdir_10m' or v == 'wspd_10m':
            meso[v] = meso[v].where(meso[v] >= 0.)
        if v == 'tdry_1_5m':
            meso[v] = meso[v].where(meso[v] >= -40.)
        if v == 'srad':
            meso[v] = meso[v].where(meso[v] >= 0.)

    dummy = meso['prec_amt'].values
    dummy[0:289] = 0
    meso['prec_amt'].values = dummy

    #Master Files
    names = ['mcp1','mcp2','htu_temp','htu_dp','htu_rh','bmp_temp',
        'bmp_pres','bmp_alt','bmp_slp','si_vis','si_ir','uv']

    units = ['degC','degC','degC','degC','%','degC','Hpa','m','Hpa','counts','counts','']
    mlist=[]
    files = glob.glob(master)
    for f in files:
        master = act.io.csvfiles.read_csv(f,column_names=names,engine='c')
        mlist.append(master)
    master_xr = xr.merge(mlist)
    master_xr['index'].values = pd.to_datetime(master_xr['index'].values)
    master_xr = master_xr.sortby('index')
    master_xr = master_xr.rename({'index': 'time'})
    for i, v in enumerate(master_xr):
        master_xr[v] = master_xr[v].where(master_xr[v] > -50.)
        if v == 'htu_temp':
            master_xr[v] = master_xr[v].where(master_xr[v] >= 0.)
        if v == 'bmp_pres':
            master_xr[v] = master_xr[v].where(master_xr[v] < 1100.)
        if v == 'htu_rh' or v == 'uv':
            master_xr[v] = master_xr[v].where(master_xr[v] >= 0.)
        master_xr[v].attrs['units'] = units[i]

    master_xr = master_xr.resample(time='5min').mean()


    #Wind files
    names = ['windspeed_mean','windspeed_max','windspeed_min','windspeed_std',
        'windspeed_med','windspeed_ct',
        'wdir_vec_mean','wdir_max','wdir_min','wdir_std','wdir_ct','raw_min',
        'raw_max','dummy_wind']
    units = ['m/s','m/s','m/s','m/s','m/s','counts','deg','deg','deg','deg','count','','','']
    mlist=[]
    files = glob.glob(wind)
    for f in files:
        master = act.io.csvfiles.read_csv(f,column_names=names,engine='c')
        _, index = np.unique(master['index'], return_index=True)
        master = master.isel(index=index)
        mlist.append(master)
    wind_xr = xr.merge(mlist)
    wind_xr['index'].values = pd.to_datetime(wind_xr['index'].values)
    wind_xr = wind_xr.sortby('index')
    wind_xr = wind_xr.rename({'index': 'time'})
    for i, v in enumerate(wind_xr):
        wind_xr[v] = wind_xr[v].where(wind_xr[v] > -1.)
        wind_xr[v].attrs['units'] = units[i]
    wind_xr = wind_xr.resample(time='5min').mean()

    #Rain Files
    names = ['total','max_tips','rain_ct','precip_ct','']
    mlist=[]
    files = glob.glob(rain)
    for f in files:
        master = act.io.csvfiles.read_csv(f,column_names=names,engine='c')
        _, index = np.unique(master['index'], return_index=True)
        master = master.isel(index=index)
        mlist.append(master)
    rain_xr = xr.merge(mlist)
    rain_xr['index'].values = pd.to_datetime(rain_xr['index'].values)
    rain_xr = rain_xr.sortby('index')
    rain_xr = rain_xr.rename({'index': 'time'})
    for i, v in enumerate(rain_xr):
        rain_xr[v] = rain_xr[v].where(rain_xr[v] > -1.)
        rain_xr[v].attrs['units'] = units[i]
    rain_xr = rain_xr.resample(time='5min').sum()
    rain_xr['total'].values[0:10] = 10*[0.]

    new_obj = xr.merge([meso, master_xr, wind_xr, rain_xr])

    ms = 0.5
    mk = '.'
    ax=0
    title = ' '.join(['Temperature from',sdate,'to',edate])
    display = act.plotting.TimeSeriesDisplay(new_obj,figsize=(15,18),subplot_shape=(7,))
    display.plot('bmp_temp', marker=mk, markersize=ms, color='c', subplot_index=(0,))
    display.plot('htu_temp', marker=mk, markersize=ms, color='m', subplot_index=(0,))
    display.plot('tdry_1_5m', marker=mk, markersize=ms, color='g', subplot_index=(0,))
    display.plot('mcp1', marker=mk, markersize=ms, color='b', subplot_index=(0,), set_title=title)
    display.axes[ax].set_ylim([-10,50])
    display.axes[0].legend(['bmp','htu','Mesonet','mcp (Primary)'], markerscale=20)

    ax = 1
    title = ' '.join(['Relative Humidity from',sdate,'to',edate])
    display.plot('rh', marker=mk, markersize=ms, color='g', subplot_index=(ax,))
    display.plot('htu_rh', marker=mk, markersize=ms, color='b', subplot_index=(ax,), set_title=title)
    display.axes[ax].legend(['Mesonet','htu (Primary)'], markerscale=20)

    ax = 2
    title = ' '.join(['Atmospheric Pressure from',sdate,'to',edate])
    display.plot('pres', marker=mk, markersize=ms, color='g', subplot_index=(ax,))
    display.plot('bmp_pres', marker=mk, markersize=ms, color='b', subplot_index=(ax,), set_title=title)
    display.axes[ax].set_ylim([940,1015])
    display.axes[ax].legend(['Mesonet','bmp (Primary)'], markerscale=20)

    ax = 3
    title = ' '.join(['Wind Speed from',sdate,'to',edate])
    display.plot('wspd_10m', marker=mk, markersize=ms, color='g', subplot_index=(ax,))
    display.plot('windspeed_mean', marker=mk, markersize=ms, color='b', subplot_index=(ax,), set_title=title)
    display.axes[ax].legend(['Mesonet','3D (Primary)'], markerscale=20)

    ax = 4
    title = ' '.join(['Wind Direction from',sdate,'to',edate])
    display.plot('wdir_10m', marker=mk, markersize=ms, color='g', subplot_index=(ax,))
    display.plot('wdir_vec_mean', marker=mk, markersize=ms, color='b', subplot_index=(ax,), set_title=title)
    display.axes[ax].legend(['Mesonet','3D (Primary)'], markerscale=20)

    ax = 5
    title = ' '.join(['Radiation from',sdate,'to',edate])
    display.plot('srad', marker=mk, markersize=ms, color='g', subplot_index=(ax,), 
                 set_title=title, label='Mesonet')
    ax2 = display.axes[ax].twinx()
    ax2.plot(new_obj['time'],new_obj['uv'], marker=mk, markersize=ms, color='b', label='3D (Primary)')
    h1, l1 = display.axes[ax].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    display.axes[ax].legend(h1+h2, l1+l2, markerscale=20,loc=0)

    ax = 6
    new_obj['total'] = new_obj['total'].fillna(0)
    rain = list(itertools.accumulate(new_obj['total'].values))
    new_obj['total'].values = rain
    dlist=[]
    dummy = new_obj['prec_amt'].values
    for i in range(len(dummy)-1):
        diff = dummy[i+1]-dummy[i]
        if diff < 0 or diff > 100:
            diff=0
        dlist.append(diff)
    dlist.append(0)
    rain = list(itertools.accumulate(dlist))

    new_obj['prec_amt'].values = rain

    title = ' '.join(['Precipitation from',sdate,'to',edate])
    display.plot('prec_amt', marker=mk, markersize=ms, color='g', subplot_index=(ax,))
    display.plot('total', marker=mk, markersize=ms, color='b', subplot_index=(ax,), set_title=title)
    display.axes[ax].legend(['Mesonet','3D (Primary)'], markerscale=20)

    plt.tight_layout()
    plt.savefig('./images/comparisons/'+sdate+'_'+edate+'.png')

