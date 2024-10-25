# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:07:24

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, DateTime

class PngForecastWeatherTable(Base):
    __tablename__ = 'png_forecast_weather_table'
    
    data_id     = Column(Integer, nullable=True, primary_key=True, comment='数据详情id')
    data_type   = Column(SmallInteger, nullable=True, primary_key=True, comment='数据类型,7种')
    fb_time     = Column(DateTime, nullable=True, primary_key=True, comment='发报时间')
    data_time   = Column(DateTime, nullable=True, primary_key=True, comment='数据时间')
    period      = Column(SmallInteger, nullable=True, primary_key=True, comment='数据时间粒度')
    file_path   = Column(String(255), nullable=True, comment='文件路径-相对路径')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='更新时间')

    def __repr__(self):
        return (f"<PngForecastWeatherTable(data_id={self.data_id}, data_type={self.data_type}, "
                f"fb_time={self.fb_time}, data_time={self.data_time}, period={self.period}, "
                f"file_path={self.file_path}, create_time={self.create_time}, update_time={self.update_time})>")
