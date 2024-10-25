# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:07:15

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, Integer, String, DateTime, Float

class ForecastDataDetailTable(Base):
    __tablename__ = 'forecast_data_detail_table'

    data_id     = Column(Integer, primary_key=True, autoincrement=True, comment='数据id')
    name        = Column(String(64), nullable=True, comment='数据名称')
    fb_time_str = Column(String(64), nullable=True, comment='发报时间描述')
    fb_length   = Column(Integer, nullable=True, comment='发报时长')
    data_time_str = Column(String(64), nullable=True, comment='数据时间描述')
    period      = Column(Integer, nullable=True, comment='数据时间粒度')
    path        = Column(String(64), nullable=True, comment='文件存储路径')
    naming      = Column(String(32), nullable=True, comment='文件命名')
    suffix      = Column(String(8), nullable=True, comment='数据格式')
    region_id   = Column(Integer, nullable=True, comment='区域代号')
    resolution  = Column(Float, nullable=True, comment='分辨率')
    max_x       = Column(Float, nullable=True, comment='四角坐标maxX')
    max_y       = Column(Float, nullable=True, comment='四角坐标maxY')
    min_x       = Column(Float, nullable=True, comment='四角坐标minX')
    min_y       = Column(Float, nullable=True, comment='四角坐标minY')
    desc        = Column(String(200), nullable=True, comment='数据描述')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='修改时间')

    def __repr__(self):
        return (
            f"<ForecastDataDetailTable(data_id={self.data_id}, "
            f"fb_time_str={self.fb_time_str}, fb_length={self.fb_length}, "
            f"data_time_str={self.data_time_str}, period={self.period}, "
            f"region_id={self.region_id}, )>")
