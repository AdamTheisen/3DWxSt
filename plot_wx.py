import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import time as ptime

plot_dir = '/var/www/html/plots/'
data_dir = '/home/pi/data/cimms/master/'

print("Finding Files")
time = dt.datetime.now()
cdate = ''.join([str(time.year).zfill(4),str(time.month).zfill(2),
    str(time.day).zfill(2)])
ptime.sleep(5)
files = ''.join([data_dir,'cimms_wxst_',cdate,'.csv'])

print('Reading Data: ',files)
names = ['mcp1_temp','mcp2_temp','htu_temp','htu_dewpoint','htu_rh',
        'bmp_temp','bmp_pres','bmp_alt','bmp_slp','si_vis','si_ir','si_uv']
df = pd.read_csv(files,names=names,index_col=0)

time = df.index
time = [pd.Timestamp(t) for t in time]
xrng = [time[0].date(),time[0].date()+dt.timedelta(days=1)]

print("Starting Plots")
fig = plt.figure(figsize=(10,12))
plt.subplots_adjust(right=0.95,left=0.1,top=0.95,bottom=0.1,wspace=0.1,hspace=0.25)
myFmt = matplotlib.dates.DateFormatter("%H:%M")
ax = fig.add_subplot(4,1,1)
ax.xaxis_date()
ax.set_title('Temperature')
mcp2_offset = 0.14
htu_offset = 0.577
bmp_offset = 1.53
ax.plot_date(time,df['mcp1_temp'])
ax.plot_date(time,df['mcp2_temp'])#-mcp2_offset)
ax.plot_date(time,df['htu_temp'])#-htu_offset)
ax.plot_date(time,df['bmp_temp'])#-bmp_offset)
ax.xaxis.set_major_formatter(myFmt)
ax.set_xlim(xrng)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1])

ax = fig.add_subplot(4,1,2)
ax.set_title('HTU21D-F Relative Humidity')
ax.plot_date(time,df['htu_rh'])
ax.xaxis.set_major_formatter(myFmt)
ax.set_xlim(xrng)

ax = fig.add_subplot(4,1,3)
ax.set_title('BMP280 Pressure')
ax.plot_date(time,df['bmp_pres']/100.)
ax.xaxis.set_major_formatter(myFmt)
ax.set_xlim(xrng)

ax = fig.add_subplot(4,1,4)
ax.set_title('SI1145 UV')
ax.plot_date(time,df['si_uv'])
ax.xaxis.set_major_formatter(myFmt)
ax.set_xlim(xrng)

savename = ''.join([plot_dir,'master_',cdate,'.png'])
print("Saving: ",savename)
plt.savefig(savename)
fig.tight_layout()
plt.close('all')
