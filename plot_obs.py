import os
import datetime
import yaml
import xarray as xr
import pandas as pd

import matplotlib
matplotlib.use('Agg') #Cairo')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from configs.plot_config import font_nsimsun, font_path_simhei, font_tnr
# 中文字体设置, 默认黑体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
from pylab import *

from cnmaps import clip_contours_by_map, draw_maps, get_adm_maps, get_adm_names
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from model import GetSession, session_merge_from_records
from model import PngRealWeatherTable

# 运行逻辑
# 逐小时运行，如果 分钟 < 30, 则运行上一小时
import argparse
time_now = datetime.datetime.utcnow() + pd.Timedelta(hours=8)
if time_now.minute < 30: 
  time_now = time_now - pd.Timedelta(hours=1)
time_data = time_now.replace(minute=0, second=0, microsecond=0)
parser = argparse.ArgumentParser(description='实况绘图主程序')
parser.add_argument('--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'), help='设置使用的实况数据的时间, 输入格式为`yyyymmddhh`, 默认是当前时间', default=time_data)
args = parser.parse_args()
# args = parser.parse_args([])
time_data = args.time
print(f"执行时间: {time_data}")

# 变量信息字典：包含实际变量名,对应的标题,绘图区间,绘图区间色号
# 注意:vis原始数据单位是m,仅绘图时修改levels，对应单位为km
variable_info = {
  'TMP': {
      'name': 'TEM',
      'title': '全国气温实况图',
      'unit': '°C',
      'levels':[-12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32, 35, 37, 40],
      'colors':('#003087','#1C5CA6','#2175CF','#3E9FEC','#81D2FF','#ACE7F7','#D2FBFF','#F2FFEE',
                '#D4FDCF','#BFFE89','#FCFE99','#FFF2C4','#FECFA5','#FA9589','#FF5500','#E60000'),
      'type': 1,
      'period': 2
  },
  'PRE': {
      'name': 'PRE',
      'title': '全国降水量实况图',
      'unit': 'mm',
      'levels':[0.1, 2.5, 5, 10, 25, 50, 100],
      'colors':('#FFFFFF','#D8F9CC','#B4F6A3','#6DD86B',
                '#41B836','#66B7F8','#0200F7','#F801FE'),
      'type': 2,
      'period': 2
  },
  'GUST': {
      'name': 'gust',
      'title': '全国逐小时极大风速图',
      'unit': '级',
      'levels':[10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7, 36.9],
      'colors':('#FFFFFF','#01CFFF','#027EFC','#031BF3','#FAD00A',
                '#F69109','#F85B5B','#FB0106','#CC0003'),
      'type': 3,
      'period': 2
  },
  'VIS': {
      'name': 'vis',
      'title': '全国能见度实况图',
      'unit': 'km',
      'levels':[200, 500, 1000, 2000, 3000, 5000, 10000, 20000, 30000],
      'colors':('#6D2701','#9803F9','#F00900','#FA5804','#FFB14D',
                '#FFFC04','#78FB33','#98DDFD','#C8EAFF','#FFFFFF'),
      'type': 4,
      'period': 2
  }
}


def load_config(config_file):
  '''
  从配置文件读取配置

  参数:
  - config_file: str, 配置文件的文件名

  返回:
  - config: dict, 配置信息字典
  '''
  with open(config_file, 'r', encoding='utf-8') as file:
      config = yaml.safe_load(file)
  return config


