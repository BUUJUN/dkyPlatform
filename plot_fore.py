import os
import datetime
import yaml
import xarray as xr
import pandas as pd
from glob import glob

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
# exit()

from model import GetSession, session_merge_from_records
from model import PngForecastWeatherTable

# 运行逻辑
# 每天 08CST 运行，使用前一天 12Z（20CST） 发报的数据
import argparse
time_now = datetime.datetime.utcnow() + pd.Timedelta(hours=8)
time_exec = pd.to_datetime(time_now.date()) + pd.Timedelta(hours=8)

parser = argparse.ArgumentParser(description='预报预警绘图主程序')
parser.add_argument('--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'), help='设置执行时间 (北京时), 输入格式为`yyyymmddhh`, 默认是当天 08 时', default=time_exec)
args = parser.parse_args()
# args = parser.parse_args([])

time_exec = args.time
fore_start_utc = (time_exec+pd.Timedelta(days=-1)).replace(hour=12)
print(f"执行时间: {time_exec}\t数据起报时间: {fore_start_utc}")

# 变量信息字典：包含实际变量名,对应的标题,绘图区间,绘图区间色号
# 注意:vis原始数据单位是m,仅绘图时修改levels，对应单位为km
variable_info = {
  'T2max': {
      'name': 'T2',
      'title': '全国最高气温预报图',
      'unit': '°C',
      'levels':[-12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32, 35, 37, 40],
      'colors':('#003087','#1C5CA6','#2175CF','#3E9FEC','#81D2FF','#ACE7F7','#D2FBFF','#F2FFEE',
                '#D4FDCF','#BFFE89','#FCFE99','#FFF2C4','#FECFA5','#FA9589','#FF5500','#E60000'),
      'type': 1,
      'period': 3
  },
    'T2min': {
      'name': 'T2',
      'title': '全国最低气温预报图',
      'unit': '°C',
      'levels':[-12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32, 35, 37, 40],
      'colors':('#003087','#1C5CA6','#2175CF','#3E9FEC','#81D2FF','#ACE7F7','#D2FBFF','#F2FFEE',
                '#D4FDCF','#BFFE89','#FCFE99','#FFF2C4','#FECFA5','#FA9589','#FF5500','#E60000'),
      'type': 2,
      'period': 3
  },
  'PRE': {
      'name': 'TP',
      'title': '全国降水量预报图',
      'unit': 'mm',
      'levels':[0.1, 10, 25, 50, 100],
      'colors':('#FFFFFF','#B4F6A3','#41B836','#66B7F8','#0200F7','#F801FE'),
      'type': 3,
      'period': 3
  },
  'WIND': {
      'name': 'WS',
      'title': '全国大风预报图',
      'unit': '级',
      'levels':[8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7, 36.9],
      'colors':('#FFFFFF','#01FFFF','#01CFFF','#027EFC','#031BF3',
                '#FAD00A','#F69109','#F85B5B','#FB0106','#CC0003'),
      'type': 4,
      'period': 3
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

  print("(1/8) plot_base_map --> finished!")
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

  print(f"(2/8) {var_details['name']} plot_contourf --> finished!")


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
  
  print("(3/8) add_province_line_name --> finished!")


def plot_nanhai(fig,lon,lat,data,var_details):
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
  # lons, lats = np.meshgrid(lon, lat)
  map_polygon = get_adm_maps(country='中华人民共和国', record='first', only_polygon=True) #获取中国边界
  maskout_data = map_polygon.maskout(lon, lat, data).filled(fill_value=np.nan)
  
  # ---------- 绘制南海填色图 ----------
  sub_ax.contourf(lon, lat, maskout_data, levels=var_details['levels'], extend='both', colors=var_details['colors'],transform=ccrs.PlateCarree())
  #clip_contours_by_map(subax_contours, map_polygon) #利用边界，对南海小地图填色图进行裁剪
    
  # 添加小地图的国界线
  draw_maps(get_adm_maps(level='国'), linewidth=0.4, color='grey')
  
  print("(4/8) plot_nanhai --> finished!")

def add_title(var_details,yyyymmdd):
  '''
  增加图标题

  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  - yyyymmddhh: int, 绘图的时间

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 信息获取 ----------
  time_start      = datetime.datetime.strptime(yyyymmdd, '%Y%m%d')  # 开始日期信息获取
  time_end        = time_start + datetime.timedelta(days=1)  # 结束日期获取
  time_start_str  = time_start.strftime('%-m月%-d日08时')
  time_end_str    = time_end.strftime('%-m月%-d日08时')
  time_str        = time_start_str+'—'+time_end_str
  var_title       = var_details['title']  # 标题信息获取
  
  # ---------- 添加图片标题 ----------
  plt.suptitle(var_title, fontsize=10, weight='bold', y=0.93)  # 第一行标题
  plt.text(0.5, 0.85, time_str, fontsize=7.5, ha='center', fontfamily='Nsimsun', transform=plt.gcf().transFigure)

  print(f"(5/8) {var_details['name']} add_title --> finished!")


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
  print("(6/8) plot_tmp_legend --> finished!")

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
  text_y = 0.20
  # 图例文字内容
  color_labels = [("0~10", "#B4F6A3"), ("10~25", "#41B836"), ("25~50", "#66B7F8"), ("50~100", "#0200F7"),("100~250", "#F801FE")]
  color_x0 = 0.155 # 左上角第1个矩形色标x坐标
  color_y0 = 0.16 # 左上角第1个矩形色标y坐标
  color_l  = 0.032 # 矩形坐标的长度,大致是color_h 的2.5倍
  color_h  = 0.019  # 矩形坐标的宽度
  gap      = 0.033  # 两个色标矩形之间的垂直间隔

  # ---------- 图例绘制 ----------
  # 添加左下角的图例框
  legend_box = patches.Rectangle((0.15, 0.01), 0.12, 0.22, linewidth=0.6, edgecolor='lightgrey', 
                                facecolor='white', transform=ax.transAxes, zorder=10)
  ax.add_patch(legend_box)
  # 添加图例文字-图例
  plt.text(text_x, text_y, "图例", fontfamily='SimHei', fontsize=7, transform=ax.transAxes, zorder=15)
  # 添加图例文字-单位,相较'图例'向右偏移0.04
  plt.text(text_x + 0.05, text_y, f"({var_unit})", fontfamily='Times New Roman', fontsize=7, transform=ax.transAxes, zorder=15)
  # 设置不同范围的数字及其对应的颜色
  for i, (label, color) in enumerate(color_labels):
      # 第1列
      rect = patches.Rectangle((color_x0, color_y0 - i * gap), color_l, color_h, linewidth=0.4, 
                              facecolor=color, transform=ax.transAxes, zorder=15)
      ax.add_patch(rect)

      ax.text(color_x0+color_l+0.005, color_y0+0.005 - i * gap, label, fontsize=6, transform=ax.transAxes, verticalalignment='center', fontfamily='Times New Roman',zorder=15)
  print("(6/8) plot_pre_legend --> finished!")

def plot_wind_legend(var_details,ax):
  '''
  添加风速图例
  
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
  color_labels = [("5级", "#01FFFF"), ("6级", "#01CFFF"), ("7级", "#027EFC"), ("8级", "#031BF3"),("9级", "#FAD00A"), 
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
  print("(6/8) plot_wind_legend --> finished!")


def plot_variable(yyyymmdd, variable, data, lat, lon, output_folder, output_sub_directory):
  '''
  主绘图函数,依次完成:绘制map底图--绘制填色图--添加省份信息--绘制南海填色--添加标题--添加图例--保存图片--信息入库

  参数:
  - yyyymmdd: str, 绘图的时间
  - variable: str, 绘图的变量,自命名
  - data: xr.DataArray, 特定变量variable的一日yyyymmdd统计数据
  - lat: xarray.DataArray, 纬度序列
  - lon: xarray.DataArray, 经度序列
  - output_folder: str, 图片的存储路径

  返回:
  直接生成图片, 同时返回入库信息或None
  '''
  
  # ---------- 获取变量信息 ----------
  var_details = variable_info.get(variable)
  
  try:
    
    # 1.绘制map底图
    fig, ax = plot_base_map()

    # 2.绘制填色图
    plot_contourf(var_details,data,lat,lon,ax)

    # 3.添加省份边界线和名称,可选择开启省份名称1
    add_province_line_name(ax)
    
    # 4.绘制南海小地图及填色
    plot_nanhai(fig,lon,lat,data,var_details)

    # 5.添加标题
    add_title(var_details,yyyymmdd) 
    
    # 6.添加特定变量的图例
    specific_plot_funcs = {
      'T2max': plot_tmp_legend,
      'T2min': plot_tmp_legend,
      'PRE': plot_pre_legend,
      'WIND': plot_wind_legend
    }
    plot_func = specific_plot_funcs.get(variable)
    if plot_func:
      plot_func(var_details,ax)  # 图例绘制
        
    # 7.保存绘制的图像
    save_path = os.path.join(output_folder, f"{variable}_{yyyymmdd}.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"(7/8) Plot saved: {save_path}")
    
    # 8.生成入库信息
    save_sub_path = os.path.join(output_sub_directory, f"{variable}_{yyyymmdd}.png")
    if os.path.exists(save_path):
      image_info = {
          "data_type": var_details['type'],
          "data_time": datetime.datetime.strptime(yyyymmdd, "%Y%m%d"),
          "period": var_details['period'],
          "file_path": save_sub_path
      }
      print(f"(8/8) Image info saved")
      print('-----------------------------------')
      return image_info

  except Exception as e:
    print(f"Unexpected error with {variable}: {e}")


def calculate_daily_stats(variable,ds,open_downsample=False,downsample_factor=4):
  '''
  利用一日数据集,计算特定变量的日统计量,提供加速
  
  参数：
  - variable: str, 所统计的变量, 如'T2max', 'T2min', 'PRE', 'WIND'
  - ds: xr.Dataset, 预报日期的一日数据, time*lat*lon
  - open_downsample: bool, 是否对数据进行下采样,默认False
  - downsample_factor: int, 下采样的因子, 默认为4, 即每4个点采样一次
  
  返回:
  - var_data: xr.DataArray, 特定变量的日统计数据
  '''
  # 获取变量信息
  var_details = variable_info.get(variable)
  var         = var_details['name']
  # 下采样,提高绘图效率
  if open_downsample:
    data = ds[var][:, ::downsample_factor, ::downsample_factor]
    lat = ds['LAT'].isel(time=0)[::downsample_factor, ::downsample_factor]
    lon = ds['LON'].isel(time=0)[::downsample_factor, ::downsample_factor]
  # 不进行下采样
  else:
    data = ds[var]
    lat  = ds['LAT'].isel(time=0)
    lon  = ds['LON'].isel(time=0)
    
  if variable == 'T2max':
    # 计算最大值
    var_data = data.reduce(np.nanmax, dim='time')
    return var_data, lat, lon
  
  elif variable == 'T2min':
    # 计算最小值
    var_data = data.reduce(np.nanmin, dim='time')
    return var_data, lat, lon
  
  elif variable == 'PRE':
    # 计算累积值
    var_data = data.sum(dim='time', skipna=True)
    return var_data, lat, lon
  
  elif variable == 'WIND':
    # 计算平均值
    var_data = data.mean(dim='time', skipna=True)
    return var_data, lat, lon

  print(f"{variable} calculate_daily_stats --> finished!")


def get_forecast_date(ndays=3):
  '''
  生成未来3天(含当日)的预报日期序列
  
  参数:
  - ndays: int, 预报天数, 默认3
  
  返回:
  - fore_start_date: str, 起报日期yyyymmdd12, 采用前一天12z起报数据
  - day_range: list, 未来3天(含当日)的日期字符序列, 例如['20230101', '20230102', '20230103']
  '''
  # start_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
  # start_date = datetime.datetime(2023, 11, 28)
  # end_date   = start_date + datetime.timedelta(days=ndays-1)
  # fore_start_date = (start_date - datetime.timedelta(days=1)).strftime('%Y%m%d12')
  fore_start_date = fore_start.strftime('%Y%m%d12')
  start_date = fore_start + pd.Timedelta(days=1)
  end_date = start_date + pd.Timedelta(days=ndays-1)
  
  day_range   = pd.date_range(start = start_date, end = end_date, freq='D').strftime('%Y%m%d')
  
  return fore_start_date, day_range


def process_one_day(start_date,fore_date):
  '''
  利用预报日期的小时nc数据,按时间维合并生成一日数据集
  
  参数:
  - start_date: str, 起报日期yyyymmdd12, 采用前一天12z起报数据
  - fore_date: str, 预报日期yyyymmdd
  
  返回:
  - ds_oneday: xr.Dataset, 预报日期的一日数据, time*lat*lon
  '''
  files_name  = f"GJD_{start_date}_{fore_date}_*.nc"
  input_files = glob(input_directory+'/'+files_name)
  print(f"找到 {start_date} 起报的 {fore_date} 预报文件共:{len(input_files)}个")
  # 若输入文件夹中至少存在1个文件
  if len(input_files) > 0:
    try:
      ds_oneday = xr.open_mfdataset(input_files, concat_dim="time", combine="nested", parallel=True)
      return ds_oneday
    except Exception as e:
      print(f"合并一天文件时出错: {e}")
  # 若输入文件夹中不存在文件
  else:
      print(f"未找到任何 {start_date} 起报的 {fore_date} 预报文件")


def main():
  '''
  主函数,从config获取必要信息,并依次处理每个变量进行日统计和绘图

  参数:
  - config: dict, 读取的配置文件

  返回:
  无返回值,完成后直接保存图片
  '''
  
  # 获取时间信息  
  fore_start_date, day_range = get_forecast_date(3)
  yyyymmdd    = day_range[0]
  # yyyymmdd = '20241127'
  
  # ---------- 输出检查 ----------
  output_sub_directory = os.path.join('pic_module/met_fcst_GJD',yyyymmdd[0:4], yyyymmdd[0:6], yyyymmdd)
  output_folder = os.path.join(output_directory, output_sub_directory)
  # 检查该日期的输出文件夹是否存在,存在则覆盖绘制,不存在则创建文件夹并绘图
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
  # ---------- 初始化入库信息 ----------
  image_info_list = []

  # ---------- 按照日期收集与处理nc文件 ----------
  # Parallel(n_jobs=16)(delayed(process_one_day)(iday) for iday in day_range)
  for iday in day_range:
    ds_oneday = process_one_day(fore_start_date, iday)
    
  # ---------- 依次处理变量 ----------
    for variable in variables:

      try:
      # ---------- 启动统计程序 ----------
        var_data, lat, lon = calculate_daily_stats(variable,ds_oneday,True)
      except Exception as e:
        print(f"未成功统计{iday} 的 {variable} 是因为该错误: {e}")
      
      try:
      # ---------- 启动绘图主程序 ----------
        onevar_image_info = plot_variable(iday, variable, var_data, lat, lon, output_folder, output_sub_directory)
        if onevar_image_info is not None:
          onevar_image_info['fb_time'] = datetime.datetime.strptime(yyyymmdd, "%Y%m%d").date()
          image_info_list.append(onevar_image_info)
      except Exception as e:
        print(f"未成功绘制和保存 {iday} 的 {variable} 是因为该错误: {e}")
  
  # ---------- 入库 ----------
  print("入库 ...")
  session = GetSession()
  nowtime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
  add_kwargs = dict(data_id=3, create_time=nowtime, update_time=nowtime)
  session_merge_from_records(session, PngForecastWeatherTable, image_info_list, **add_kwargs)
  session.close()
  
  return image_info_list



if __name__ == "__main__":
  # 脚本与相应配置文件请放置在同一个路径下
  config_path = './'
  config_name = 'fore_config.yaml'
  config_file = os.path.join(config_path,config_name)
  config = load_config(config_file)
  # ---------- 获取配置文件信息 ----------
  variables = config['variables']
  output_directory = config['output_directory']
  input_directory  = config['input_directory']
  image_info_list = main()
  
  print("FINISHED! 程序执行完毕")