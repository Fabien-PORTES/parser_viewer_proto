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
        self.insert_data_query = ""
        self.insert_closure_query = ""
        
        self.set_db(path)
        self.set_data_columns()
        self.create_data_table()
        self.create_closure_table()
        self.set_insert_query()
        
    def set_db(self, path):
        print(path)
        self.database = sqlite3.connect(path)
        self.cursor = self.database.cursor()
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.database.isolation_level = 'IMMEDIATE'
    
    def set_data_columns(self):
        self.columns["row_id"] = "INTEGER PRIMARY KEY NOT NULL"
        self.columns["key"] = "TEXT"
        self.columns["value"] = "FLOAT"
        self.columns["parentID"] = "INTEGER"
    
    def create_data_table(self):
        create_table = "CREATE TABLE " + self.table_name
        create_table += " (" + ",".join( k + " " + v for k,v in self.columns.items()) + ")"
        print(create_table)
        self.cursor.execute(create_table)
        
    def create_closure_table(self):
        create_table = ("CREATE TABLE " + "closure_" + self.table_name +
                        "(ancestor, descendant, depth)")
        self.cursor.execute(create_table)

    def set_insert_query(self):
        col = ",".join(list(self.columns.keys())[1:])
        values_mark = ",".join((len(self.columns.keys())-1) * ["?"])
        self.insert_data_query = "INSERT INTO {table} ({columns}) VALUES ({values})".format(table = self.table_name, columns = col, values = values_mark)
        self.insert_closure_query = "INSERT INTO closure_{table} (ancestor, descendant, depth) VALUES (?, ?, ?)".format(table = self.table_name)
    
    def push_to_db(self, key, value = None, parentID = None):
        #print(self.insert_query, (key, value, parentID))
        #print(key, value, parentID)
        if isinstance(value, list):
            for v in value:
                self.cursor.execute(self.insert_data_query, (key, v, parentID))
        else:
            self.cursor.execute(self.insert_data_query, (key, value, parentID))
        return self.cursor.lastrowid
    
    def push_to_closure(self, parent_list):
        l = len(parent_list)
        if l >1:
            for i, row_id in enumerate(parent_list):
                ancestor = row_id
                descendant = parent_list[-1]
                depth = l - (i + 1)
                self.cursor.execute(self.insert_closure_query,(ancestor, descendant, depth))
        else:
            ancestor = 1
            descendant = 1
            depth = 0
            self.cursor.execute(self.insert_closure_query,(ancestor, descendant, depth))
    
    def commit(self):
        self.database.commit()
        
    def last_row_id(self):
        return self.cursor.lastrowid