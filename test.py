# -*- encoding: utf-8 -*-
'''
Created on {year}/{month}/{day} 14:42:08

@author: BOJUN WANG
'''
#%%
from model import GetSession
from model import PngRealWeatherTable

# 新建对话
session = GetSession()

dt = dict(
    data_type = 1,
    data_time = '{year}-{month}-01 {hour}:{hour}:{hour}',
    file_path = 'png_real_weather_table/{year}{month}0{month}0/tmp_{year}{month}0{month}0.png',
    create_time = '{year}-{month}-01 15:{hour}:{hour}',
    update_time = '{year}-{month}-01 15:{hour}:{hour}')

# 新增内容
session.merge(PngRealWeatherTable(**dt))

# 合并、关闭对话
session.commit()
session.close()


# %%
from model import *
import os

session_clear_all(PngRealWeatherTable)
session_clear_all(PngForecastWeatherTable)
session_clear_all(PngRadarWeatherTable)
session_clear_all(PngWarnWeatherTable)
session_clear_all(WarnDeviceTable)
session_clear_all(WarnRegionTable)
session_clear_all(StatDeviceTable)
session_clear_all(StatRegionTable)
session_clear_all(WinterForecastProductInfo)

os.system('rm -rf ./runlogs/*')
# %%
import os

# 1km
path_fmt_1km = "/home/gpusr/user/wangbj/statis_jsdk/data/1km/1KM_NC_{var}/{year}/{year}{month}/{year}{month}{day}/1KM_{var}_{year}{month}{day}{hour}.nc"
path_fmt_5km = "/home/gpusr/user/wangbj/Datasets/5km/5KM_NC_{var}/{year}/{year}{month}/{year}{month}{day}/5KM_{var}_{year}{month}{day}{hour}.nc"

year = '2024'
month = '10'
day = '25'
day_new = [str(i).zfill(2) for i in range(26, 32)]

for d in day_new:
    for i in range(0, 24):
        for var in ['PRE', 'GUST', 'TMP', 'WIN']:
            path_raw = path_fmt_1km.format(var=var, year=year, month=month, day=day, hour='00')
            path_new = path_fmt_1km.format(var=var, year=year, month=month, day=d, hour=str(i).zfill(2))
            
            if os.path.exists(path_new):
                continue
            
            dn, fn = os.path.split(path_new)
            os.makedirs(dn, exist_ok=True)
            
            print(f'ln -s {path_raw} {path_new}')
            os.system(f'ln -s {path_raw} {path_new}')

for d in day_new:
    for i in range(0, 24):
        for var in ['PRE', 'DPT', 'PRS', 'RH', 'VIS', 'TMP', 'WIN', 'WIU', 'WIV']:
            path_raw = path_fmt_5km.format(var=var, year=year, month=month, day=day, hour='00')
            path_new = path_fmt_5km.format(var=var, year=year, month=month, day=d, hour=str(i).zfill(2))
            
            if os.path.exists(path_new):
                continue
            
            dn, fn = os.path.split(path_new)
            os.makedirs(dn, exist_ok=True)
            
            print(f'ln -s {path_raw} {path_new}')
            os.system(f'ln -s {path_raw} {path_new}')
            
        #     break
        # break



path_fmt_rad = '/home/gpusr/user/sue/china_DKY/test_data/DOR_RDCP_LATLON_QC_NC/{year}/{year}{month}/{year}{month}{day}/DOR_RDCP_LATLON_QREF_{year}{month}{day}{hour}{minu}.nc'

for d in day_new:
    for i in range(0, 24):
        for m in ['00', '30']:
            path_raw = path_fmt_rad.format(year=year, month=month, day=day, hour='00', minu='00')
            path_new = path_fmt_rad.format(year=year, month=month, day=d, hour=str(i).zfill(2), minu=m)
            
            if os.path.exists(path_new):
                continue
            
            dn, fn = os.path.split(path_new)
            os.makedirs(dn, exist_ok=True)
            
            print(f'ln -s {path_raw} {path_new}')
            os.system(f'ln -s {path_raw} {path_new}')
            
        #     break
        # break





import pandas as pd

path_fmt_gjd = '/home/gpusr/user/wangbj/Datasets/GJD/GJD_{fbstr}_{ybstr}.nc'

fb_time = pd.to_datetime("2024-10-24 12:00:00")
yb_time = pd.to_datetime("2024-10-24 12:00:00")

for d in range(25, 32):
    
    fb_time_new = fb_time.replace(day=d)
    
    for h in range(0, 169):
        fb_str_raw = fb_time.strftime('%Y%m%d%H')
        yb_time = fb_time + pd.Timedelta(hours=h)
        yb_str_raw = yb_time.strftime('%Y%m%d_%H:00:00')
        
        fb_str_new = fb_time_new.strftime('%Y%m%d%H')
        yb_time_new = fb_time_new + pd.Timedelta(hours=h)
        yb_str_new = yb_time_new.strftime('%Y%m%d_%H:00:00')
        
        path_raw = path_fmt_gjd.format(fbstr=fb_str_raw, ybstr=yb_str_raw)
        path_new = path_fmt_gjd.format(fbstr=fb_str_new, ybstr=yb_str_new)
        
        if os.path.exists(path_new):
            continue
        
        dn, fn = os.path.split(path_new)
        os.makedirs(dn, exist_ok=True)
        
        print(f'ln -s {path_raw} {path_new}')
        os.system(f'ln -s {path_raw} {path_new}')