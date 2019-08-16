import matplotlib.pyplot as plt

import xarray as xr
import numpy as np
import pandas as pd 
import act
import glob
import datetime as dt
import itertools


sdate = '20180815'
#sdate = '20190415'
edate = '20190416'

dates = act.utils.datetime_utils.dates_between(sdate,edate)

time = []
temp_diff = []
temp_mean = []
temp_std = []
rh_mean = []
rh_diff = []
rh_std = []
pres_diff = []
pres_std = []
wspd_diff = []
wspd_std = []
rain_diff = []


for d in dates:
    print(d)
    wxst_file = glob.glob('./cimmswxstX1.b1/master/*'+d.strftime('%Y%m%d')+'.csv')
    meso_file = glob.glob('./sgp05okmX1.b1/*'+d.strftime('%Y%m%d')+'*.cdf')
    wind_file = glob.glob('./cimmswxstX1.b1/wind/wind_'+d.strftime('%Y%m%d')+'.csv')
    rain_file = glob.glob('./cimmswxstX1.b1/rain/rain_'+d.strftime('%Y%m%d')+'.csv')

    if len(meso_file) == 0:
        continue

    meso = act.io.armfiles.read_netcdf(meso_file)
    meso = meso.sortby('time')
    meso = meso.where(meso['platform'] == b'NRMN',drop=True)
    meso['prec_amt'].values[0] = np.array(0)

    if len(wxst_file) > 0:
        headers = ['mcp1','mcp2','htu_temp','htu_dp','htu_rh','bmp_temp',
                 'bmp_pres','bmp_alt','bmp_slp','si_vis','si_ir','uv']    
        master = act.io.csvfiles.read_csv(wxst_file[0],column_names=headers,engine='c')
        #print(list(master['index'].values))
        master['index'].values = pd.to_datetime(master['index'].values)
        master = master.sortby('index')
        for v in master:
            master[v] = master[v].where(master[v] != -9999.)
        temp_mean.append(np.nanmean(master['mcp1'].values))
        rh_mean.append(np.nanmean(master['htu_rh'].values))
        master = master.resample(index='5min').mean()

        headers = ['windspeed_mean','windspeed_max','windspeed_min','windspeed_std',
            'windspeed_med','windspeed_ct',
            'wdir_vec_mean','wdir_max','wdir_min','wdir_std','wdir_ct','raw_min',
            'raw_max','dummy_wind']
        wind = act.io.csvfiles.read_csv(wind_file[0],column_names=headers,engine='c')
        #print(list(wind['index'].values))
        wind['index'].values = pd.to_datetime(wind['index'].values)
        wind = wind.sortby('index')
        for v in wind:
            wind[v] = wind[v].where(wind[v] != -9999.)
        wind = wind.resample(index='5min').mean()
   
        headers = ['total','max_tips','rain_ct','precip_ct','dummy_rain'] 
        rain = act.io.csvfiles.read_csv(rain_file[0],column_names=headers,engine='c')
        rain['index'].values = pd.to_datetime(rain['index'].values)
        rain = rain.sortby('index')
        for v in rain:
            rain[v] = rain[v].where(rain[v] != -9999.)
        rain = rain.resample(index='5min').sum()

        obj = xr.merge([meso,master,wind,rain])

        time.append(obj['time'].values[0])
        temp_diff.append(np.nanmean(obj['mcp1'].values - obj['tdry_1_5m'].values))
        temp_std.append(np.nanstd(obj['mcp1'].values - obj['tdry_1_5m'].values))
        rh_diff.append(np.nanmean(obj['htu_rh'].values - obj['rh'].values))
        rh_std.append(np.nanstd(obj['htu_rh'].values - obj['rh'].values))
        pres_diff.append(np.nanmean(obj['bmp_pres'].values - obj['pres'].values))
        pres_std.append(np.nanstd(obj['bmp_pres'].values - obj['pres'].values))
        wspd_diff.append(np.nanmean(obj['windspeed_mean'].values - obj['wspd_10m'].values))
        wspd_std.append(np.nanstd(obj['windspeed_mean'].values - obj['wspd_10m'].values))
        rain_diff.append((np.sum(obj['total'].values) - obj['prec_amt'].values[-1])[0])

attrs = {'units':'C','long_name':'3D - Mesonet Temperature'}
new = xr.DataArray(temp_diff,coords={'time':time},dims='time',attrs=attrs).to_dataset(name='temp_diff')
attrs = {'units':'C','long_name':'3D Daily Average Temperature'}
new['temp_mean'] = xr.DataArray(temp_mean,coords={'time':time},dims='time',attrs=attrs)
attrs = {'units':'C','long_name':'3D -Mesonet Temperature Difference Standard Deviation'}
new['temp_std'] = xr.DataArray(temp_std,coords={'time':time},dims='time',attrs=attrs)

attrs = {'units':'%','long_name':'3D - Mesonet Relative Humidity'}
new['rh_diff'] = xr.DataArray(rh_diff,coords={'time':time},dims='time',attrs=attrs)
attrs = {'units':'%','long_name':'3D Daily Average Relative Humidity'}
new['rh_mean'] = xr.DataArray(rh_mean,coords={'time':time},dims='time',attrs=attrs)
attrs = {'units':'%','long_name':'3D -Mesonet Relative Humidity Difference Standard Deviation'}
new['rh_std'] = xr.DataArray(rh_std,coords={'time':time},dims='time',attrs=attrs)

attrs = {'units':'HPa','long_name':'3D - Mesonet Atmospheric Pressure'}
new['pres_diff'] = xr.DataArray(pres_diff,coords={'time':time},dims='time',attrs=attrs)
attrs = {'units':'HPa','long_name':'3D -Mesonet Atmospheric Pressure Difference Standard Deviation'}
new['pres_std'] = xr.DataArray(pres_std,coords={'time':time},dims='time',attrs=attrs)

attrs = {'units':'m/s','long_name':'3D - Mesonet Wind Speed'}
new['wspd_diff'] = xr.DataArray(wspd_diff,coords={'time':time},dims='time',attrs=attrs)
attrs = {'units':'m/s','long_name':'3D -Mesonet Wind Speed Difference Standard Deviation'}
new['wspd_std'] = xr.DataArray(wspd_std,coords={'time':time},dims='time',attrs=attrs)

attrs = {'units':'mm','long_name':'3D - Mesonet Rain Accumulation'}
new['rain_diff'] = xr.DataArray(rain_diff,coords={'time':time},dims='time',attrs=attrs)

new.to_netcdf('./data.nc',mode='w')

display = act.plotting.TimeSeriesDisplay(new,figsize=(12,8),subplot_shape=(9,))
display.plot('temp_diff',subplot_index=(0,))
display.plot('temp_std',subplot_index=(1,))
display.plot('rh_diff',subplot_index=(2,))
display.plot('rh_std',subplot_index=(3,))
display.plot('pres_diff',subplot_index=(4,))
display.axes[4].set_yscale('log')
display.plot('pres_std',subplot_index=(5,))
display.plot('wspd_diff',subplot_index=(6,))
display.plot('wspd_std',subplot_index=(7,))
display.plot('rain_diff',subplot_index=(8,))

plt.tight_layout()
plt.savefig('./images/'+dates[0].strftime('%Y%m%d')+'_'+dates[-1].strftime('%Y%m%d')+'.png')
