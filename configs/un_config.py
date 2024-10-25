# -*- encoding: utf-8 -*-
'''
Created on 2024/09/13 12:19:41

@author: BOJUN WANG
'''
# write_tiff
resolution = 0.02
# extent = [116, 122, 30.5, 35.5]
extent = [73, 136, 18, 54]

# ID 类映射
var_type_mapping = {'tmax': 1, 'tmin': 2, 'tp': 3, 'ws10': 4}
device_type_mapping = {'基本站': 1, '基准站': 2, '一般站': 3}
period_mapping = {'1min':1, '1h':2, '1d': 3, '1MS': 4, '1QS': 5, '1YS': 6}   
report_type_mapping = {'imminent':1, 'medium-term': 2, 'short-term': 3}   

## 路径设置

# 输入数据路径
## 高精度预报数据
# input_directory_GJD = '/mnt/wxdata/GX_data/XNYZX-BJ/GJD'
input_directory_GJD = '/home/gpusr/user/wangbj/dkyPlatform/data/GJD'
## 5km 实况数据
# input_directory_5km = '/mnt/wxdata/GX_data'
input_directory_5km = '/home/gpusr/user/wangbj/dkyPlatform/data/5km'
## 1km 实况数据
# input_directory_1km = '/mnt/wxdata/GX_data'
input_directory_1km = '/home/gpusr/user/wangbj/dkyPlatform/data/1km'

# 输出文件路径
output_prefix = '/home/gpusr/user/wangbj/dkyPlatform/output'

# 行政区划、电力设备矢量文件
shape_sta = '/home/gpusr/user/wangbj/Datasets/shapes/remake/station_met.shp'

shape_prov = './shapes/remake/prov_2022.shp'
shape_city = './shapes/remake/city_2022.shp'