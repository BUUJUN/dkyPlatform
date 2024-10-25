# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:08:03

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, BigInteger, String, DateTime, Float, Integer, SmallInteger

class WinterForecastProductInfo(Base):
    __tablename__ = 'winter_forecast_product_info'
    
    region_id = Column(Integer, primary_key=True, comment='出图的区域')
    region_level = Column(SmallInteger, primary_key=True, comment='出图的区域级别')
    data_id = Column(SmallInteger, primary_key=True, comment='数据源')
    data_time = Column(DateTime, primary_key=True, comment='数据的预报时间')
    forecast_cycle = Column(DateTime, primary_key=True, comment='数据的发报时间')
    forecast_type = Column(SmallInteger, primary_key=True, comment='预报类型, 短临, 短期, 中期')
    forecast_step = Column(Integer, primary_key=True, comment='预报步长, 小时')
    forecast_timestr = Column(String(255), nullable=True, comment='预报时段, ymdh_ymdh')
    report_time = Column(DateTime, nullable=True, comment='报告生成时间')
    pre_avg = Column(Float, nullable=True, comment='降水平均值')
    pre_max = Column(Float, nullable=True, comment='降水最大值')
    pre_level_0 = Column(Float, nullable=True, comment='无降水所占比例')
    pre_level_1 = Column(Float, nullable=True, comment='小雨所占比例')
    pre_level_2 = Column(Float, nullable=True, comment='中雨所占比例')
    pre_level_3 = Column(Float, nullable=True, comment='大雨所占比例')
    pre_level_4 = Column(Float, nullable=True, comment='暴雨所占比例')
    pre_level_5 = Column(Float, nullable=True, comment='大暴雨所占比例')
    pre_level_6 = Column(Float, nullable=True, comment='特大暴雨所占比例')
    wins_avg = Column(Float, nullable=True, comment='风速平均值')
    wins_max = Column(Float, nullable=True, comment='风速最大值')
    wins_min = Column(Float, nullable=True, comment='风速最小值')
    wins_level_0 = Column(Float, nullable=True, comment='0级风速所占比例')
    wins_level_1 = Column(Float, nullable=True, comment='1级风速所占比例')
    wins_level_2 = Column(Float, nullable=True, comment='2级风速所占比例')
    wins_level_3 = Column(Float, nullable=True, comment='3级风速所占比例')
    wins_level_4 = Column(Float, nullable=True, comment='4级风速所占比例')
    wins_level_5 = Column(Float, nullable=True, comment='5级风速所占比例')
    wins_level_6 = Column(Float, nullable=True, comment='6级风速所占比例')
    wins_level_7 = Column(Float, nullable=True, comment='7级风速所占比例')
    wins_level_8 = Column(Float, nullable=True, comment='8级风速所占比例')
    wins_level_9 = Column(Float, nullable=True, comment='9级风速所占比例')
    temp_min = Column(Float, nullable=True, comment='气温最小值')
    temp_avg = Column(Float, nullable=True, comment='气温平均值')
    temp_max = Column(Float, nullable=True, comment='气温最大值')
    rh_min = Column(Float, nullable=True, comment='相对湿度最小值')
    rh_avg = Column(Float, nullable=True, comment='相对湿度平均值')
    rh_max = Column(Float, nullable=True, comment='相对湿度最大值')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='修改时间')

    def __repr__(self):
        return (f"<WinterForecastProductInfo(region_id={self.region_id}, region_level='{self.region_level}', "
                f"data_id='{self.data_id}', data_time='{self.data_time}', "
                f"forecast_cycle='{self.forecast_cycle}', forecast_type='{self.forecast_type}', "
                f"forecast_step='{self.forecast_step}', forecast_timestr='{self.forecast_timestr}', "
                f"report_time='{self.report_time}', pre_avg='{self.pre_avg}', pre_max='{self.pre_max}', "
                f"pre_level_0='{self.pre_level_0}', pre_level_1='{self.pre_level_1}', "
                f"pre_level_2='{self.pre_level_2}', pre_level_3='{self.pre_level_3}', "
                f"pre_level_4='{self.pre_level_4}', pre_level_5='{self.pre_level_5}', "
                f"pre_level_6='{self.pre_level_6}', wins_avg='{self.wins_avg}', "
                f"wins_max='{self.wins_max}', wind_min='{self.wind_min}', "
                f"wins_level_0='{self.wins_level_0}', wins_level_1='{self.wins_level_1}', "
                f"wins_level_2='{self.wins_level_2}', wins_level_3='{self.wins_level_3}', "
                f"wins_level_4='{self.wins_level_4}', wins_level_5='{self.wins_level_5}', "
                f"wins_level_6='{self.wins_level_6}', wins_level_7='{self.wins_level_7}', "
                f"wins_level_8='{self.wins_level_8}', wins_level_9='{self.wins_level_9}', "
                f"temp_min='{self.temp_min}', temp_avg='{self.temp_avg}', temp_max='{self.temp_max}', "
                f"rh_min='{self.rh_min}', rh_avg='{self.rh_avg}', rh_max='{self.rh_max}', "
                f"create_time='{self.create_time}', update_time='{self.update_time}', "
                f")>")
