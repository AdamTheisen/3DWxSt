import psutil
from subprocess import call

proc = [p.info for p in psutil.process_iter(attrs=['pid','name','cmdline']) if 'python' in p.info['name']]

wind = False
rain = False
for p in proc:
    if 'wind.py' in p['cmdline'][-1]:
        wind = True
    if 'rain.py' not in p['cmdline'][-1]:
        rain = True

if rain is False:
    cmd = 'sudo nohup /home/pi/software/CIMMS_Station/run_rain.txt &'
    print(cmd)
    call(cmd)
if wind is False:
    cmd = 'sudo nohup /home/pi/software/CIMMS_Station/run_wind.txt &'
    print(cmd)
    call(cmd)
