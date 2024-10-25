# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:07:53

@author: BOJUN WANG
'''
from ..Base import Base
from sqlalchemy import Column, BigInteger, SmallInteger, Float, DateTime, Integer, String

class WarnDeviceTable(Base):
    __tablename__ = 'warn_device_table'
    
    data_id     = Column(Integer, primary_key=True, comment='数据id')
    data_time   = Column(DateTime, primary_key=True, comment='告警时间')
    device_id   = Column(Integer, primary_key=True, comment='设备id')
    device_type = Column(SmallInteger, primary_key=True, comment='设备类型')
    device_name = Column(String(32), nullable=True, comment='设备名称')
    lat         = Column(Float, nullable=True, comment='设备经纬度')
    lon         = Column(Float, nullable=True, comment='设备经纬度')
    type        = Column(SmallInteger, primary_key=True, comment='告警类型')
    value       = Column(Float, nullable=True, comment='根据告警类型来区分,如果高温,即温度值')
    level       = Column(SmallInteger, nullable=True, comment='告警级别')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_time = Column(DateTime, nullable=True, comment='修改时间')

    def __repr__(self):
        return (
            f"<WarnDeviceTable(device_id={self.device_id}, device_type={self.device_type}, device_name={self.device_name}, "
            f"data_id={self.data_id}, data_time={self.data_time}, "
            f"lat={self.lat}, lon={self.lon}, "
            f"type={self.type}, level={self.level}, value={self.value}, "
            f"create_time={self.create_time}, update_time={self.update_time}, "
            f")>")
