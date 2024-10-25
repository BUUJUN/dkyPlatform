# -*- encoding: utf-8 -*-
'''
Created on 2024/09/19 15:51:15

@author: BOJUN WANG
'''
import xarray as xr
import numpy as np
import scipy.interpolate as interpolate

from osgeo import gdal, osr
from configs import resolution


def check_files(files):
	if files is None:
		return False
	
	if len(files)==0:
		return False
	
	return True


def check_data_to_composite(array:np.ndarray):
	if not (type(array) is np.ndarray):
		return False
	if not (len(array.shape) <= 2):
		return False
	return True


def check_list(array):
	try:
		if array is None:
			return False
		
		if len(array) == 0:
			return False
	except:
		return False
	
	return True

def composite_data(array_list:list[np.ndarray], method:str):
	'''
	将多个二维数组沿第3个维度拼接、合成
	
	:param method:
	:param array_list: List[np.ndarray], ( 2维数组 )
	'''
	print(f"堆叠数据 ...")
	
	if not check_list(array_list):
		print("[ERROR] 没有数据用于堆叠")
		return None
	
	filtered_arrays = [arr for arr in array_list if check_data_to_composite(arr)]
	
	if len(filtered_arrays) == 0:
		print("[ERROR] 没有有效的数据用于堆叠")
		return None
	
	stack_array = np.dstack(filtered_arrays)
	
	if method is None:
		return stack_array
	
	print(f"合成数据 ...")
	
	if method=="max":
		composite = np.nanmax(stack_array, axis=2)
	
	elif method=="min":
		composite = np.nanmin(stack_array, axis=2)
	
	elif method=="sum":
		composite = np.sum(stack_array, axis=2)
	
	elif (method=="avg") or (method=="mean"):
		composite = np.nanmean(stack_array, axis=2)
	
	elif method=="most":
		bins = np.array([0, 45, 90, 135, 180, 225, 270, 315, 360])
		# 使用 np.digitize 将第三维的数据分到区间，得到区间编号（0-7）
		digitized_array = np.digitize(stack_array, bins) - 1
		# 在第三维度上统计每个区间编号的出现频率
		hist_counts = np.apply_along_axis(
			lambda x: np.bincount(x, minlength=8), axis=2, arr=digitized_array
		)
		composite = np.argmax(hist_counts, axis=2)
	
	else:
		print("[WARNING] 输入的合成方式无效, 应为 `['max', 'sum', 'avg', 'min']`")
		return stack_array
	
	# print_ndarray_info(filtered_arrays[0])
	# print_ndarray_info(stack_array)
	# print_ndarray_info(composite)
	
	return composite


def write_tiff(outfile, data, extent:list, res):
	driver = gdal.GetDriverByName('GTiff')
	im_height, im_width = data.shape
	out_tif = driver.Create(outfile, im_width, im_height, 1, gdal.GDT_Float32)
	
	# 设置影像显示区域
	lon_min, lon_max, lat_min, lat_max = extent
	geotransform = (lon_min, res, 0, lat_max, 0, -res)
	out_tif.SetGeoTransform(geotransform)
	
	# 设置地理信息, 选取所需的坐标系统
	srs = osr.SpatialReference()
	# 定义输出的坐标为 WGS84, Authority['EPSG', '4326']
	srs.ImportFromEPSG(4326)
	# 新建图层投影
	out_tif.SetProjection(srs.ExportToWkt())
	# 数据写出
	out_tif.GetRasterBand(1).WriteArray(data)
	out_tif.FlushCache()
	# 关闭 tif 文件
	out_tif = None


