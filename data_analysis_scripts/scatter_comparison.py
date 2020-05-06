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
#sdate = '20190116'
#edate = '20190117'
edate = '20190415'

#sdate = '20180815'
#edate = '20180930'

# Say, "the default sans-serif font is COMIC SANS"
matplotlib.rcParams['font.sans-serif'] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams['font.family'] = "sans-serif"

dates = act.utils.datetime_utils.dates_between(sdate,edate)

meso_fields = ['tdry_1_5m', 'rh', 'pres','wspd_10m','wdir_10m','srad', 'prec_amt','tdry_1_5m', 'prec_amt']
wxt_fields = ['mcp1', 'htu_rh', 'bmp_pres', 'windspeed_mean', 'wdir_vec_mean', 
              'si_vis','total','htu_temp', 'total']
fieldname = ['Air Temperature','Relative Humidity','Atmospheric Pressure',
             'Wind Speed','Wind Direction','Solar Radiation',
             'Precipitation','Air Temperature', 'Rain Rate']
ytitle = ['$^\circ$C','%','hPa','m/s','$^\circ$','W/m2','mm', '$^\circ$C', 'mm/hr']
xtitle = ['$^\circ$C','%','hPa','m/s','$^\circ$','W/m2','mm', '$^\circ$C', 'mm/hr']

