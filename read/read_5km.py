# -*- encoding: utf-8 -*-
'''
Created on 2024/09/12 09:21:30

@author: BOJUN WANG
'''
# %%
import os
import datetime
import numpy as np
import pandas as pd
import xarray as xr

from typing import Union
from configs import file_info, data_info, extent, get_time_type
from configs import get_output_path, get_output_filename, print_ndarray_info
from .functions import convert_source_totiff, composite_data, check_files


class Reader_5km(object):
	def __init__(
		self,
		time_start:  	Union[datetime.datetime, pd.Timestamp],
		time_length:   	int,
		time_interval:  int,
		time_type: 		str):
		'''
		:param time_start: 		开始时间
		:param time_length: 	时间长度
		:param time_interval: 	时间间隔
		:param time_type: 		时间长度、间隔类型, ['hour/h/H', 'day/D/d', 'month/M/m', 'quarter/Q/q', 'year/Y/y']
		'''
		self.dsname = '5km'
		
		# 文件信息
		self.root = file_info[self.dsname]['file_root']
		self.folder_name = file_info[self.dsname]['file_folder']
		self.folder_re = file_info[self.dsname]['file_folder_re']
		self.file_name = file_info[self.dsname]['file_name']
		self.file_re = file_info[self.dsname]['file_name_re']
		self.file_var = file_info[self.dsname]['file_name_var']
		self.time_fmts = file_info[self.dsname]['time_fmts']
		self.file_interval = file_info[self.dsname]['file_interval']
		
		# 数据信息
		self.renames = data_info[self.dsname]['renames']
		self.select_extent = extent
		
		# 输入信息标准化
		self.time_start = pd.to_datetime(time_start)
		self.time_interval = int(time_interval)
		self.time_length = int(time_length)
		self.time_type = get_time_type(time_type)
		self.time_period = f'{self.time_interval}{self.time_type}'
		# 输入信息检查
		self.time_check = self.__check_time_info__()
		# 信息获取
		self.__get_field_info__()
	
	def extract_file_infos(self, var):
		'''
		获取文件信息
		'''
		extract_time_range = []
		extract_infos = []
		
		if not self.time_check:
			return None
		
		files_count = 0
		files_group = 0
		
		files_count_target = self.time_length_hour
		files_group_target = len(self.time_range) - 1
		
		for i, start_i in enumerate(self.time_range[:-1]):
			stop_i = self.time_range[i + 1] - datetime.timedelta(hours=self.file_interval)
			
			if (start_i, stop_i) in extract_time_range:
				continue
			
			# start_i ~ stop_i
			print(f"获取 {start_i.strftime('%Y-%m-%dT%H')} 至 {stop_i.strftime('%Y-%m-%dT%H')} 的 {var} 文件")
			files = self.find_files(var, start_i, stop_i, ignore_na=False)
			
			# 没有文件就不加入 self 了
			if not check_files(files):
				extract_files_info = {'time_start': start_i, 'time_stop': stop_i, 'files_count': 0, 'files': None}
			
			else:
				files_count += len(files)
				files_group += 1
				
				extract_files_info = {
					'time_start': start_i, 'time_stop': stop_i, 'files_count': len(files), 'files': files}
			
			extract_infos.append(extract_files_info)
		
		print("———————— ————————")
		
		if files_count==files_count_target:
			print(
				f"[SUCCESS] 成功获取所需的所有文件!", f"文件组:({files_group}/{files_group_target}) 文件数:({files_count}/{files_count_target})")
		
		else:
			print(
				f"[WARNING] 文件获取存在缺失!", f"文件组:({files_group}/{files_group_target}) 文件数:({files_count}/{files_count_target})")
		return extract_infos
	
	
	def find_files(self, var: str, start: pd.Timestamp, stop: pd.Timestamp, ignore_na=False, ignore_warnings=False):
		files = []
		
		time_range = pd.date_range(start, stop, freq=f"{self.file_interval}h")
		ymdhstr_range = list(time_range.strftime(self.time_fmts['ymdh']))
		ymdstr_range = list(time_range.strftime(self.time_fmts['ymd']))
		ymstr_range = list(time_range.strftime(self.time_fmts['ym']))
		ystr_range = list(time_range.strftime(self.time_fmts['year']))
		
		for ymdhstr, ymdstr, ymstr, ystr in zip(ymdhstr_range, ymdstr_range, ymstr_range, ystr_range):
			folder_tar = self.folder_name.format(var=self.file_var[var], year=ystr, ym=ymstr, ymd=ymdstr)
			filename_tar = self.file_name.format(var=self.file_var[var], ymdh=ymdhstr)
			path_tar = os.path.join(self.root, folder_tar, filename_tar)
			
			if os.path.exists(path_tar):
				files.append(path_tar)
			else:
				if not ignore_warnings:
					print(f"[WARNING] 无法获取文件: {filename_tar}, 请检查是否存在!")
				continue
		
		if len(files)!=len(ymdhstr_range):
			if not ignore_warnings:
				print(f"[WARNING] 获取文件存在缺失! \t ({len(files)}/{len(ymdhstr_range)})")
			if not ignore_na:
				if not ignore_warnings:
					print(f"[WARNING] 将不获取存在缺失的文件组")
				return None
			
			if not ignore_warnings:
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
			'method': str, 合成方法
			'variable': str, 变量名
			'tiff_path': str, 合成数据转为 tif 的路径
		}
		'''
		variable_check = list(self.renames)+['wd10', 'epe']
		if not variable in variable_check:
			print(f"[ERROR] 输入的变量 `{variable}` 错误,  应在 `{variable_check}` 中")
			return None
		
		if not method in ['max', 'sum', 'avg', 'mean', 'min', 'most']:
			print(f"[ERROR] 输入的合成方式错误, 应为 `['max','sum', 'avg','mean','min', 'most']`")
			return None
		
		print(f"Loading '{variable}' ...")
		
		data_list = []
		
		if variable == 'wd10':
			extract_infos_u = self.extract_file_infos('u10')
			extract_infos_v = self.extract_file_infos('v10')
			for epoch_u, epoch_v in zip(extract_infos_u, extract_infos_v):
				data_dict = epoch_u.copy()
				
				data = None
				lon = None
				lat = None
				
				if (check_files(epoch_u['files'])) and (check_files(epoch_v['files'])):
					
					lon = self.get_data(epoch_u['files'][0], variable='lon')
					lat = self.get_data(epoch_u['files'][0], variable='lat')
					
					arr_list = []
					for file_u, file_v in zip(epoch_u['files'], epoch_v['files']):
						arr_u = self.get_data(file_u, variable='u10')
						arr_v = self.get_data(file_v, variable='v10')
						arr = np.mod((180. + np.arctan2(arr_u, arr_v)*180./np.pi  ), 360)
						arr_list.append(arr)
					data = composite_data(arr_list, method=method)
					print_ndarray_info(data)
				data_dict.update({'data': data, 'lon':lon, 'lat':lat, 'method': method, 'variable': variable, })
				if to_tiff:
					tiff_path = self.__save_to_tiff__(data_dict)
					data_dict.update({'tiff_path': tiff_path})
				data_list.append(data_dict)
		
		elif variable == 'epe':
			extract_infos = self.extract_file_infos('tp')
			for epoch_infos in extract_infos:
				data_dict = epoch_infos.copy()
				
				data = None
				lon = None
				lat = None
				
				if check_files(epoch_infos['files']):
					
					lon = self.get_data(epoch_infos['files'][0], variable='lon')
					lat = self.get_data(epoch_infos['files'][0], variable='lat')
					
					arr_list = []
					for file in epoch_infos['files']:
						arr_tp = self.get_data(file, variable='tp')
						arr_epe = np.where(np.isnan(arr_tp), np.nan, (arr_tp>50).astype(np.float32))
						arr_list.append(arr_epe)
					data = composite_data(arr_list, method=method)
					print_ndarray_info(data)
				data_dict.update({'data': data, 'lon':lon, 'lat':lat, 'method': method, 'variable': variable, })
				if to_tiff:
					tiff_path = self.__save_to_tiff__(data_dict)
					data_dict.update({'tiff_path': tiff_path})
				data_list.append(data_dict)
		
		else:
			extract_infos = self.extract_file_infos(variable)

			for epoch_infos in extract_infos:
				data_dict = epoch_infos.copy()
				
				data = None
				lon = None
				lat = None
				
				if check_files(epoch_infos['files']):
					
					lon = self.get_data(epoch_infos['files'][0], variable='lon')
					lat = self.get_data(epoch_infos['files'][0], variable='lat')
					
					arr_list = []
					for file in epoch_infos['files']:
						arr = self.get_data(file, variable=variable)
						arr_list.append(arr)

					data = composite_data(arr_list, method=method)
					# 单位转换
					if variable == 'sp':
						# Pa -> hPa
						data = data / 100
					if variable == 'r2m':
						data = data * 100
						data[data>100] = 100
						pass
					
					print_ndarray_info(data)
				
				data_dict.update({'data': data, 'lon':lon, 'lat':lat, 'method': method, 'variable': variable, })
				
				if (variable=='t2m') and (method=='max'):
					data_dict.update({'variable': 'tmax'})
				elif (variable=='t2m') and (method=='min'):
					data_dict.update({'variable': 'tmin'})
				else:
					pass
				
				if to_tiff:
					tiff_path = self.__save_to_tiff__(data_dict)
					data_dict.update({'tiff_path': tiff_path})
				
				data_list.append(data_dict)
		
		return data_list
	
	def get_data(self, filepath, variable: str, select=True):
		# print(f"Load {variable} -> {filepath}")
		
		if variable in self.renames:
			variable = self.renames[variable]
		
		try:
			data = xr.open_dataset(filepath)[variable]
		except Exception as e:
			print(f"[ERROR] 读取失败 {variable} -> {filepath}: {e}")
			return None
		
		if variable in [self.renames['lon'], self.renames['lat']]:
			if select:
				try:
					data = data.sel({variable: self.select[variable]})
				except Exception as e:
					print(f"[ERROR] 切片失败 {variable} -> {filepath}: {e}")
					return None
			
			return data.values.squeeze()
		
		else:
			try:
				dims_ordered = [self.renames['lon'], self.renames['lat']]
				dims_other = sorted([str(i) for i in list(set(data.dims) - set(dims_ordered))])
				dims_ordered = dims_ordered + dims_other
				data = data.transpose(*dims_ordered)
				# data = data.sortby(self.renames['lat']).sortby(self.renames['lon'])
				if select:
					data = data.sel(self.select)
				
			except Exception as e:
				print(f"[ERROR] 排序处理失败 {variable} -> {filepath}: {e}")
				return data.values.squeeze()
			
			return data.values.squeeze()
	
	def __check_time_info__(self):
		# 判断长度是否大于等于间隔
		if self.time_length<self.time_interval:
			print("[ERROR] 输入时间错误: 时间跨度应大于等于 `interval`")
			return False
		
		# time_range [ start, end )
		self.time_range = pd.date_range(start=self.time_start, periods=(self.time_length//self.time_interval)+1, freq=self.time_period)
		
		if self.time_start < self.time_range[0]:
			time_range_start = pd.date_range(end=self.time_start,periods=1,freq=self.time_period)
			self.time_range = time_range_start.append(self.time_range)
		
		self.time_range = self.time_range[:self.time_length+1]
		
		self.time_start = self.time_range[0]
		self.time_end = self.time_range[-1]
		
		time_delta = self.time_end - self.time_start
		self.time_length_hour = int(time_delta.days*24 + time_delta.seconds//3600)
		
		return True
	
	def __get_field_info__(self):
		print("获取文件中 LON, LAT 信息")
		# TODO: 提取 LON, LAT 信息, shape 处理
		lon_min, lon_max, lat_min, lat_max = self.select_extent
		self.select = {self.renames['lon']: slice(lon_min, lon_max), self.renames['lat']: slice(lat_min, lat_max)}
		
		files = []
		for var in self.file_var:
			files = self.find_files(
				var=var,
				start=self.time_start, stop=self.time_end,
				ignore_na=True, ignore_warnings=True)
			if check_files(files):
				break
		
		if not check_files(files):
			self.lon = None
			self.lat = None
			self.shape = None
			self.extent = None
			print(f"[ERROR] 获取文件中 LON, LAT 信息失败")
			return
		
		self.lon = self.get_data(files[0], variable='lon', select=True)
		self.lat = self.get_data(files[0], variable='lat', select=True)
		self.shape = self.get_data(files[0], variable='t2m', select=True).shape  # tuple
		self.extent = [np.nanmin(self.lon), np.nanmax(self.lon), np.nanmin(self.lat), np.nanmax(self.lat)]
		print(f"[SUCCESS] 获取文件中 LON, LAT 信息成功")
	
	def __save_to_tiff__(self, data_dict):
		print("Converting to TIFF ...")
		
		output_path = get_output_path(self.dsname, self.time_period, self.time_start, data_dict['variable'])
		filename_tiff = get_output_filename(
			var=data_dict['variable'], start=data_dict['time_start'], stop=data_dict['time_stop'], filetype='tiff')
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


# %%
# if __name__=="__main__":
	# reader = Reader_5km(datetime.datetime(2023, 11, 27), datetime.datetime(2023, 11, 28), 24)
	
