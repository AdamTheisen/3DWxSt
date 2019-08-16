import matplotlib.pyplot as plt

import xarray as xr
import numpy as np
import pandas as pd 
import act
import glob
import datetime as dt
import itertools


data_file = glob.glob('./data.nc')
var_list = ['temp_diff','temp_mean','rh_diff','rh_mean','pres_diff','wspd_diff','rain_diff']
obj = act.io.armfiles.read_netcdf(data_file,data_vars=var_list)

obj['pres_diff'] = obj['pres_diff'].where(obj['pres_diff'] < 100)
obj['pres_std'] = obj['pres_diff'].where(obj['pres_diff'] < 100)

display = act.plotting.TimeSeriesDisplay(obj,figsize=(12,15),subplot_shape=(5,))
display.plot('temp_diff',subplot_index=(0,))
display.axes[0].yaxis.grid()
#display.plot('temp_std',subplot_index=(1,))
#display.axes[1].yaxis.grid()
display.plot('rh_diff',subplot_index=(1,))
display.axes[1].yaxis.grid()
#display.plot('rh_std',subplot_index=(3,))
#display.axes[3].yaxis.grid()
display.plot('pres_diff',subplot_index=(2,))
display.axes[2].yaxis.grid()
#display.axes[4].set_yscale('log')
#display.plot('pres_std',subplot_index=(5,))
#display.axes[5].yaxis.grid()
display.plot('wspd_diff',subplot_index=(3,))
display.axes[3].yaxis.grid()
#display.plot('wspd_std',subplot_index=(7,))
#display.axes[7].yaxis.grid()
display.plot('rain_diff',subplot_index=(4,))
display.axes[4].yaxis.grid()

plt.tight_layout()

dates = [pd.to_datetime(str(obj['time'].values[0])),pd.to_datetime(str(obj['time'].values[-1]))]
plt.savefig('./images/'+dates[0].strftime('%Y%m%d')+'_'+dates[-1].strftime('%Y%m%d')+'.png')
