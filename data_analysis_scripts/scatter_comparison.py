import matplotlib
matplotlib.use('Agg')

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
#sdate = '20190415'
edate = '20190416'

#sdate = '20180815'
#edate = '20180930'

dates = act.utils.datetime_utils.dates_between(sdate,edate)

meso_fields = ['tdry_1_5m', 'rh', 'pres','wspd_10m','wdir_10m','srad', 'prec_amt']
wxt_fields = ['mcp1', 'htu_rh', 'bmp_pres', 'windspeed_mean', 'wdir_vec_mean', 
              'si_vis','total']
fieldname = ['Temperature','Relative Humidity','Pressure','Wind Speed',
             'Wind Direction','Radiation','Precipitation']
ytitle = ['deg C','%','HPa','m/s','deg','W/m2','mm']
xtitle = ['deg C','%','HPa','m/s','deg','counts','mm']

for i,f in enumerate(meso_fields):
    #if i != 6:
    #    continue
    time = []
    wxt = []
    mes = []
    for d in dates:
        if i == 6:
            if d == dt.datetime(2018,8,15):
                continue
        wxst_file = glob.glob('./cimmswxstX1.b1/master/*'+d.strftime('%Y%m%d')+'.csv')
        meso_file = glob.glob('./sgp05okmX1.b1/*'+d.strftime('%Y%m%d')+'*.cdf')
        wind_file = glob.glob('./cimmswxstX1.b1/wind/wind_'+d.strftime('%Y%m%d')+'.csv')
        rain_file = glob.glob('./cimmswxstX1.b1/rain/rain_'+d.strftime('%Y%m%d')+'.csv')

        if len(meso_file) == 0 or len(wxst_file) == 0:
            continue

        meso = act.io.armfiles.read_netcdf(meso_file)
        meso = meso.sortby('time')
        meso = meso.where(meso['platform'] == b'NRMN',drop=True)
        dummy = meso['prec_amt'].values
        dummy[0] = np.array(0)
        meso['prec_amt'].values = dummy

        if len(wxst_file) > 0:
            headers = ['mcp1','mcp2','htu_temp','htu_dp','htu_rh','bmp_temp',
                       'bmp_pres','bmp_alt','bmp_slp','si_vis','si_ir','uv']    
            master = act.io.csvfiles.read_csv(wxst_file[0],column_names=headers,engine='c')
            master['index'].values = pd.to_datetime(master['index'].values)
            master = master.sortby('index')
            master = master.rename({'index': 'time'})
            for v in master:
                master[v] = master[v].where(master[v] != -9999.)
            master = master.resample(time='5min').mean()

            headers = ['windspeed_mean','windspeed_max','windspeed_min','windspeed_std',
                       'windspeed_med','windspeed_ct',
                       'wdir_vec_mean','wdir_max','wdir_min','wdir_std','wdir_ct','raw_min',
                       'raw_max','dummy_wind']
            wind = act.io.csvfiles.read_csv(wind_file[0],column_names=headers,engine='c')
            wind['index'].values = pd.to_datetime(wind['index'].values)
            wind = wind.sortby('index')
            wind = wind.rename({'index': 'time'})
            for v in wind:
                wind[v] = wind[v].where(wind[v] != -9999.)
            wind = wind.resample(time='5min').mean()

            headers = ['total','max_tips','rain_ct','precip_ct','dummy_rain']
            rain = act.io.csvfiles.read_csv(rain_file[0],column_names=headers,engine='c')
            rain['index'].values = pd.to_datetime(rain['index'].values)
            rain = rain.sortby('index')
            rain = rain.rename({'index': 'time'})
            for v in rain:
                rain[v] = rain[v].where(rain[v] != -9999.)
            rain = rain.resample(time='5min').sum()
        else:
            continue

        if i == 3 or i ==4:
            new_obj = xr.merge([meso,wind])
        elif i == 6:
            rain = rain.resample(time='24h').sum()
            meso24 = meso.resample(time='24h').max()
            new_obj = xr.merge([meso24,rain])
        else:
            new_obj = xr.merge([meso,master])

        new_obj = new_obj.where(new_obj[f] > -100)
        if i == 2:
            new_obj = new_obj.where(new_obj[f] > 900)
            new_obj = new_obj.where(new_obj[f] < 1100)
            new_obj = new_obj.where(new_obj['bmp_pres'] > 900)
            new_obj = new_obj.where(new_obj['bmp_pres'] < 1100)

        time += list(new_obj['time'].values)
        if len(np.shape(new_obj[wxt_fields[i]].values)) > 2:
            wxt += list(new_obj[wxt_fields[i]].values[:,0,0])
            print(new_obj)
            sys.exit()
        else:
            wxt += list(new_obj[wxt_fields[i]].values)

        mes += list(new_obj[meso_fields[i]].values[:,0])

        if len(wxt) != len(mes):
            print(new_obj)
            sys.exit()

    if len(np.shape(wxt)) > 1:
        wxt = np.reshape(wxt,len(wxt))

    colors = time

    title = ' '.join([fieldname[i],'Comparison Between',
                      dates[0].strftime('%Y%m%d'),'-',dates[-1].strftime('%Y%m%d')])
    fig, ax = plt.subplots(1,figsize=(9,8))

    sc = ax.scatter(wxt,mes,c=colors)
    plt.title(title)
    plt.xlabel('3D Weather Station ('+xtitle[i]+')')
    plt.ylabel('Mesonet ('+ytitle[i]+')')
    if i == 0:
       plt.xlim([-15,40])
       plt.ylim([-15,40])
       ax.plot([-15,40],[-15,40],'--b')
    if i == 1:
       plt.xlim([0,110])
       plt.ylim([0,110])
       ax.plot([0,110],[0,110],'--b')
    if i == 2:
       plt.xlim([940,1010])
       plt.ylim([940,1010])
       ax.plot([940,1010],[940,1010],'--b')
    if i == 3:
       plt.xlim([0,15])
       plt.ylim([0,15])
       ax.plot([0,15],[0,15],'--b')
    if i == 4:
       plt.xlim([0,360])
       plt.ylim([0,360])
       ax.plot([0,360],[0,360],'--b')

    if i == 6:
       plt.xlim([0,80])
       plt.ylim([0,80])
       ax.plot([0,80],[0,80],'--b')

    diff = np.nanmean(list(map(operator.sub, wxt, mes)))
    plt.text(0.99,-0.05, 'Average Diff = '+str(round(diff,2)),ha='right',va='center',transform=ax.transAxes)

    s1 = pd.Series(wxt)
    s2 = pd.Series(mes)
    cc = s1.corr(s2)
    plt.text(0.99,-0.075, 'Correlation Coeff = '+str(round(cc,2)),ha='right',va='center',transform=ax.transAxes)

    cbar = plt.colorbar(sc, aspect=70)
    cbar.ax.set_yticklabels(pd.to_datetime(cbar.get_ticks()).strftime(date_format='%-m/%-d/%y'))

    #plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.999)
    plt.savefig('./images/scatter/'+wxt_fields[i]+'_'+meso_fields[i]+'_'+dates[0].strftime('%Y%m%d')+'_'+dates[-1].strftime('%Y%m%d')+'.png')
    plt.close()