for i,f in enumerate(meso_fields):
    if i !=  1:
        continue
    time = []
    wxt = []
    mes = []
    wxt_u = []
    wxt_v = []
    mes_u = []
    mes_v = []
    wxt_wind = []
    for d in dates:
        if i == 6 or i == 8:
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
        elif i == 0 or i == 7 or i == 1:
            new_obj = xr.merge([meso,master,wind])

        elif i == 6:
            rain = rain.resample(time='24h').sum()
            meso24 = meso.resample(time='24h').max()
            new_obj = xr.merge([meso24,rain])
        elif i == 8:
            new_obj = xr.merge([meso,rain])
            meso_rain = np.append(np.diff(new_obj[f].values[:,0]),0)
            idx = (meso_rain > 100.)
            meso_rain[idx] = 0.
            new_obj[meso_fields[i]].values[:, 0] = meso_rain * 12.
            new_obj[wxt_fields[i]].values = new_obj[wxt_fields[i]].values * 12.
        else:
            new_obj = xr.merge([meso,master])

        new_obj = new_obj.where(new_obj[f] > -100)
        if i == 2:
            new_obj = new_obj.where(new_obj[f] > 900)
            new_obj = new_obj.where(new_obj[f] < 1100)
            new_obj = new_obj.where(new_obj['bmp_pres'] > 900)
            new_obj = new_obj.where(new_obj['bmp_pres'] < 1100)

        if i == 1:
            new_obj[wxt_fields[i]].values = new_obj[wxt_fields[i]].values + (25. - new_obj[wxt_fields[7]].values) * (0-0.15)
        if i == 2:
            new_obj[wxt_fields[i]].values = new_obj[wxt_fields[i]].values + (25. - new_obj['mcp2'].values) * (0-0.015)


        if i == 5:
            new_obj[wxt_fields[i]].values = new_obj[wxt_fields[i]].values * 0.7 - 170.66

        time += list(new_obj['time'].values)
        if len(np.shape(new_obj[wxt_fields[i]].values)) > 2:
            wxt += list(new_obj[wxt_fields[i]].values[:,0,0])
        else:
            wxt += list(new_obj[wxt_fields[i]].values)

        #wxt_wind += list(new_obj['windspeed_mean'].values[:,0])

        mes += list(new_obj[meso_fields[i]].values[:,0])

        if len(wxt) != len(mes):
            print(new_obj)
            sys.exit()


    if len(np.shape(wxt)) > 1:
        wxt = np.reshape(wxt,len(wxt))

    if i == 0 or i == 7:
        idx = (wxt > 45.)
        wxt[idx] = np.nan

        #idx = (np.asarray(wxt_wind) < 8.)
        #wxt[idx] = np.nan


    if i == 1:
        idx = (wxt > 100.)
        wxt[idx] = 100.

        idx = (wxt > 80.)
        wxt[idx] = np.nan
        #idx = (np.asarray(wxt_wind) >= 20.)
        #wxt[idx] = np.nan
    if i == 3:
        mp = 4.87 / np.log(67.8 * 10. - 5.42)
        print(mp)
        mes = np.array(mes) * mp

    #if i == 4:
    #    idx = (np.asarray(wxt_wind) < 5.)
    #    wxt[idx] = np.nan

    if i == 5:
        idx = (wxt < 0.)
        wxt[idx] = np.nan
    #if i == 8:
        #idx = (np.asarray(wxt) == 0.) & (np.asarray(mes) == 0.)
        #wxt = np.asarray(wxt)
        #wxt[idx] = np.nan
        #mes = np.asarray(mes)
        #mes[idx] = np.nan

    colors = time

    title = fieldname[i]
    fig, ax = plt.subplots(1,figsize=(9,8))

    sc = ax.scatter(wxt,mes,c=colors)
    plt.title(title)
    plt.xlabel('3D Weather Station ('+xtitle[i]+')')
    plt.ylabel('Mesonet ('+ytitle[i]+')')
    if i == 0:
       plt.xlim([-15,45])
       plt.ylim([-15,45])
       ax.plot([-15,45],[-15,45],'--b')
    if i == 1:
       plt.xlim([0,100])
       plt.ylim([0,100])
       ax.plot([0,100],[0,100],'--b')
    if i == 2:
       plt.xlim([940,1010])
       plt.ylim([940,1010])
       ax.plot([940,1010],[940,1010],'--b')
    if i == 3:
       plt.xlim([0,18])
       plt.ylim([0,18])
       ax.plot([0,18],[0,18],'--b')
    if i == 4:
       plt.xlim([0,360])
       plt.ylim([0,360])
       ax.plot([0,360],[0,360],'--b')
    if i == 5:
       plt.xlim([0,1250])
       plt.ylim([0,1250])
       ax.plot([0,1250],[0,1250],'--b')

    if i == 6:
       plt.xlim([0,80])
       plt.ylim([0,80])
       ax.plot([0,80],[0,80],'--b')
    if i == 7:
       plt.xlim([-15,45])
       plt.ylim([-15,45])
       ax.plot([-15,45],[-15,45],'--b')
    if i == 8:
       plt.xlim([0,120])
       plt.ylim([0,120])
       ax.plot([0,120],[0,120],'--b')


    plt.text(1.05,-0.025, 'Min(3D) = '+str(round(np.nanmin(wxt),2)),ha='left',va='center',transform=ax.transAxes)
    plt.text(1.05,-0.05, 'Min(Meso) = '+str(round(np.nanmin(mes),2)),ha='left',va='center',transform=ax.transAxes)
    plt.text(1.05,-0.075, 'Max(3D) = '+str(round(np.nanmax(wxt),2)),ha='left',va='center',transform=ax.transAxes)
    plt.text(1.05,-0.1, 'Max(Meso) = '+str(round(np.nanmax(mes),2)),ha='left',va='center',transform=ax.transAxes)


    if i == 4:
        idx = (np.asarray(wxt) < 60.) & (np.asarray(mes) > 300.)
        np.asarray(wxt)[idx] += 360.
        idx = (np.asarray(mes) < 60.) & (np.asarray(wxt) > 300.)
        np.asarray(mes)[idx] += 360.


    try:
        diff = np.nanmean(np.abs(list(map(operator.sub, wxt, mes))))
    except:
        print('failed on '+wxt_fields[i])
        continue

    s1 = pd.Series(wxt)
    s2 = pd.Series(mes)
    cc = s1.corr(s2)

    mse = np.nanmean((wxt - mes)**2)
    rmse = np.sqrt(mse)
    mask = ~np.isnan(mes) & ~np.isnan(wxt)
  
    try: 
        linreg = stats.linregress(np.asarray(wxt)[mask], np.asarray(mes)[mask])
    except:
        print('failed on '+wxt_fields[i])
        continue

    stdev = np.sqrt(np.nanmean(np.abs(wxt - np.nanmean(mes))**2))
    sem = stdev/np.sqrt(len(wxt))

    plt.text(0.99, -0.05, 'SEM = '+str(round(sem,3)),ha='right',va='center',transform=ax.transAxes)
    plt.text(0.99, -0.075, 'RMSE = '+str(round(rmse,2)),ha='right',va='center',transform=ax.transAxes)
    plt.text(0.99, -0.1, 'Average Diff = '+str(round(diff,2)),ha='right',va='center',transform=ax.transAxes)

    plt.plot(wxt, linreg.slope * wxt + linreg.intercept, 'k')
    plt.text(0.01,-0.05, 'Slope = '+str(round(linreg.slope,2)),ha='left',va='center',transform=ax.transAxes)
    plt.text(0.01,-0.075, 'Intercept = '+str(round(linreg.intercept,2)),ha='left',va='center',transform=ax.transAxes)
    plt.text(0.01,-0.1, 'Correlation Coeff = '+str(round(linreg.rvalue,2)),ha='left',va='center',transform=ax.transAxes)

    cbar = plt.colorbar(sc, aspect=70)
    cbar.ax.set_yticklabels(pd.to_datetime(cbar.get_ticks()).strftime(date_format='%d/%m/%Y'))
    cbar.ax.set_ylabel('Date', rotation=90, labelpad=-80)

    #plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.999)
    if i == 8:
        plt.savefig('./images/scatter/'+'rain_rate_'+dates[0].strftime('%Y%m%d')+'_'+dates[-1].strftime('%Y%m%d')+'.png', dpi=300)
    else:
        plt.savefig('./images/scatter/'+wxt_fields[i]+'_'+meso_fields[i]+'_'+dates[0].strftime('%Y%m%d')+'_'+dates[-1].strftime('%Y%m%d')+'.png', dpi=300)
    plt.close()

meso.close()
