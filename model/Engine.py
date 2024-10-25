# -*- encoding: utf-8 -*-
'''
Created on 2024/10/21 18:02:51

@author: BOJUN WANG
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse
import pymysql

# 初始化 pymysql 替代 MySQLdb
pymysql.install_as_MySQLdb()

# 数据库连接信息
sql_info = {
    'host': '8.130.174.50',  # 主机
    'port': '3306',          # 端口
    'schema': 'bjdky_weather_com_platform',  # 数据库名称
    'user': 'root',          # 用户名
    'pw': urllib.parse.quote_plus("Tsingtaogiser+1s")  # URL编码后的密码
}

class CreateEngine:
    def __init__(self):
        # 初始化时创建数据库连接
        self.conn = self.conn_to_sql()

    def conn_to_sql(self):
        # 拼接数据库连接命令
        cmd = f"mysql://{sql_info['user']}:{sql_info['pw']}@{sql_info['host']}:{sql_info['port']}/{sql_info['schema']}"
        engine = create_engine(cmd)
        return engine

# 获取数据库连接引擎
def GetEngine():
    instance = CreateEngine()
    return instance.conn

# 获取 Session 用于数据库操作
def GetSession():
    engine = GetEngine()  # 获取引擎
    SessionMaker = sessionmaker(bind=engine)
    session = SessionMaker()  # 创建 session 实例
    return session