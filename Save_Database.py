# -*- coding: utf-8 -*-
import MySQLdb as mdb
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

user_id = 'root'
user_pass = 'endeoddl2*'
host = '127.0.0.1'
database = 'youtube_comments'

class upload_db:
    def make_db_connect(self, user_id, user_pass, host, database):
        engine = create_engine("mysql+mysqldb://{}:{}@{}/{}?charset=utf8".format(user_id, user_pass, host, database), encoding='utf-8')
        conn = engine.connect()
        return engine, conn
    
    def upload_database(self, table, table_name):
        ###sql 연결
        engine, conn = self.make_db_connect(user_id, user_pass, host, database)
        table.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        conn.close()
    
    def make_dataframe(self, query, columns):
        engine, conn = self.make_db_connect(user_id, user_pass, host, database)
        qq = pd.read_sql_query(query, conn)
        data_frame = pd.DataFrame(qq, columns=columns)
        conn.close()
        return data_frame