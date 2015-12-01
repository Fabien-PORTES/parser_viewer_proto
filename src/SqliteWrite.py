# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

# -*- coding: utf-8 -*-

import sqlite3
from collections import OrderedDict

class SqliteWrite():
    def __init__(self, path):
        self.path = ""
        self.table_name = 'data'
        self.database = None
        self.cursor = None
        self.columns = OrderedDict()
        self.insert_query
        
        self.set_db(path)
        self.set_columns()
        self.create_table()
        self.insert_query()
        
    def set_db(self, path):
        print(path)
        self.database = sqlite3.connect(path)
        self.cursor = self.database.cursor()
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.database.isolation_level = 'IMMEDIATE'
    
    def set_columns(self):
        self.columns["row_id"] = "INTEGER PRIMARY KEY NOT NULL"
        self.columns["key"] = "TEXT"
        self.columns["value"] = "FLOAT"
        self.columns["parentID"] = "INTEGER"
    
    def create_table(self):
        create_table = "CREATE TABLE " + self.table_name
        create_table += " (" + ",".join( k + " " + v for k,v in self.columns.items()) + ")"
        print(create_table)
        self.cursor.execute(create_table)

    def insert_query(self):
        col = ",".join(list(self.columns.keys())[1:])
        values_mark = ",".join((len(self.columns.keys())-1) * ["?"])
        self.insert_query = "INSERT INTO data ({columns}) VALUES ({values})".format(columns = col, values = values_mark)
    
    def push_to_db(self, key, value = None, parentID = None):
        #print(self.insert_query, (key, value, parentID))
        #print(key, value, parentID)
        self.cursor.execute(self.insert_query, (key, value, parentID))
        return self.cursor.lastrowid
    
    def commit(self):
        self.database.commit()
        
    def last_row_id(self):
        return self.cursor.lastrowid        

        
        
        