class Resample(object):
	def __init__(self, lons: np.ndarray, lats: np.ndarray, data: np.ndarray, res=resolution):
		'''
		:param lons:
		:param lats:
		:param data:
		:param res: 格点分辨率
		'''
		self.lons = lons
		self.lats = lats
		self.data = data
		self.res  = res
		self.data_check = self.__check_data__()
		self.extent = [np.nanmin(lons), np.nanmax(lons), np.nanmin(lats), np.nanmax(lats)]
		self.__generate_grid_lonlat__()
		
	def __generate_grid_lonlat__(self):
		lon_min, lon_max, lat_min, lat_max = self.extent
		lon_line = np.arange(lon_min, lon_max, self.res)
		lat_line = np.arange(lat_min, lat_max, self.res)
		lon_grid, lat_grid = np.meshgrid(lon_line, lat_line)
		self.lon_grid = lon_grid
		self.lat_grid = lat_grid
	
	def __check_data__(self):
		lons_shape = self.lons.shape
		lats_shape = self.lats.shape
		data_shape = self.data.shape
		
		# 首先，经纬度的维度必须相等
		if len(lons_shape) != len(lats_shape):
			print("[ERROR] Input `lons`, `lats` must have the same dimension.")
			return False
		
		# 其次，判断数据与经纬度的维度是否相等
		# 如果相等，都是一维或者都是二维
		if len(data_shape) == len(lons_shape):
			if lons_shape!= data_shape or lats_shape!= data_shape:
				print("[ERROR] Input `lons`, `lats`, `data` must have the same shape.")
				return False
		
		# 如果不相等，经纬度是一维，数据是二维
		elif (len(data_shape) == 2) & (len(lons_shape) == 1):
			if self.data.size != (self.lons.size*self.lats.size):
				print("[ERROR] Input `data` shape must be matched with `lons` and `lats`.")
				return False
			
			if not(set(lons_shape) <= set(data_shape)):
				print("[ERROR] Input `data` shape must be matched with `lons` and `lats`.")
				return False
			
			else:
				lons_new, lats_new = np.meshgrid(self.lons, self.lats)
				if lons_new.shape == data_shape:
					lons_new = lons_new
					lats_new = lats_new
				else:
					self.lons = lons_new.T
					self.lats = lats_new.T
		
		else:
			print("[ERROR] Input `lons`, `lats`, `data` must be either 1D or 2D.")
			return False
		
		if self.lons.shape!=data_shape or self.lats.shape!= data_shape:
			print("[ERROR] Opps...! `lons`, `lats`, `data` shape 还是不一样.")
			return False
		
		return True
	
	def resample_data(self, method='nearest'):
		
		if not self.data_check:
			return None
		
		lon_raw = self.lons.flatten().astype('float32')
		lat_raw = self.lats.flatten().astype('float32')
		data_raw = self.data.flatten().astype('float32')
		
		# 去掉 nan
		data_sel = ~(np.isnan(lon_raw) | np.isnan(lat_raw) | np.isnan(data_raw))
		lon_raw = lon_raw[data_sel]
		lat_raw = lat_raw[data_sel]
		data_raw = data_raw[data_sel]
		
		if len(data_raw) == 0:
			print("[ERROR] No valid data to interpolate.")
			return None
		
		try:
			if method in ['nearest', 'linear']:
				data_interp = interpolate.griddata(
					points=(lon_raw, lat_raw),
					values=data_raw,
					xi=(self.lon_grid, self.lat_grid),
					method=method
				)
			
			# elif method == 'dask':
			#     lon_da = da.from_array(lon_raw, chunks=(1000,))
			#     lat_da = da.from_array(lat_raw, chunks=(1000,))
			#     data_da = da.from_array(data_raw, chunks=(1000,))
			
			#     results = []
			#     for lon_chunck, lat_chunck, data_chunck in zip(lon_da, lat_da, data_da):
			#         results.append(delayed(interpolate.griddata)(
			#             points=(lon_chunck,lat_chunck),
			#             values=data_chunck,
			#             xi=(self.lon_grid, self.lat_grid),
			#             method='nearest'
			#         ))
			#     data_interp = data_interp.compute(*results)
			
			else:
				print(f"[ERROR] 方法：{method} 出错")
				return None
			
		except Exception as e:
			print(f"[ERROR] 重采样出错：{str(e)}")
			return None
			
		return data_interp


# %%
def convert_source_totiff(lons:np.ndarray, lats:np.ndarray, data:np.ndarray, outfile):
	resample = Resample(lons, lats, data)
	data_grid = resample.resample_data(method='nearest')
	write_tiff(outfile, np.flipud(data_grid), resample.extent, resample.res)
	return None

# %%
if __name__ == '__main__':
	ds_test = xr.open_dataset('/home/gpusr/user/wangbj/dkyPlatform/data/2023112712/GJD_2023112712_20231127_12_00_00.nc')
	
	convert_source_totiff(
		lons=ds_test.LON.values,
		lats=ds_test.LAT.values,
		data=ds_test.T2.values,
		outfile='/home/gpusr/user/wangbj/dkyPlatform/test.tiff'
		)
# %%
