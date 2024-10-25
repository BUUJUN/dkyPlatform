import os
import datetime
import yaml
import xarray as xr
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg') #Cairo')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from configs.plot_config import font_nsimsun, font_path_simhei, font_tnr
# 中文字体设置, 默认黑体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
from pylab import *

from cnmaps import draw_maps, get_adm_maps, get_adm_names
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from model import GetSession, session_merge_from_records
from model import PngRadarWeatherTable

# 运行逻辑
# 逐小时运行，如果 分钟 < 30, 则运行上一小时 30 分，否则这一小时 00 分
import argparse
time_now = datetime.datetime.utcnow() + pd.Timedelta(hours=8)

if time_now.minute < 30: 
  time_data = time_now - pd.Timedelta(hours=1)
  time_data = time_data.replace(minute=30, second=0, microsecond=0)
else:
  time_data = time_now.replace(minute=0, second=0, microsecond=0)

parser = argparse.ArgumentParser(description='雷达绘图主程序')
parser.add_argument('--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'), help='设置使用的实况数据的时间, 输入格式为`yyyymmddhh`, 默认是当前时间00分', default=time_data)
args = parser.parse_args()
# args = parser.parse_args([])
time_data = args.time
print(f"执行时间: {time_data}")

# 变量信息字典：包含实际变量名,对应的标题,绘图区间,绘图区间色号
# 注意:cref原始数据单位是*0.01 dBZ,转换单位为dBZ
variable_info = {
  'RADAR':{
      'name': 'CREF',
      'title': '全国雷达拼图',
      'unit': 'dBZ',
      'levels': np.arange(5,75,5),
      'colors':('#419DF1','#64E7EB','#6DFA3D','#00D800','#019000','#FFFF00','#E7C000',
                '#FF9000','#FF0000','#D60000','#C00000','#FF00F0','#9600B4','#AD90F0'),
      'type': 1,
      'period': 1
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
    data = ds[var_details['name']][::downsample_factor, ::downsample_factor] /10
    lat = ds['lat'][::downsample_factor]
    lon = ds['lon'][::downsample_factor]
  # 不进行下采样
  else:
    data = ds[var_details['name']] /10
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
  - gs: GridSpec, 主图与图例区域9:1划分
  '''
  # ---------- 底图创建 ----------
  # 定义Albers Equal-Area投影，并设置中央经度为105°E，中央纬度为35°N，标准纬线为25°N和47°N。    
  proj    = ccrs.AlbersEqualArea(central_longitude=105, central_latitude=35, standard_parallels=(25, 47))
  # 参照中央气象台图片825*739像素，400 dpi    
  fig     = plt.figure(figsize=(11.45, 10.25), dpi=200)  # 创建画布
  # 使用GridSpec来布局
  gs      = gridspec.GridSpec(2, 1, height_ratios=[9, 1]) 
  ax      = fig.add_subplot(gs[0], projection=proj)  # 创建子图
  # 左、右、上边距为0，下边距留出10%的距离
  ax.set_position([0, 0.10, 1, 0.95])

  # 将地图的范围限制在中国范围内
  region = [79, 127, 17.8, 55.5]
  ax.set_extent(region, crs=ccrs.PlateCarree())

  # ---------- 添加地图要素 ----------
  ax.add_feature(cfeature.LAND, facecolor='#E5E5E5') # 添加灰色陆地
  ax.add_feature(cfeature.OCEAN, facecolor='#B3E6FF') # 添加蓝色海洋
  ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.8,edgecolor='#0BB6FF') # 添加海岸线
  #ax.add_feature(cfeature.RIVERS.with_scale('50m'), linewidth=0.4, zorder=10) # 添加河流

  # 将中国区域陆地填充为白色
  ax.add_geometries(get_adm_maps(level='国',only_polygon=True), crs=ccrs.PlateCarree(), edgecolor='white', facecolor='white',zorder=10)
  
  print("(2/9) plot_base_map --> finished!")
  return fig, ax, gs


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
  ax_contours = ax.contourf(lon, lat, data, levels=var_details['levels'], extend='max', colors=var_details['colors'],transform=ccrs.PlateCarree(),zorder=11)
  
  # 添加国界线
  draw_maps(get_adm_maps(level='国'), linewidth=1.3, color='black',zorder=12)
  
  print(f"(3/9) {var_details['name']} plot_contourf --> finished!")
  return ax_contours


def plot_colorbar(var_details,fig,gs,ax_contours):
  # ---------- 绘制图例 ----------
  # 创建颜色条，指定cax为cbar_ax，同时禁用cbar_ax边框
  cbar_ax = fig.add_subplot(gs[1])  # 将颜色条绘制在gs[1]区域
  cbar_ax.set_position([0.2, 0.06, 0.6, 0.02])  # 明确设置颜色条位置，覆盖cbar_ax
  #cbar_ax.axis('off')  # 隐藏cbar_ax的坐标轴框线
  
  # 将颜色条绘制在cbar_ax里
  cbar = fig.colorbar(
    ax_contours, 
    cax=cbar_ax, 
    orientation='horizontal',  # colorbar的摆放方向,可以是 'horizontal'(水平)或 'vertical'(垂直)
    pad = 0.2,
    shrink=0.2,  # 控制颜色条的缩放比例，值应在 0 到 1 之间。1 表示颜色条的长度与子图相同
    aspect=60,  # 控制颜色条的长宽比,值越大,colorbar越扁平(水平)或窄细(垂直)
  )
  
  cbar.set_ticks(var_details['levels'])
  cbar.ax.tick_params(labelsize=11)
  cbar.set_label(f"雷达反射率 ({var_details['unit']})", fontsize=12)

  print(f"(7/9) {var_details['name']} plot_colorbar --> finished!")


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
  draw_maps(get_adm_maps(level='省'), linewidth=0.5, color='#818181',zorder=13)

  # ---------- 添加省份名称 ----------
  if name_open == 1:
    id        = get_adm_names(level='省')  # 获取地名列表
    shp_info  = get_adm_maps(level='省', engine='geopandas') #获取地名的GeoDataFrame对象
    for x, y, label in zip(shp_info.geometry.centroid.x, shp_info.geometry.centroid.y, id): #添加地名名称
      ax.text(x, y, label, fontsize = 11, ha='left',transform=ccrs.PlateCarree(),zorder=14) #,bbox = dict(facecolor='red', alpha=0.5))
  
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
  sub_ax = fig.add_axes([0, 0.1, 0.23, 0.26], projection=proj)
  
  # 设置边框线的颜色
  for spine in sub_ax.spines.values():
    spine.set_edgecolor('black')
      
  # 设置南海经纬度范围 
  sub_ax.set_extent([105.2, 120, 2, 23],crs=ccrs.PlateCarree())
  # 绘制地图要素
  sub_ax.add_feature(cfeature.LAND, facecolor='#E5E5E5') # 添加灰色陆地
  sub_ax.add_feature(cfeature.OCEAN, facecolor='#B3E6FF') # 添加蓝色海洋
  sub_ax.add_feature(cfeature.COASTLINE.with_scale('50m'),linewidth=0.6, edgecolor='#0BB6FF')

  # ---------- 绘制南海填色图 ----------
  # 将陆地填充为白色
  sub_ax.add_geometries(get_adm_maps(level='国',only_polygon=True), crs=ccrs.PlateCarree(), edgecolor='white', facecolor='white',zorder=10)
  # 绘制填色图
  sub_ax.contourf(lon, lat, data, levels=var_details['levels'], extend='max', colors=var_details['colors'],transform=ccrs.PlateCarree(),zorder=11)
  # 添加国界线
  draw_maps(get_adm_maps(level='国'), linewidth=0.8, color='black',zorder=12)
  # 添加省界线
  draw_maps(get_adm_maps(level='省'), linewidth=0.4, color='#818181',zorder=13)

  print("(5/9) plot_nanhai --> finished!")


def add_title(var_details,yyyymmddhhMM):
  '''
  增加图标题

  参数:
  - var_details: dict, 某变量的绘图信息字典,包含name,title,unit,levels,colors
  - yyyymmddhhMM: str, 绘图的时间

  返回:
  无返回,直接执行函数功能
  '''
  # ---------- 信息获取 ----------
  time_obj  = datetime.datetime.strptime(yyyymmddhhMM, '%Y%m%d%H%M')  # 时间信息获取
  time_str  = time_obj.strftime('%Y年%-m月%-d日%H时%M分')
  var_title = var_details['title']  # 标题信息获取
  
  # ---------- 添加图片标题 ----------
  plt.suptitle(var_title, fontsize=28, weight='bold', y=0.93)  # 第一行标题
  plt.text(0.5, 0.85, time_str, fontsize=20, ha='center', fontfamily='Nsimsun', transform=plt.gcf().transFigure)

  print(f"(6/9) {var_details['name']} add_title --> finished!")


def plot_variable(yyyymmddhhMM, variable, file_path, output_folder, output_sub_directory):
  '''
  主绘图函数,依次完成:读取nc文件--绘制map底图--绘制填色图--添加省份信息--添加标题--添加图例--保存图片

  参数:
  - yyyymmddhhMM: str, 绘图的时间
  - variable: str, 绘图的变量,来自文件名中命名
  - file_path: str, nc路径及文件名
  - output_folder: str, 图片的存储路径

  返回:
  直接生成图片,同时返回入库信息或None
  '''
  
  # ---------- 获取变量信息 ----------
  var_details = variable_info.get(variable)
  
  try:
    # 1.读取nc文件,数据格点过多时开启下采样
    data,lat,lon = read_ncfile(file_path,var_details,open_downsample=True,downsample_factor=10)

    # 2.绘制map底图
    fig, ax, gs = plot_base_map()

    # 3.绘制填色图
    ax_contours = plot_contourf(var_details,data,lat,lon,ax)

    # 4.添加省份边界线和名称,可选择开启省份名称1
    add_province_line_name(ax,1)
    
    # 5.绘制南海小地图及填色
    plot_nanhai(fig,lon,lat,data,var_details)

    # 6.添加标题
    add_title(var_details,yyyymmddhhMM)
    
    # 7.添加图例
    plot_colorbar(var_details,fig,gs,ax_contours)

    # 8.保存绘制的图像
    save_path = os.path.join(output_folder, f"{variable}_{yyyymmddhhMM}.png")
    fig.savefig(save_path)
    plt.close(fig)
    print(f"(8/9) Plot saved: {save_path}")
    
    # 9.生成入库信息
    save_sub_path = os.path.join(output_sub_directory, f"{variable}_{yyyymmddhhMM}.png")
    if os.path.exists(save_path):
        image_info = {
            "data_type": var_details['type'],
            "data_time": datetime.datetime.strptime(yyyymmddhhMM, "%Y%m%d%H%M"),
            'period': var_details['period'],
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
  获取当前时间,若小于30分,返回前一小时30分的时间,若大于30分,返回当前小时00分的时间

  参数：
  无

  返回:
  - latest_time: datetime.datetime, 00分或30分的时间
  '''
  # current_time = datetime.datetime.now()
  # current_minute = current_time.minute

  # # 判断当前分钟
  # if current_minute < 30:
  #   # 如果小于30分钟，返回前一个小时的30分
  #   latest_time = current_time - datetime.timedelta(hours=1)
  #   latest_time = latest_time.replace(minute=30, second=0, microsecond=0)
  # else:
  #   # 如果大于等于30分钟，返回当前小时的00分
  #   latest_time = current_time.replace(minute=0, second=0, microsecond=0)
  latest_time = time_data
  return latest_time


def process_variable(yyyymmddhhMM, variable, file_path, output_folder, output_sub_directory):
  '''
  处理每个变量的函数,检查nc文件存在并绘图

  参数:
  - yyyymmddhhMM: str, 绘图的时间
  - variable: str, 绘图的变量,来自文件名中命名
  - input_directory: str, nc文件的输入路径
  - output_folder: str, 图片的存储路径

  返回:
  返回入库信息或None
  '''

  # ---------- 检查nc文件存在 ----------
  try:
    if not os.path.exists(file_path):
      print(f"File {file_path} not found.")
      return
    
    # ---------- 启动绘图主程序 ----------
    onevar_image_info = plot_variable(yyyymmddhhMM, variable, file_path, output_folder, output_sub_directory)
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
  variable = config['variables'][0]
  output_directory = config['output_directory']
  
  # 获取需要的整点时间
  latest_time  = find_latest_time()
  yyyymmdd   = latest_time.strftime('%Y%m%d')
  yyyymmddhhMM = latest_time.strftime('%Y%m%d%H%M')
  # yyyymmdd = '20241023'
  # yyyymmddhhMM = '202410231700'
  
  output_sub_directory = os.path.join('pic_module/radar_obs', yyyymmdd[0:4], yyyymmdd[0:6], yyyymmdd)
  output_folder = os.path.join(output_directory, output_sub_directory)
  
  # ---------- 输出检查 ----------
  # 检查该时刻的输出文件夹是否存在,存在则覆盖绘制,不存在则创建文件夹并绘图
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  # ---------- 初始化入库信息 ----------
  image_info_list = []

  # ---------- 处理文件 ----------

  # 获取nc文件信息
  file_name = f"DOR_RDCP_LATLON_QREF_{yyyymmddhhMM}.nc"
  input_directory = config['input_directory']
  file_path = os.path.join(input_directory, yyyymmdd[0:4], yyyymmdd[0:6], yyyymmdd, file_name)
  try:
    onevar_image_info = process_variable(yyyymmddhhMM, variable, file_path, output_folder, output_sub_directory)
    if onevar_image_info is not None:
      image_info_list.append(onevar_image_info)
  except Exception as e:
    print(f"Failed to process {variable} due to an error: {e}")
  
  # ---------- 入库 ----------
  print("入库 ...")
  session = GetSession()
  nowtime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
  add_kwargs = dict(data_id=4, create_time=nowtime, update_time=nowtime)
  print(image_info_list)
  session_merge_from_records(session, PngRadarWeatherTable, image_info_list, **add_kwargs)
  session.close()

  return image_info_list


if __name__ == "__main__":
  # 脚本与相应配置文件请放置在同一个路径下
  config_path = './'
  config_name = 'radar_config.yaml'
  config_file = os.path.join(config_path,config_name)
  config = load_config(config_file)
  image_info_list = main(config)
  # print(image_info_list)
  
  print("FINISHED! 程序执行完毕")