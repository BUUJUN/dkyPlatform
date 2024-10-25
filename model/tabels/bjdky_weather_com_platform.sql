/*
 Navicat Premium Dump SQL

 Source Server         : electricty_exhibition
 Source Server Type    : MySQL
 Source Server Version : 80026 (8.0.26)
 Source Host           : 8.130.174.50:3306
 Source Schema         : bjdky_weather_com_platform

 Target Server Type    : MySQL
 Target Server Version : 80026 (8.0.26)
 File Encoding         : 65001

 Date: 22/10/2024 10:32:26
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for forecast_data_detail_table
-- ----------------------------
DROP TABLE IF EXISTS `forecast_data_detail_table`;
CREATE TABLE `forecast_data_detail_table`  (
  `data_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '数据id',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据名称',
  `fb_time_str` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发报时间描述',
  `fb_length` int NULL DEFAULT NULL COMMENT '发报时长',
  `data_time_str` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据时间描述',
  `period` tinyint NULL DEFAULT NULL COMMENT '数据时间粒度',
  `path` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件存储路径',
  `naming` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件命名',
  `suffix` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据格式',
  `region_id` int NULL DEFAULT NULL COMMENT '区域代号',
  `resolution` double NULL DEFAULT NULL COMMENT '分辨率',
  `max_x` double NULL DEFAULT NULL COMMENT '四角坐标maxX',
  `max_y` double NULL DEFAULT NULL COMMENT '四角坐标maxY',
  `min_x` double NULL DEFAULT NULL COMMENT '四角坐标minX',
  `min_y` double NULL DEFAULT NULL COMMENT '四角坐标minY',
  `desc` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据描述',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`data_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '预报数据详情表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for png_cloud_weather_table
-- ----------------------------
DROP TABLE IF EXISTS `png_cloud_weather_table`;
CREATE TABLE `png_cloud_weather_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据详情id',
  `data_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据类型',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径-相对路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '实况云图图片存储表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for png_forecast_weather_table
-- ----------------------------
DROP TABLE IF EXISTS `png_forecast_weather_table`;
CREATE TABLE `png_forecast_weather_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据详情id',
  `data_type` tinyint NULL DEFAULT NULL COMMENT '数据类型,7种,',
  `fb_time` datetime NULL DEFAULT NULL COMMENT '发报时间',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径-相对路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '气象预报图片存储表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for png_radar_weather_table
-- ----------------------------
DROP TABLE IF EXISTS `png_radar_weather_table`;
CREATE TABLE `png_radar_weather_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据详情id',
  `data_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据类型',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径-相对路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '雷达图片存储表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for png_real_weather_table
-- ----------------------------
DROP TABLE IF EXISTS `png_real_weather_table`;
CREATE TABLE `png_real_weather_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据详情id',
  `data_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据类型',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径-相对路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '气象实况图片存储表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for png_warn_weather_table
-- ----------------------------
DROP TABLE IF EXISTS `png_warn_weather_table`;
CREATE TABLE `png_warn_weather_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据详情id',
  `data_type` tinyint NULL DEFAULT NULL COMMENT '数据类型,7种,',
  `fb_time` datetime NULL DEFAULT NULL COMMENT '发报时间',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `file_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件路径-相对路径',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '气象预警图片存储表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for real_data_detail_table
-- ----------------------------
DROP TABLE IF EXISTS `real_data_detail_table`;
CREATE TABLE `real_data_detail_table`  (
  `data_id` int UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '数据id',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据名称',
  `data_time_str` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据时间',
  `period` tinyint NULL DEFAULT NULL COMMENT '数据尺度',
  `path` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件存储路径',
  `naming` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件命名',
  `suffix` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件格式',
  `region_id` int NULL DEFAULT NULL COMMENT '区域代码',
  `resolution` double NULL DEFAULT NULL COMMENT '分辨率',
  `max_x` double NULL DEFAULT NULL COMMENT '四角坐标maxX',
  `max_y` double NULL DEFAULT NULL COMMENT '四角坐标maxY',
  `min_x` double NULL DEFAULT NULL COMMENT '四角坐标minX',
  `min_y` double NULL DEFAULT NULL COMMENT '四角坐标minY',
  `desc` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据描述',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`data_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '实况数据详情表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for stat_device_table
-- ----------------------------
DROP TABLE IF EXISTS `stat_device_table`;
CREATE TABLE `stat_device_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `device_id` int NULL DEFAULT NULL COMMENT '设备id',
  `device_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备名称',
  `device_type` tinyint NULL DEFAULT NULL COMMENT '设备类型',
  `data_id` int NULL DEFAULT NULL COMMENT '数据id',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `period` tinyint NULL DEFAULT NULL COMMENT '数据时间粒度,',
  `lon` double NULL DEFAULT NULL COMMENT '纬度',
  `lat` double NULL DEFAULT NULL COMMENT '经度',
  `avg_temp` double NULL DEFAULT NULL COMMENT '平均温度',
  `max_temp` double NULL DEFAULT NULL COMMENT '最高温度',
  `min_temp` double NULL DEFAULT NULL COMMENT '最低温度',
  `prec_statistics` double NULL DEFAULT NULL COMMENT '降水量统计',
  `extreme_prec_statistics` double NULL DEFAULT NULL COMMENT '极端降水统计',
  `wind_speed_dir_statistics` double NULL DEFAULT NULL COMMENT '风速、风向统计',
  `hum_statistics` double NULL DEFAULT NULL COMMENT '湿度统计',
  `pressure_statistics` double NULL DEFAULT NULL COMMENT '气压统计',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '基于电力设备坐标的统计' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for stat_region_table
-- ----------------------------
DROP TABLE IF EXISTS `stat_region_table`;
CREATE TABLE `stat_region_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `region_id` int NULL DEFAULT NULL COMMENT '区域id',
  `data_id` int NULL DEFAULT NULL COMMENT '数据id',
  `data_time` datetime NULL DEFAULT NULL COMMENT '数据时间',
  `period` tinyint NULL DEFAULT NULL COMMENT '数据时间粒度',
  `avg_temp` double NULL DEFAULT NULL COMMENT '平均温度',
  `max_temp` double NULL DEFAULT NULL COMMENT '最高温度',
  `min_temp` double NULL DEFAULT NULL COMMENT '最低温度',
  `prec_statistics` double NULL DEFAULT NULL COMMENT '降水量统计',
  `extreme_prec_statistics` double NULL DEFAULT NULL COMMENT '极端降水统计',
  `wind_speed_dir_statistics` double NULL DEFAULT NULL COMMENT '风速、风向统计',
  `hum_statistics` double NULL DEFAULT NULL COMMENT '湿度统计',
  `pressure_statistics` double NULL DEFAULT NULL COMMENT '气压统计',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '基于行政区划的统计（市-省）' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for warn_device_table
-- ----------------------------
DROP TABLE IF EXISTS `warn_device_table`;
CREATE TABLE `warn_device_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `type` tinyint NULL DEFAULT NULL COMMENT '告警类型',
  `value` double NULL DEFAULT NULL COMMENT '根据告警类型来区分,如果高温,即温度值',
  `data_time` datetime NULL DEFAULT NULL COMMENT '告警时间',
  `level` tinyint NULL DEFAULT NULL COMMENT '告警级别',
  `data_id` int NULL DEFAULT NULL COMMENT '数据id',
  `device_id` int NULL DEFAULT NULL COMMENT '设备id',
  `device_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备名称',
  `device_type` tinyint NULL DEFAULT NULL COMMENT '设备类型',
  `lat` double NULL DEFAULT NULL COMMENT '设备经纬度',
  `lon` double NULL DEFAULT NULL COMMENT '设备经纬度',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '基于电力设备坐标的告警' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for warn_region_table
-- ----------------------------
DROP TABLE IF EXISTS `warn_region_table`;
CREATE TABLE `warn_region_table`  (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `type` tinyint NULL DEFAULT NULL COMMENT '告警类型',
  `value` double NULL DEFAULT NULL COMMENT '根据告警类型来区分,如果高温,即温度值',
  `data_time` datetime NULL DEFAULT NULL COMMENT '告警时间',
  `level` tinyint NULL DEFAULT NULL COMMENT '告警级别',
  `data_id` int NULL DEFAULT NULL COMMENT '数据id',
  `region_id` int NULL DEFAULT NULL COMMENT '区域id',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '基于区域的告警' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for winter_forecast_product_info
-- ----------------------------
DROP TABLE IF EXISTS `winter_forecast_product_info`;
CREATE TABLE `winter_forecast_product_info`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `data_from` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据源',
  `forecast_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '预报的类型,是短临还是短期，中期',
  `region_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '出图的区域级别 1-省 2-省方向 3-市 4-市方向 5-区县',
  `region` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '出图的区域',
  `forecast_step` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '预报步长',
  `forecast_imminent_tag` int NULL DEFAULT NULL COMMENT '短临小时气象要素标注',
  `forecast_cycle_utc` datetime NULL DEFAULT NULL COMMENT 'EC预报文件夹,或者初始场',
  `forecast_report_time` datetime NULL DEFAULT NULL COMMENT '发报时间',
  `forecast_timestr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '预报的时段',
  `forecast_figure_timestr` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '预报时段,每一张图',
  `area` float NULL DEFAULT NULL COMMENT '统计区域面积',
  `pre_max` float NULL DEFAULT NULL COMMENT '降水最大值',
  `pre_avg` float NULL DEFAULT NULL COMMENT '降水平均值',
  `wind_max` float NULL DEFAULT NULL COMMENT '风速最大值',
  `wind_avg` float NULL DEFAULT NULL COMMENT '风速平均值',
  `wind_min` float NULL DEFAULT NULL COMMENT '风速最小值',
  `cape_max` float NULL DEFAULT NULL COMMENT '位能最大值',
  `cape_avg` float NULL DEFAULT NULL COMMENT '位能平均值',
  `pre_level_0` float NULL DEFAULT NULL COMMENT '无降水所占比例',
  `pre_level_1` float NULL DEFAULT NULL COMMENT '小雨所占比例',
  `pre_level_2` float NULL DEFAULT NULL COMMENT '中雨所占比例',
  `pre_level_3` float NULL DEFAULT NULL COMMENT '大雨所占比例',
  `pre_level_4` float NULL DEFAULT NULL COMMENT '暴雨所占比例',
  `pre_level_5` float NULL DEFAULT NULL COMMENT '大暴雨所占比例',
  `pre_level_6` float NULL DEFAULT NULL COMMENT '特大暴雨所占比例',
  `cape_low_risk` float NULL DEFAULT NULL COMMENT '位能低风险所占比例',
  `cape_high_risk` float NULL DEFAULT NULL COMMENT '位能高风险所占比例',
  `wins_level9` float NULL DEFAULT NULL COMMENT '9级风速所占比例',
  `wins_level8` float NULL DEFAULT NULL COMMENT '8级风速所占比例',
  `wins_level7` float NULL DEFAULT NULL COMMENT '7级风速所占比例',
  `wins_level6` float NULL DEFAULT NULL COMMENT '6级风速所占比例',
  `wins_level5` float NULL DEFAULT NULL COMMENT '5级风速所占比例',
  `wins_level4` float NULL DEFAULT NULL COMMENT '4级风速所占比例',
  `wins_level3` float NULL DEFAULT NULL COMMENT '3级风速所占比例',
  `wins_level2` float NULL DEFAULT NULL COMMENT '2级风速所占比例',
  `wins_level1` float NULL DEFAULT NULL COMMENT '1级风速所占比例',
  `wins_level0` float NULL DEFAULT NULL COMMENT '0级风速所占比例',
  `temp_min` float NULL DEFAULT NULL COMMENT '气温最小值',
  `temp_avg` float NULL DEFAULT NULL COMMENT '气温平均值',
  `temp_max` float NULL DEFAULT NULL COMMENT '气温最大值',
  `rh_min` float NULL DEFAULT NULL COMMENT '相对湿度最小值',
  `rh_avg` float NULL DEFAULT NULL COMMENT '相对湿度平均值',
  `rh_max` float NULL DEFAULT NULL COMMENT '相对湿度最大值',
  `snow_level0` float NULL DEFAULT NULL COMMENT '无降雪所占比例',
  `snow_level1` float NULL DEFAULT NULL COMMENT '小雪所占比例',
  `snow_level2` float NULL DEFAULT NULL COMMENT '中雪所占比例',
  `snow_level3` float NULL DEFAULT NULL COMMENT '大雪所占比例',
  `snow_level4` float NULL DEFAULT NULL COMMENT '暴雪所占比例',
  `snow_level5` float NULL DEFAULT NULL COMMENT '大暴雪所占比例',
  `snow_level6` float NULL DEFAULT NULL COMMENT '特大暴雪所占比例',
  `snow_min` float NULL DEFAULT NULL COMMENT '最小降雪',
  `snow_avg` float NULL DEFAULT NULL COMMENT '平均降雪',
  `snow_max` float NULL DEFAULT NULL COMMENT '最大降雪',
  `sleet_level0` float NULL DEFAULT NULL COMMENT '无雨夹雪占比',
  `sleet_level1` float NULL DEFAULT NULL COMMENT '小雨夹雪占比',
  `sleet_level2` float NULL DEFAULT NULL COMMENT '中雨夹雪占比',
  `sleet_level3` float NULL DEFAULT NULL COMMENT '大雨夹雪占比',
  `sleet_min` float NULL DEFAULT NULL COMMENT '雨夹雪最小值',
  `sleet_avg` float NULL DEFAULT NULL COMMENT '雨夹雪平均值',
  `sleet_max` float NULL DEFAULT NULL COMMENT '雨夹雪最大值',
  `forecast_exec_time` datetime NULL DEFAULT NULL COMMENT '执行时间',
  `temp_time_max` float NULL DEFAULT NULL COMMENT '时间上最高温',
  `temp_time_avg` float NULL DEFAULT NULL COMMENT '时间上平均温度',
  `temp_time_min` float NULL DEFAULT NULL COMMENT '时间上最低温',
  `thunder_no_risk` float NULL DEFAULT NULL COMMENT '雷电无风险比例',
  `thunder_mid_risk` float NULL DEFAULT NULL COMMENT '雷电中风险比例',
  `thunder_high_risk` float NULL DEFAULT NULL COMMENT '雷电高风险比例',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `index_forecastCycleUtc_forecastReportTime`(`forecast_cycle_utc` ASC, `forecast_report_time` ASC) USING BTREE,
  INDEX `index_time`(`data_from` ASC, `forecast_type` ASC, `region_level` ASC, `forecast_step` ASC, `forecast_report_time` ASC, `forecast_figure_timestr` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '报告数据表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