def read_ncfile(file_path,var_details,open_downsample=False,downsample_factor=10):
  '''
  读取某变量的nc文件,并按需进行下采样
  
  参数:
  - file_path: str, nc路径及文件名
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  - open_downsample: bool, 打开(True)或关闭(False)下采样,默认关闭
  - downsample_factor: integer, 下采样因子,默认10,即每10个格点取一个值
  
  返回:
  - data: xarray.DataArray, 读取的某变量的nc数据
  - lat: xarray.DataArray, 纬度序列
  - lon: xarray.DataArray, 经度序列
  '''
  # ---------- nc文件读取 ----------
  ds = xr.open_dataset(file_path)
  
  # ---------- nc文件信息读取 ----------
  # 下采样,提高绘图效率
  if open_downsample and var_details['name']!='vis':
    data = ds[var_details['name']][::downsample_factor, ::downsample_factor]
    lat = ds['lat'][::downsample_factor]
    lon = ds['lon'][::downsample_factor]
  # 不进行下采样
  else:
    data = ds[var_details['name']]
    lat  = ds['lat']
    lon  = ds['lon']
  
  print(f"(1/9) {var_details['name']} read_ncfile --> finished!")
  return data, lat, lon
  
  
def plot_base_map():
  '''
  通用底图绘制,包含基本地理信息和南海小地图

  参数:
  无

  返回:
  - fig: Figure对象, 存储整个图片
  - ax: Axes对象, 中国区域底图
  - sub_ax: Axes对象, 南海小地图底图
  '''
  # ---------- 底图创建 ----------
  # 定义Albers Equal-Area投影，并设置中央经度为105°E，中央纬度为35°N，标准纬线为25°N和47°N。    
  proj  = ccrs.AlbersEqualArea(central_longitude=105, central_latitude=35, standard_parallels=(25, 47))
  # 参照中央气象台图片848*718像素，400 dpi    
  fig   = plt.figure(figsize=(4.24, 3.60), dpi=400)  # 创建画布    
  ax    = fig.add_subplot(1, 1, 1, projection=proj)  # 创建子图
  # 调整子图边距，占满整个画布
  fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

  # 将地图的范围限制在中国范围内
  region = [80, 126.2, 17, 53.3]
  ax.set_extent(region, crs=ccrs.PlateCarree())

  # ---------- 添加地图要素 ----------
  ax.add_feature(cfeature.LAND, facecolor='white') # 添加白色陆地
  ax.add_feature(cfeature.OCEAN, facecolor='#97DBF2') # 添加蓝色海洋
  ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3) # 添加海岸线
  #ax.add_feature(cfeature.RIVERS.with_scale('50m'), linewidth=0.4, zorder=10) # 添加河流

  # 添加国界线
  draw_maps(get_adm_maps(level='国'), linewidth=0.8, color='grey')

  print("(2/9) plot_base_map --> finished!")
  return fig, ax


def plot_contourf(var_details,data,lat,lon,ax):
  '''
  绘制填色图

  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  - data: xarray.DataArray, 读取的某变量的nc数据
  - lat: xarray.DataArray, 纬度序列
  - lon: xarray.DataArray, 经度序列
  - ax: Axes对象, 中国区域底图
  - sub_ax: Axes对象, 南海小地图底图

  返回:
  无返回,直接执行绘图及裁剪
  '''
  # ---------- 绘制填色图 ----------
  ax_contours = ax.contourf(lon, lat, data, levels=var_details['levels'], extend='both', colors=var_details['colors'],transform=ccrs.PlateCarree())

  # ---------- 裁剪填色图 ----------
  map_polygon = get_adm_maps(country='中华人民共和国', record='first', only_polygon=True) #获取中国边界
  clip_contours_by_map(ax_contours, map_polygon) #利用边界，对填色图进行裁剪

  print(f"(3/9) {var_details['name']} plot_contourf --> finished!")


