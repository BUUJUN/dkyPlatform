# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:07:49

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, Float, DateTime

class StatRegionTable(Base):
    __tablename__ = 'stat_region_table'

    region_id   = Column(Integer, primary_key=True, comment='区域id')
    region_level= Column(SmallInteger, primary_key=True, comment='区域等级')
    data_id     = Column(Integer, primary_key=True, comment='数据id')
    data_time   = Column(DateTime, primary_key=True, comment='数据时间')
    period      = Column(SmallInteger, primary_key=True, comment='数据时间粒度')
    avg_temp    = Column(Float, nullable=True, comment='平均温度')
    max_temp    = Column(Float, nullable=True, comment='最高温度')
    min_temp    = Column(Float, nullable=True, comment='最低温度')
    precipitation = Column(Float, nullable=True, comment='降水量统计')
    extreme_prec = Column(Float, nullable=True, comment='极端降水统计')
    wind_speed  = Column(Float, nullable=True, comment='风速统计')
    wind_direction = Column(Float, nullable=True, comment='风向统计')
    relative_humidity = Column(Float, nullable=True, comment='湿度统计')
    pressure    = Column(Float, nullable=True, comment='气压统计')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='修改时间')

    def __repr__(self):
        return (
            f"<StatRegionTable(region_id={self.region_id}, region_level={self.region_level}, "
            f"data_id={self.data_id}, data_time={self.data_time}, period={self.period}, "
            f"avg_temp={self.avg_temp}, max_temp={self.max_temp}, min_temp={self.min_temp}, "
            f"precipitation={self.precipitation}, extreme_prec={self.extreme_prec}, "
            f"wind_speed={self.wind_speed}, wind_direction={self.wind_direction}, "
            f"relative_humidity={self.relative_humidity}, pressure={self.pressure}," 
            f"create_time={self.create_time}, update_time={self.update_time}, "
            f")>")
