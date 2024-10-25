#!/bin/bash

py_interpreter="/home/gpusr/miniconda3/envs/dky_platform/bin/python"
py_scripts_dir="/home/gpusr/user/wangbj/dkyPlatform"

cd "$py_scripts_dir"

current_time=$(date +"%Y-%m-%d %H:%M:%S")
hour=$(date +"%H")

echo "START TIME: $current_time"

# 预报相关的组件
if [ "$hour" -eq 8 ]; then
    echo "预报绘图组件启动"
    echo "START TIME: $current_time" >> runlogs/plot_fore.log
    $py_interpreter plot_fore.py >> runlogs/plot_fore.log 2>&1 &
    
    echo "预警绘图组件启动"
    echo "START TIME: $current_time" >> runlogs/plot_fore.log
    $py_interpreter plot_fore_warn.py >> runlogs/plot_fore_warn.log 2>&1 &

    echo "预报报告组件启动"
    echo "START TIME: $current_time" >> runlogs/report_fore.log
    # 短临
    $py_interpreter report_GJD_exec.py --length 24 --interval 3 >> runlogs/report_fore.log 2>&1 &
    # 短期
    $py_interpreter report_GJD_exec.py --length 72 --interval 24 >> runlogs/report_fore.log 2>&1 &
    # 中期
    $py_interpreter report_GJD_exec.py --length 168 --interval 24 >> runlogs/report_fore.log 2>&1 &
fi

# 实况相关的组件
echo "实况绘图组件启动"
echo "START TIME: $current_time" >> runlogs/plot_obs.log
$py_interpreter plot_obs.py >> runlogs/plot_obs.log 2>&1 &

echo "雷达绘图组件启动"
echo "START TIME: $current_time" >> runlogs/plot_radar.log
$py_interpreter plot_radar.py >> runlogs/plot_radar.log 2>&1 &

echo "实况告警组件启动"
echo "START TIME: $current_time" >> runlogs/warn_obs.log
$py_interpreter warn_obs_hourly.py >> runlogs/warn_obs.log 2>&1 &

if [ "$hour" -eq 1 ]; then
    echo "实况统计组件启动"
    echo "START TIME: $current_time" >> runlogs/statis_obs.log
    $py_interpreter statis_obs_daily.py >> runlogs/statis_obs.log 2>&1 &
fi

echo "END TIME: $current_time"