def add_province_line_name(ax,name_open=0):
  '''
  添加省份分界线,以及省份的名称(可选)

  参数:
  - ax: Axes对象, 中国区域底图
  - name_open: int, 打开(1)或关闭(0)省份名称显示,默认关闭

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 添加省份分界线 ----------
  draw_maps(get_adm_maps(level='省'), linewidth=0.2, color='silver')

  # ---------- 添加省份名称 ----------
  if name_open == 1:
    id        = get_adm_names(level='省')  # 获取地名列表
    shp_info  = get_adm_maps(level='省', engine='geopandas') #获取地名的GeoDataFrame对象
    for x, y, label in zip(shp_info.geometry.centroid.x, shp_info.geometry.centroid.y, id): #添加地名名称
      ax.text(x, y, label, fontsize = 3, ha='left',transform=ccrs.PlateCarree()) #,bbox = dict(facecolor='red', alpha=0.5))
  
  print("(4/9) add_province_line_name --> finished!")


def plot_nanhai(fig,lon,lat,data,var_details):
  '''
  处理南海小地图数据,并绘图
  
  参数:
  - fig: Figure对象, 存储整个图片
  - lon: xarray.DataArray, 经度序列
  - lat: xarray.DataArray, 纬度序列
  - data: xarray.DataArray, 读取的某变量的nc数据
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  
  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 绘制南海地图 ----------
  # 定义Albers Equal-Area投影，并设置中央经度为105°E，中央纬度为35°N，标准纬线为25°N和47°N。    
  proj  = ccrs.AlbersEqualArea(central_longitude=105, central_latitude=35, standard_parallels=(25, 47))
  sub_ax = fig.add_axes([0, 0.01, 0.14, 0.2], projection=proj)
  
  # 设置边框线的颜色
  for spine in sub_ax.spines.values():
    spine.set_edgecolor('grey')
      
  # 设置南海经纬度范围 
  sub_ax.set_extent([107, 120, 2, 23],crs=ccrs.PlateCarree())
  # 绘制地图要素
  sub_ax.add_feature(cfeature.COASTLINE.with_scale('50m'),linewidth=0.2, zorder=1)
  sub_ax.add_feature(cfeature.LAND, facecolor='white') # 添加白色陆地
  sub_ax.add_feature(cfeature.OCEAN, facecolor='#97DBF2') # 添加蓝色海洋
  
  # # ---------- 切片中国区域数据 ----------
  # 将经纬信息转为网格坐标,供maskout使用
  lons, lats = np.meshgrid(lon, lat)
  map_polygon = get_adm_maps(country='中华人民共和国', record='first', only_polygon=True) #获取中国边界
  maskout_data = map_polygon.maskout(lons, lats, data).filled(fill_value=np.nan)
  
  # ---------- 绘制南海填色图 ----------
  sub_ax.contourf(lon, lat, maskout_data, levels=var_details['levels'], extend='both', colors=var_details['colors'],transform=ccrs.PlateCarree())
  #clip_contours_by_map(subax_contours, map_polygon) #利用边界，对南海小地图填色图进行裁剪
    
  # 添加小地图的国界线
  draw_maps(get_adm_maps(level='国'), linewidth=0.4, color='grey')
  
  print("(5/9) plot_nanhai --> finished!")


