# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:07:59

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, BigInteger, SmallInteger, Float, DateTime, Integer

class WarnRegionTable(Base):
    __tablename__ = 'warn_region_table'

    data_id     = Column(Integer, primary_key=True, comment='数据id')
    data_time   = Column(DateTime, primary_key=True, comment='告警时间')
    region_id   = Column(Integer, primary_key=True, comment='区域id')
    region_level= Column(SmallInteger, primary_key=True, comment='区域等级')
    type        = Column(SmallInteger, primary_key=True, comment='告警类型')
    value       = Column(Float, nullable=True, comment='根据告警类型来区分,如果高温,即温度值')
    level       = Column(SmallInteger, nullable=True, comment='告警级别')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='修改时间')

    def __repr__(self):
        return (
            f"<WarnRegionTable(region_id={self.region_id}, region_level={self.region_level}"
            f"data_id={self.data_id}, data_time={self.data_time}, "
            f"lat={self.lat}, lon={self.lon}, "
            f"type={self.type}, level={self.level}, value={self.value}, "
            f"create_time={self.create_time}, update_time={self.update_time}, "
            f")>")
