# -*- encoding: utf-8 -*-
'''
Created on 2024/10/23 09:31:16

@author: BOJUN WANG
'''
import datetime
import numpy as np
import pandas as pd
from typing import Union
from sqlalchemy.exc import IntegrityError

from .Engine import GetSession
from configs import get_time_type, check_time_info

def session_merge_from_df(session, table, df, cols=None, keys=None, **kwargs):
    
    if cols is not None:
        df = df[cols]
    if keys is not None:
        df = df.rename(columns={col:key for col,key in zip(df.columns, keys)})
    
    records = df.to_dict(orient='records')
    
    for rec in records:
        rec.update(kwargs)
        try:
            session.merge(table(**rec))
            session.commit()
        except IntegrityError:
            session.rollback()
            print("[ERROR] 入库失败:", rec)
    
    return

def session_merge_from_records(session, table, records:list[dict], cols=None, keys=None, **kwargs):
    records_df = pd.DataFrame(records)
    if cols is not None:
        records_df = records_df[cols]
    if keys is not None:
        records_df = records_df.rename(columns={col:key for col,key in zip(records_df.columns, keys)})
    
    records = records_df.to_dict(orient='records')
    for rec in records:
        rec.update(kwargs)
        try:
            session.merge(table(**rec))
            session.commit()
        except IntegrityError:
            session.rollback()
            print("[ERROR] 入库失败:", rec)
    
    
    return None

def session_clear_all(table):
    session = GetSession()
    try:
        session.query(table).delete()
        session.commit()
        print(f"{table} 表中的所有数据已被清空。")
    except Exception as e:
        session.rollback()  # 发生错误时回滚
        print(f"清空数据时发生错误: {e}")
    finally:
        session.close()
    return


def session_extract_data(
    table, 
    time_start:  	Union[datetime.datetime, pd.Timestamp],
    time_length:   	int,
    time_interval:  int,
    time_type: 		str):
    
    # 输入信息标准化
    time_start = pd.to_datetime(time_start)
    time_interval = int(time_interval)
    time_length = int(time_length)
    time_type = get_time_type(time_type)
    time_period = f'{time_interval}{time_type}'
    
    checkout = check_time_info(time_start, time_length, time_interval, time_period)
    
    if checkout is None:
        return None
    
    time_start = checkout['time_start']
    time_end = checkout['time_end']
    time_interval = checkout['time_interval']
    time_length = checkout['time_length']
    time_range = checkout['time_range']
    
    session = GetSession()
    query_list = []
    
    for i, _ in enumerate(time_range):
        if i == 0:
            continue
        tstart = time_range[i-1]
        tend = time_range[i] + pd.Timedelta(days=-1)
        
        query_out = (
            session.query(table).filter(table.period == 1)
            .filter(table.data_time.between(tstart, tend)).all()
        )
        
        query_df = pd.DataFrame.from_records([row.__dict__ for row in query_out])
        # 移除 SQLAlchemy 的内部属性
        query_df = query_df.drop(columns=['_sa_instance_state'], errors='ignore')
        
        if query_df.empty:
            print(f"{tstart.strftime('%Y-%m-%d')} 至 {tend.strftime('%Y-%m-%d')} 无记录")
        
        else:
            print(f"{tstart.strftime('%Y-%m-%d')} 至 {tend.strftime('%Y-%m-%d')} 查询到 {len(query_df)} 条记录")
            query_list.append(query_df)
        
    session.close()
    
    return query_list