def add_title(var_details,yyyymmddhh):
  '''
  增加图标题

  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  - yyyymmddhh: int, 绘图的时间

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 信息获取 ----------
  time_obj  = datetime.datetime.strptime(yyyymmddhh, '%Y%m%d%H')  # 时间信息获取
  time_str  = time_obj.strftime('%Y年%-m月%-d日%H时')
  var_title = var_details['title']  # 标题信息获取
  
  # ---------- 添加图片标题 ----------
  plt.suptitle(var_title, fontsize=10, weight='bold', y=0.93)  # 第一行标题
  plt.text(0.5, 0.85, time_str, fontsize=7.5, ha='center', fontfamily='Nsimsun', transform=plt.gcf().transFigure)

  print(f"(6/9) {var_details['name']} add_title --> finished!")


def plot_tmp_legend(var_details,ax):
  '''
  添加气温图例

  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors 
  - ax: Axes对象, 中国区域底图

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 绘图信息获取 ----------  
  var_unit  = var_details['unit']  # 单位信息获取
  text_x = 0.155 # '图例'文字水平边距
  text_y = 0.195 # '图例'文字垂直边距
  # 图例文字内容
  color_labels = [("<-12", "#003087"), ("-12~-8", "#1C5CA6"), ("-8~-4", "#2175CF"), ("-4~0", "#3E9FEC"),("0~4", "#81D2FF"), ("4~8", "#ACE7F7"),("8~12","#D2FBFF"),("12~16","#F2FFEE"),
              ("16~20", "#D4FDCF"), ("20~24", "#BFFE89"), ("24~28", "#FCFE99"), ("28~32", "#FFF2C4"), ("32~35", "#FECFA5"),("35~37","#FA9589"),("37~40","#FF5500"),(">40","#E60000")]
  color_x0 = 0.155 # 左上角第1个矩形色标x坐标
  color_y0 = 0.17 # 左上角第1个矩形色标y坐标
  color_l  = 0.022 # 矩形坐标的长度,大致是color_h 的2.5倍
  color_h  = 0.014  # 矩形坐标的宽度
  gap      = 0.022 # 矩形的间隔

  # ---------- 图例绘制 ----------
  # 添加左下角的图例框
  legend_box = patches.Rectangle((0.15, 0.01), 0.15, 0.21, linewidth=0.6, edgecolor='lightgrey', 
                                facecolor='white', transform=ax.transAxes, zorder=10)
  ax.add_patch(legend_box)
  # 添加图例文字-图例
  plt.text(text_x, text_y, "图例", fontname='SimHei', fontsize=5.5, transform=ax.transAxes, zorder=15)
  # 添加图例文字-单位,相较'图例'向右偏移0.04
  plt.text(text_x + 0.04, text_y, f"({var_unit})", fontname='Times New Roman', fontsize=5.5, transform=ax.transAxes, zorder=15)
  # 设置不同范围的数字及其对应的颜色
  for i, (label, color) in enumerate(color_labels):
      if i < 8:
          # 第1列
          rect = patches.Rectangle((color_x0, color_y0 - i * gap), color_l, color_h, linewidth=0.4, edgecolor='grey', 
                                  facecolor=color, transform=ax.transAxes, zorder=15)
          ax.add_patch(rect)
          ax.text(color_x0+color_l+0.005, color_y0+0.004 - i * gap, label, fontsize=4.3, transform=ax.transAxes, verticalalignment='center', fontfamily='Times New Roman',zorder=15)
      else:
          # 第2列
          rect = patches.Rectangle((color_x0+color_l*3+0.01, color_y0 - (i-8) * gap), color_l, color_h, linewidth=0.4, edgecolor='grey', 
                                  facecolor=color, transform=ax.transAxes, zorder=15)
          ax.add_patch(rect)
          ax.text(color_x0+color_l*3+0.01+color_l+0.005, color_y0+0.004 - (i-8) * gap, label, fontsize=4.3, 
                  transform=ax.transAxes, verticalalignment='center', fontfamily='Times New Roman',zorder=15)
  print("(7/9) plot_tmp_legend --> finished!")

