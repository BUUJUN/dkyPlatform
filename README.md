### 中国电科院共性平台技术说明

#### 执行主程序

1. **图片组件**
    
    实况图: `plot_obs.py`
    预报图: `plot_fore.py`
    预警图: `plot_fore_warn.py`
    雷达图: `plot_radar.py`

2. **统计组件**
    `statis_obs_daily.py`

3. **告警组件**
    `warn_obs_hourly.py`

4. **报告组件**
    `report_GJD_exec.py`

#### 参数设置

1. **图片组件**
   
   - `fore_config.yaml`
   - `fore_warn_config.yaml`
   - `obs_config.yaml`
   - `radar_config.yaml`

    设置 `input_directory` 参数，指定**输入数据**目录
    设置 `output_directory` 参数，指定**输出图片**目录
   
2. **统计、告警、报告组件**
   
   - `configs/un_config.py`
   
    设置 `input_directory_GJD`，指定**输入高精度预报数据**目录
    设置 `input_directory_5km`，指定**输入5km实况数据**目录
    设置 `input_directory_1km`，指定**输入1km实况数据**目录
    设置 `output_prefix`，指定中间生成数据目录

    设置 `shape_sta`，指定**电力设备坐标矢量**路径

#### 自动运行逻辑

1. **图片组件**
    
    - 实况图片: 逐小时运行，绘制当前时刻一小时内气象实况，滞后 35 分钟
    
    - 预报图片：逐日运行，每日 08 时运行一次，绘制未来 3 日逐日预报，所用预报数据起报时间为前一日 20时 (12Z) 
    
    - 预警图片: 逐日运行，每日 08 时运行一次，绘制未来 3 日逐日预警，所用预报数据起报时间为前一日 20时 (12Z) 

    - 雷达图片: 逐小时运行，绘制当前时刻半小时雷达实况，滞后 35 分钟
    

2. **统计组件**
    
    - 日统计: 逐日运行，每日 01 时运行一次，统计前一天气象实况
    
    - 月度统计: 逐月运行，每月第一天运行一次，统计前一月气象实况
     
    - 季度统计: 逐季度运行，1、4、7、10月第一天运行一次，统计前一季度气象实况
    
    - 年度统计: 逐年运行，每年 1月1日 运行一次，统计前一年气象实况

3. **告警组件**
    
    逐小时运行，计算当前时刻一小时内告警信息，滞后 35 分钟

4. **报告组件**
    
    逐日运行，每日 08 时运行一次，统计未来短临、短期和中期预报信息，所用预报数据起报时间为前一日 20时 (12Z) 


#### 手动运行指南

1. **图片组件**
   
   设置 `--time` 参数指定实况绘图或预报预警绘图的**执行时间**，参数格式为 `yyyymmddhh`，如：

    ```bash
    python plot_fore.py --time 2024010112   # 绘制 2024年01月01日起 的未来三天预报图
    python plot_obs.py --time 2024010112    # 绘制 2024年01月01日12时 的实况图
    ```

2. **统计组件**
   
   设置 `--time` 参数指定统计的**开始时间**，参数格式为 `yyyymmddhh`；
   设置 `--period` 参数指定统计的**时间粒度单位**，包括天、月、季度和年度，参数格式为对应英文 `day`、`month`、`quarter` 和 `year`；
   设置 `--length` 参数指定所用统计的**时间长度**，参数格式为数字；
   设置 `--interval` 参数指定所用统计的**时间间隔**，参数格式为数字；

   如，对 2024年01月内 逐日进行统计：

    ```bash
    python statis_obs_daily.py --time 2024010100  --period day --length 31 --interval 1
    ```


3. **告警组件**
   
   设置 `--time` 参数指定所用**实况数据开始时间**，参数格式为 `yyyymmddhh`；

   如，对 2024年01月01日00时 数据计算告警信息：

    ```bash
    python warn_obs_hourly.py --time 2024010100
    ```

4. **报告组件**
   
   设置 `--time` 参数指定预报报告的**执行时间**，参数格式为 `yyyymmddhh`；
   设置 `--length` 参数指定报告的**时间长度**，参数格式为数字；
   设置 `--interval` 参数指定报告的**时间间隔**，参数格式为数字；

   一般地，
   
        短临为 未来 24 小时，间隔 1 小时；
        短期为 未来 72 小时，间隔 24 小时；
        中期为 未来 168 小时（7天），间隔 24 小时

   如，指定 2024年 01月 01日 生成报告

    ```bash
    python report_GJD_exec.py --time 2024010108 --length 24 --interval 1    # 短临
    python report_GJD_exec.py --time 2024010108 --length 72 --interval 24   # 短期
    python report_GJD_exec.py --time 2024010108 --length 168 --interval 24  # 中期
    ```

#### 其他

1. 本算法所用的 python 版本为 3.9.7，`requirements.txt` 为本算法所需要的 python 依赖库

2. 所用组件的启动脚本：`start.sh`

3. `Cron` 定时作业设置: `cron.txt`

4. 程序运行的日志: `runlogs`