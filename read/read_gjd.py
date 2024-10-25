# -*- encoding: utf-8 -*-
'''
Created on 2024/09/12 09:21:58

@author: BOJUN WANG
'''
#%%
import re
import os
import datetime
import numpy as np
import pandas as pd
import xarray as xr
from typing import Union
from configs import file_info, data_info, extent, get_forecast_type
from configs import get_output_path, get_output_filename
from .functions import convert_source_totiff, composite_data, check_files


class Reader_GJD(object):
    def __init__(self, time_start:Union[datetime.datetime, pd.Timestamp], time_end:Union[datetime.datetime, pd.Timestamp], interval:int):
        '''
        :param time_start: 开始时间
        :param time_end: 结束时间
        :param interval: 间隔, hours
        '''
        self.dsname = 'GJD'
        
        # 文件信息
        self.root = file_info[self.dsname]['file_root']
        self.folder_re = file_info[self.dsname]['file_folder_re']
        self.file_re = file_info[self.dsname]['file_name_re']
        self.file_name = file_info[self.dsname]['file_name']
        self.fcst_start_hours = file_info[self.dsname]['fcst_start_hours']
        self.fcst_length = file_info[self.dsname]['fcst_length']
        self.fcst_interval = file_info[self.dsname]['fcst_interval']
        self.time_fmts = file_info[self.dsname]['time_fmts']
        
        # 数据信息
        self.renames = data_info[self.dsname]['renames']
        # TODO: 区域选择通过参数传出
        self.select_extent = extent
        
        # 输入信息标准化
        self.time_start = pd.to_datetime(time_start)
        self.time_end = pd.to_datetime(time_end)
        self.interval = int(interval)
        # 输入信息检查
        self.time_check = self.__check_time_info__()
        self.report_type = get_forecast_type(self.time_length, self.interval)
        
        # 信息获取
        self.__get_folders_info__()
        self.__extract_file_infos__()
        self.__get_field_info__()

    def __extract_file_infos__(self):
        '''
        获取文件信息
        '''
        
        # 初始化
        self.files_count = 0
        self.files_group = 0
        # 一共需要获取 files_count_target 个文件
        # 时期数: len(self.time_range)
        # 各个时期: int(self.interval / self.fcst_interval) 个文件
        self.files_count_target = (len(self.time_range)-1) * int(self.interval / self.fcst_interval)
        
        # 一共获取 len(self.time_range) - 1 组文件
        self.files_group_target = len(self.time_range) - 1
        
        self.extract_fb: list[Union[pd.Timestamp, None]] = [None] * self.files_group_target
        self.extract_files = [[]] * self.files_group_target
        self.extract_yb_range: list[(Union[pd.Timestamp, None], Union[pd.Timestamp, None])] = [(None, None)] * self.files_group_target
        self.extract_infos = []
        
        for i in range(len(self.extract_yb_range)):
            yb_start_i = self.time_range[i]
            yb_stop_i = self.time_range[i+1] - datetime.timedelta(hours=self.fcst_interval)
            self.extract_yb_range[i] = (yb_start_i, yb_stop_i)
            
            extract_files_info = {
                'time_fb': None,
                'time_yb_start': yb_start_i, 
                'time_yb_stop': yb_stop_i,
                'files_count':0,
                'files': []
            }
            self.extract_infos.append(extract_files_info)
        
        # 目录结构
        # root
        # ├── data
        # │   ├── 2024091100
        # │   │   ├── GJD_2024091100_2024091101.nc
        # │   │   ├── GJD_2024091100_2024091102.nc
        # │   │   └── ...
        # │   ├── 2024091112
        # │   │   ├── GJD_2024091112_2024091113.nc
        # │   │   ├── GJD_2024091112_2024091114.nc
        # │   │   └── ...
        # │   ├── 2024091200
        # │   │   ├── GJD_2024091212_2024091201.nc
        # │   │   ├── GJD_2024091212_2024091202.nc
        # │   │   └── ...
        
        # 查找最近的预报
        
        yb_fetched = []
        
        if self.time_check:
            for fbstr in self.folder_fbs:
                print("———————— ————————")
                print(f"匹配发报时间: {fbstr}")
                
                folder = None
                
                yb_start = pd.to_datetime(fbstr, format=self.time_fmts['time_fb'])
                yb_end   = yb_start + pd.Timedelta(hours=self.fcst_length)
                
                # print(yb_start, yb_end)
                
                for i in range(len(self.extract_yb_range)):
                    yb_start_i, yb_stop_i = self.extract_yb_range[i]
                    if (yb_start_i, yb_stop_i) in yb_fetched:
                        continue
                    if not (yb_start <= yb_start_i <= yb_end):
                        # print(yb_start, yb_start_i, yb_end)
                        continue
                    if not (yb_start <= yb_stop_i <= yb_end):
                        # print(yb_start, yb_stop_i, yb_end)
                        continue
                    
                    print(f"获取 {yb_start_i.strftime('%Y-%m-%dT%H')} 至 {yb_stop_i.strftime('%Y-%m-%dT%H')} 的文件")
                    files = self.find_files(yb_start, yb_start_i, yb_stop_i, ignore_na=False)
                    
                    # 没有文件就不加入 self 了
                    if not check_files(files):
                        continue
                    
                    self.files_count += len(files)
                    self.files_group += 1
                    
                    self.extract_files[i] = files
                    self.extract_fb[i]    = yb_start
                    
                    self.extract_infos[i].update({
                        'time_fb': yb_start,
                        'files_count': len(files),
                        'files':files, })
                    
                    yb_fetched.append((yb_start_i, yb_stop_i))
                
                if self.files_group == self.files_group_target:
                    break
        
        print("———————— ————————")
        
        if self.files_count == self.files_count_target:
            print(
                f"[SUCCESS] 成功获取所需的所有文件!", 
                f"文件组:({self.files_group}/{self.files_group_target}) 文件数:({self.files_count}/{self.files_count_target})")
        
        else:
            print(
                f"[WARNING] 文件获取存在缺失!",
                f"文件组:({self.files_group}/{self.files_group_target}) 文件数:({self.files_count}/{self.files_count_target})")

    def find_files(self, fb_time:pd.Timestamp, yb_start:pd.Timestamp, yb_stop:pd.Timestamp, ignore_na=False):
        files = []
        
        yb_range = pd.date_range(yb_start, yb_stop, freq=f"{self.fcst_interval}h")
        ybstr_range = list(yb_range.strftime(self.time_fmts['time_yb']))
        fbstr = fb_time.strftime(self.time_fmts['time_fb'])
        
        for ybstr in ybstr_range:
            filename_tar = self.file_name.format(time_fb=fbstr, time_yb=ybstr)
            path_tar = os.path.join(self.root, filename_tar)
            
            if os.path.exists(path_tar):
                files.append(path_tar)
            else:
                print(f"[ERROR] 无法获取文件: {filename_tar}, 请检查是否存在!")
                continue
        
        if len(files) != len(ybstr_range):
            print(f"[ERROR] 获取文件存在缺失! \t ({len(files)}/{len(ybstr_range)})")
            if not ignore_na:
                print(f"[WARNING] 将不获取存在缺失的文件组")
                return None
            
            print(f"[WARNING] 将获取存在缺失的文件组")
        
        [print(f"Add -> {f}") for f in files]
        
        return files

    def extract_data(self, variable, method, to_tiff=True):
        '''
        根据变量名 `variable` 获取并合成数据, 合成方法为 `method`
        
        :param variable: str, ['ws10', 'fg10', 'tp', 't2m', 'r2m', 'sp']
        :param method: str, ['max', 'sum', 'avg', 'mean', 'min']
        :param to_tiff: bool
        :return: {
            'time_fb': pd.Timestamp, 发报时间
            'time_yb_start': pd.Timestamp, 预报时间_开始
            'time_yb_stop': pd.Timestamp, 预报时间_结束
            'files_count': int, 所用源文件数量
            'files': List[str], 所用源文件
            'data': np.ndarray, 合成数据
            'lon': np.ndarray, 合成数据经度
            'lat': np.ndarray, 合成数据纬度
            'method': str, 合成方法
            'variable': str, 变量名
            'tiff_path': str, 合成数据转为 tif 的路径
        }
        '''
        if not variable in self.renames:
            print(f"[ERROR] 输入的变量 `{variable}` 错误,  应为 {list(self.renames)} 中")
            return None
        
        if not method in ['max','sum', 'avg','mean','min']:
            print(f"[ERROR] 输入的合成方式错误, 应为 `['max','sum', 'avg','mean','min']`")
            return None
        
        print(f"Looding '{variable}' ...")
        
        data_list = []
        
        for epoch_infos in self.extract_infos:
            
            data_dict = epoch_infos.copy()
            
            if not check_files(epoch_infos['files']):
                lon = None
                lat = None
                data = None
            
            else:
                lon = self.get_data(epoch_infos['files'][0], variable='lon')
                lat = self.get_data(epoch_infos['files'][0], variable='lat')
                
                arr_list = []
                for file in epoch_infos['files']:
                    arr = self.get_data(file, variable=variable)
                    arr_list.append(arr)
                
                data = composite_data(arr_list, method=method)
            
            data_dict.update({
                'data': data,
                'lon': lon,
                'lat': lat,
                'method': method,
                'variable': variable, 
            })
            
            if (variable == 't2m') and (method == 'max'):
                data_dict.update({'variable': 'tmax'})
            elif (variable == 't2m') and (method == 'min'):
                data_dict.update({'variable': 'tmin'})
            else:
                pass
            
            if to_tiff:
                tiff_path = self.__save_to_tiff__(data_dict)
                data_dict.update({'tiff_path': tiff_path})
            
            data_list.append(data_dict)
        
        return data_list

    def get_data(self, filepath:str, variable:str, select=True):
        # print(f"Load {variable} -> {filepath}")
        
        if variable in self.renames:
            variable = self.renames[variable]
        
        try:
            data = xr.open_dataset(filepath)[variable].values.squeeze()
        
        except Exception as e:
            print(f"[ERROR] 无法读取 {variable} -> {filepath}: {e}")
            return None
        
        if select:
            
            data = np.where(self.select, data, np.nan)
            data = data[~np.isnan(data).all(axis=1)]  # 去掉全为 NaN 的行
            data = data[:, ~np.isnan(data).all(axis=0)]  # 去掉全为 NaN 的列
            
            # data = data[self.select] # Note: 直接切片后的数据转为 1 维
        
        return data

    def __check_time_info__(self):
        
        # 计算时间跨度
        time_delta = self.time_end - self.time_start
        self.time_length = int(time_delta.days * 24 + time_delta.seconds / 3600)
        
        # 检查开始时间是否与预报时间匹配
        fcst_hours = []
        [fcst_hours.extend(range(h, 24, self.fcst_interval)) for h in self.fcst_start_hours]
        fcst_hours = list(set(fcst_hours))
        time_start_hour = self.time_start.hour
        if not (time_start_hour in fcst_hours):
            time_start_hour_new = min(fcst_hours, key=lambda fh: min(abs(fh-time_start_hour), 24-abs(fh-time_start_hour)))
            time_start_new = self.time_start.replace(hour=time_start_hour_new)
            print(f"[WARNING] 输入的开始时间 `{self.time_start}` 有误, 已自动更正为: `{time_start_new}`")
            self.time_start = time_start_new
        
        # 检查结束时间是否与时间间隔匹配
        if (self.time_length % self.interval) != 0:
            time_length_new = self.time_length - (self.time_length % self.interval)
            time_end_new = self.time_start + datetime.timedelta(hours=time_length_new)
            print(f"[WARNING] 输入的结束时间 `{self.time_end}` 有误, 已自动更正为: `{time_end_new}`")
            self.time_end = time_end_new
            self.time_length = time_length_new
        
        # 生成时间数组
        self.time_range = pd.date_range(self.time_start, self.time_end, freq=f'{self.interval}h')
        
        if self.time_length < self.interval:
            print("[ERROR] 输入时间错误: 时间跨度应大于等于 `interval`")
            return False

        if (self.time_length < 0) | (self.time_length > self.fcst_length):
            print("[ERROR] 输入时间错误: `0d <= time_end-time_start <= 7d`")
            return False
        
        if (self.interval % self.fcst_interval) != 0:
            print(f"[ERROR] {self.dsname} 的预报间隔为逐 {self.fcst_interval} 小时, 输入的间隔应为预报间隔的`倍数`!")
            return False
        
        return True

    def __get_folders_info__(self):
        self.folder = []
        self.folder_fbs = []
        
        files_all = [f for f in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, f))]
        files_all = reversed(sorted(files_all))
        
        for f in files_all:
            m = re.match(self.file_re, f)
            
            if not m:
                continue
            
            fb_str = m.groups()[0]
            f_start = pd.to_datetime(fb_str, format=self.time_fmts['time_fb'])
            f_end   = f_start + pd.Timedelta(hours=self.fcst_length)
            
            # 预报开始 <= 报告结束
            # 预报结束 >= 报告开始 
            if not ((f_start <= self.time_end) and (f_end >= self.time_start)):
                continue
            
            # 发报开始时间应在报告开始时间之前
            if not (f_start <= self.time_start):
                continue
            
            if fb_str in self.folder_fbs:
                continue
            
            self.folder.append(f)
            self.folder_fbs.append(fb_str)
        
        if len(self.folder) == 0:
            print(f"[WARNING] 获取的查找目录为空, 无法匹配适合的预报数据")

    def __get_field_info__(self):
        print("获取文件中 LON, LAT 信息")
        lon_min, lon_max, lat_min, lat_max = self.select_extent
        
        files = [x for x in self.extract_files if check_files(x)]
        if (self.files_group == 0) or (len(files) == 0):
            self.lon = None
            self.lat = None
            self.shape = None
            self.extent = None
            print(f"[ERROR] 获取文件中 LON, LAT 信息失败")
            return
        
        file0 = files[0][0]
        lon_raw = xr.open_dataset(file0).LON.values.squeeze()
        lat_raw = xr.open_dataset(file0).LAT.values.squeeze()
        self.select = (lon_raw >= lon_min) & (lon_raw <= lon_max) & (lat_raw >= lat_min) & (lat_raw <= lat_max)
        self.lon = self.get_data(file0, variable='LON', select=True)
        self.lat = self.get_data(file0, variable='LAT', select=True)
        self.shape = self.lon.shape # tuple
        self.extent = [
            np.nanmin(self.lon), np.nanmax(self.lon), 
            np.nanmin(self.lat), np.nanmax(self.lat) ]
        print(f"[SUCCESS] 获取文件中 LON, LAT 信息成功")

    def __save_to_tiff__(self, data_dict):
        print("Converting to TIFF ...")
        output_path = get_output_path(self.dsname, self.report_type, self.time_start, data_dict['variable'])
        filename_tiff = get_output_filename(
            fbtime=data_dict['time_fb'],
            var=data_dict['variable'], 
            start=data_dict['time_yb_start'], 
            stop=data_dict['time_yb_stop'], 
            filetype='tiff'
        )
        path_tiff = os.path.join(output_path, filename_tiff)
        
        if os.path.exists(path_tiff):
            print(f"[WARNING] TIFF 已存在 ...")
            return path_tiff
        
        if data_dict['data'] is None:
            return None
        
        try:
            convert_source_totiff(data_dict['lon'], data_dict['lat'], data_dict['data'], path_tiff)
            print(f"[SUCCESS] TIFF 转换成功 ...")
            
        except Exception as e:
            print(f"[ERROR] TIFF 转换出错: {e}")
            return None
        
        return path_tiff
    
    