def plot_pre_legend(var_details,ax):
  '''
  添加降水量图例
  
  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors 
  - ax: Axes对象, 中国区域底图

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 绘图信息获取 ---------- 
  var_unit  = var_details['unit']  # 单位信息获取
  text_x = 0.155
  text_y = 0.235
  # 图例文字内容
  color_labels = [("无降水", "#FFFFFF"), ("0~2.5", "#D8F9CC"), ("2.5~5", "#B4F6A3"), ("5~10", "#6DD86B"),("10~25", "#41B836"), ("25~50", "#66B7F8"),("50~100","#0200F7"),(">100","#F801FE")]
  color_x0 = 0.155 # 左上角第1个矩形色标x坐标
  color_y0 = 0.21 # 左上角第1个矩形色标y坐标
  color_l  = 0.022 # 矩形坐标的长度,大致是color_h 的2.5倍
  color_h  = 0.014  # 矩形坐标的宽度
  gap      = 0.027  # 两个色标矩形之间的垂直间隔

  # ---------- 图例绘制 ----------
  # 添加左下角的图例框
  legend_box = patches.Rectangle((0.15, 0.01), 0.10, 0.25, linewidth=0.6, edgecolor='lightgrey', 
                                facecolor='white', transform=ax.transAxes, zorder=10)
  ax.add_patch(legend_box)
  # 添加图例文字-图例
  plt.text(text_x, text_y, "图例", fontfamily='SimHei', fontsize=6, transform=ax.transAxes, zorder=15)
  # 添加图例文字-单位,相较'图例'向右偏移0.04
  plt.text(text_x + 0.04, text_y, f"({var_unit})", fontfamily='Times New Roman', fontsize=6, transform=ax.transAxes, zorder=15)
  # 设置不同范围的数字及其对应的颜色
  for i, (label, color) in enumerate(color_labels):
      # 第1列
      rect = patches.Rectangle((color_x0, color_y0 - i * gap), color_l, color_h, linewidth=0.4, edgecolor='grey', 
                              facecolor=color, transform=ax.transAxes, zorder=15)
      ax.add_patch(rect)
      if i==0:
          ax.text(color_x0+color_l+0.005, color_y0+0.005 - i * gap, label, fontsize=4.7, transform=ax.transAxes, verticalalignment='center', fontfamily='Nsimsun',zorder=15)
      else:
          ax.text(color_x0+color_l+0.005, color_y0+0.005 - i * gap, label, fontsize=4.7, transform=ax.transAxes, verticalalignment='center', fontfamily='Times New Roman',zorder=15)
  print("(7/9) plot_pre_legend --> finished!")

def plot_gust_legend(var_details,ax):
  '''
  添加阵风图例
  
  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors 
  - ax: Axes对象, 中国区域底图

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 绘图信息获取 ----------
  var_unit  = var_details['unit']  # 单位信息获取
  text_x = 0.155
  text_y = 0.265
  color_labels = [("6级以下", "#FFFFFF"), ("6级", "#01CFFF"), ("7级", "#027EFC"), ("8级", "#031BF3"),("9级", "#FAD00A"), 
                  ("10级", "#F69109"),("11级","#F85B5B"),("12级","#FB0106"),("≥13级","#CC0003")]
  color_x0 = 0.155 # 左上角第1个矩形色标x坐标
  color_y0 = 0.24 # 左上角第1个矩形色标y坐标
  color_l  = 0.022 # 矩形坐标的长度,大致是color_h 的2.5倍
  color_h  = 0.014  # 矩形坐标的宽度
  gap      = 0.027  # 两个色标矩形之间的垂直间隔

  # ---------- 图例绘制 ----------
  # 添加左下角的图例框
  legend_box = patches.Rectangle((0.15, 0.01), 0.10, 0.28, linewidth=0.6, edgecolor='lightgrey', 
                                facecolor='white', transform=ax.transAxes, zorder=10)
  ax.add_patch(legend_box)
  # 添加图例文字-图例
  plt.text(text_x, text_y, f"图例({var_unit})", fontname='SimHei', fontsize=6, transform=ax.transAxes, zorder=15)
  # 设置不同范围的数字及其对应的颜色
  for i, (label, color) in enumerate(color_labels):
      # 第1列
      rect = patches.Rectangle((color_x0, color_y0 - i * gap), color_l, color_h, linewidth=0.4, edgecolor='grey', 
                              facecolor=color, transform=ax.transAxes, zorder=15)
      ax.add_patch(rect)
      ax.text(color_x0+color_l+0.005, color_y0+0.005 - i * gap, label, fontsize=4.8, transform=ax.transAxes, 
              verticalalignment='center', fontfamily='Nsimsun',zorder=15)
  print("(7/9) plot_gust_legend --> finished!")

