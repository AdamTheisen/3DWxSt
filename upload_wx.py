#!/usr/bin/env python
import os
import datetime as dt
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import glob
import json

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('/home/pi/software/CIMMS_Station/storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('/home/pi/software/CIMMS_Station/client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

path='/home/pi/data/cimms/'

dirs = glob.glob(path+'*')

id_filename = '/home/pi/software/CIMMS_Station/ids.json'
with open(id_filename) as f:
    dir_id = json.load(f)

date = dt.datetime.now()-dt.timedelta(days=1)
prev_date = ''.join([str(date.year).zfill(4),str(date.month).zfill(2),
    str(date.day).zfill(2)])

for d in dirs:
    files = glob.glob(d+'/*'+prev_date+'*csv')
    if len(files) == 0:
        continue
    inst = d.split('/')[-1]
    for f in files:
        filename = f.split('/')[-1]
        inst_id = dir_id[inst] 
        metadata = {'title': filename,'parents':[inst_id],'name':filename}
        res = DRIVE.files().create(body=metadata,media_body=f).execute()
        if res:
            print('Uploaded "%s" (%s)' % (f, res['mimeType']))