def plot_vis_legend(var_details,ax):
  '''
  添加能见度图例
  
  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors 
  - ax: Axes对象, 中国区域底图

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 绘图信息获取 ----------
  var_unit  = var_details['unit']  # 单位信息获取
  text_x = 0.155
  text_y = 0.265
  color_labels = [("0~0.2", "#6D2701"), ("0.2~0.5", "#9803F9"), ("0.5~1", "#F00900"), ("1~2", "#FA5804"),("2~3", "#FFB14D"), 
                  ("3~5", "#FFFC04"),("5~10","#78FB33"),("10~20","#98DDFD"),("20~30","#C8EAFF"),("≥30","#FFFFFF")]
  color_x0 = 0.155 # 左上角第1个矩形色标x坐标
  color_y0 = 0.24 # 左上角第1个矩形色标y坐标
  color_l  = 0.022 # 矩形坐标的长度,大致是color_h 的2.5倍
  color_h  = 0.014  # 矩形坐标的宽度
  gap      = 0.025  # 两个色标矩形之间的垂直间隔

  # ---------- 图例绘制 ----------
  # 添加左下角的图例框
  legend_box = patches.Rectangle((0.15, 0.01), 0.10, 0.28, linewidth=0.6, edgecolor='lightgrey', 
                                facecolor='white', transform=ax.transAxes, zorder=10)
  ax.add_patch(legend_box)
  # 添加图例文字-图例
  plt.text(text_x, text_y, "图例", fontfamily='SimHei', fontsize=6, transform=ax.transAxes, zorder=15)
  # 添加图例文字-单位,相较'图例'向右偏移0.04
  plt.text(text_x + 0.04, text_y, f"({var_unit})", fontfamily='Times New Roman', fontsize=6, transform=ax.transAxes, zorder=15)
  # 设置不同范围的数字及其对应的颜色
  for i, (label, color) in enumerate(color_labels):
      # 第1列
      rect = patches.Rectangle((color_x0, color_y0 - i * gap), color_l, color_h, linewidth=0.4, edgecolor='grey', 
                              facecolor=color, transform=ax.transAxes, zorder=15)
      ax.add_patch(rect)
      ax.text(color_x0+color_l+0.005, color_y0+0.005 - i * gap, label, fontsize=4.8, transform=ax.transAxes, 
              verticalalignment='center', fontfamily='Times New Roman',zorder=15)
  print("(7/9) plot_vis_legend --> finished!")
  
  
def plot_variable(yyyymmddhh, variable, file_path, output_folder,output_sub_directory):
  '''
  主绘图函数,依次完成:读取nc文件--绘制map底图--绘制填色图--添加省份信息--添加标题--添加图例--保存图片--信息生成

  参数:
  - yyyymmddhh: str, 绘图的时间
  - variable: str, 绘图的变量,来自文件名中命名
  - file_path: str, nc路径及文件名
  - output_folder: str, 图片的存储路径

  返回:
  直接生成图片,返回该变量的入库信息,或None
  '''
  
  # ---------- 获取变量信息 ----------
  var_details = variable_info.get(variable)
  
  try:
    # 1.读取nc文件,数据格点过多时开启下采样
    data,lat,lon = read_ncfile(file_path,var_details,open_downsample=True,downsample_factor=10)

    # 2.绘制map底图
    fig, ax = plot_base_map()

    # 3.绘制填色图
    plot_contourf(var_details,data,lat,lon,ax)

    # 4.添加省份边界线和名称,可选择开启省份名称1
    add_province_line_name(ax)
    
    # 5.绘制南海小地图及填色
    plot_nanhai(fig,lon,lat,data,var_details)

    # 6.添加标题
    add_title(var_details,yyyymmddhh) 
    
    # 7.添加特定变量的图例
    specific_plot_funcs = {
      'TMP': plot_tmp_legend,
      'PRE': plot_pre_legend,
      'GUST': plot_gust_legend,
      'VIS': plot_vis_legend
    }
    plot_func = specific_plot_funcs.get(variable)
    if plot_func:
      plot_func(var_details,ax)  # 图例绘制

    # 8.保存绘制的图像
    save_path = os.path.join(output_folder, f"{variable}_{yyyymmddhh}.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"(8/9) Plot saved: {save_path}")

    # 9.生成入库信息
    save_sub_path = os.path.join(output_sub_directory, f"{variable}_{yyyymmddhh}.png")
    if os.path.exists(save_path):
        image_info = {
            "data_type": var_details['type'],
            "data_time": datetime.datetime.strptime(yyyymmddhh, "%Y%m%d%H"),
            "period": var_details['period'],
            "file_path": save_sub_path
        }
        print(f"(9/9) Image info saved")
        print('-----------------------------------')
        return image_info
    else:
        print(f"Image not found: {save_path}")

  except Exception as e:
    print(f"Unexpected error with {variable}: {e}")


def find_latest_time():
  '''
  获取当前整点时间

  参数：
  无

  返回:
  - latest_time: datetime.datetime, 当前的整点时间
  '''
  # current_time = datetime.datetime.now()
  # latest_time = current_time.replace(minute=0, second=0, microsecond=0)
  latest_time = time_data
  return latest_time


def process_variable(yyyymmddhh, variable, file_path, output_folder, output_sub_directory):
  '''
  处理每个变量的函数,检查nc文件存在并绘图

  参数:
  - yyyymmddhh: str, 绘图的时间
  - variable: str, 绘图的变量,来自文件名中命名
  - input_directory: str, nc文件的输入路径
  - output_folder: str, 图片的存储路径

  返回:
  返回该变量的入库信息, 或None
  '''

  # ---------- 检查nc文件存在 ----------
  try:
    if not os.path.exists(file_path):
      print(f"File {file_path} not found.")
      return
    
    # ---------- 启动绘图主程序 ----------
    onevar_image_info = plot_variable(yyyymmddhh, variable, file_path, output_folder, output_sub_directory)
    return onevar_image_info

  except Exception as e:
    print(f"Unexpected error with {variable}: {e}")


def main(config):
  '''
  主函数,从config获取必要信息,并依次处理每个变量进行绘图

  参数:
  - config: dict, 读取的配置文件

  返回:
  无返回值,完成后直接保存图片
  '''
  # ---------- 获取配置文件信息 ----------
  variables = config['variables']
  output_directory = config['output_directory']
  
  # 获取当前的整点时间
  latest_time = find_latest_time()
  yyyymmddhh = latest_time.strftime('%Y%m%d%H')
  # yyyymmddhh = '2024102317'
  
  output_sub_directory = os.path.join('pic_module/met_obs',yyyymmddhh[0:4],yyyymmddhh[0:6],yyyymmddhh[0:8],yyyymmddhh)
  output_folder = os.path.join(output_directory, output_sub_directory)
  
  # ---------- 输出检查 ----------
  # 检查该时刻的输出文件夹是否存在,存在则覆盖绘制,不存在则创建文件夹并绘图
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  # ---------- 初始化入库信息 ----------
  image_info_list = []
  
  # ---------- 依次处理变量 ----------
  for variable in variables:
  # 获取nc文件信息
    if variable == 'VIS':
      file_name = f"5KM_{variable}_{yyyymmddhh}.nc"
      input_directory = config['input_directory_5km']
      input_sub_directory = f"5KM_NC_{variable}"
    else:
      file_name = f"1KM_{variable}_{yyyymmddhh}.nc"
      input_directory = config['input_directory_1km']
      input_sub_directory = f"1KM_NC_{variable}"
    file_path = os.path.join(input_directory, input_sub_directory, yyyymmddhh[0:4], yyyymmddhh[0:6], yyyymmddhh[0:8], file_name)
    try:
      onevar_image_info = process_variable(yyyymmddhh, variable, file_path, output_folder, output_sub_directory)
      if onevar_image_info is not None:
        image_info_list.append(onevar_image_info)
    except Exception as e:
      print(f"Failed to process {variable} due to an error: {e}")
  
  # ---------- 入库 ----------
  print("入库 ...")
  session = GetSession()
  nowtime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
  add_kwargs = dict(data_id=1, create_time=nowtime, update_time=nowtime)
  # print(image_info_list)
  session_merge_from_records(session, PngRealWeatherTable, image_info_list, **add_kwargs)
  session.close()

  return image_info_list


if __name__ == "__main__":
  # 脚本与相应配置文件请放置在同一个路径下
  config_path = './'
  config_name = 'obs_config.yaml'
  config_file = os.path.join(config_path,config_name)
  config = load_config(config_file)
  image_info_list = main(config)
  
  print("FINISHED! 程序执行完毕")