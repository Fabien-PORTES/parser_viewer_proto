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

        self.set_db(path)
        
    def set_db(self, path):
        print(path)
        self.database = sqlite3.connect(path)
        self.cursor = self.database.cursor()
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.database.isolation_level = 'IMMEDIATE'
    
    def create_table(self, column_dict, table_name):
        create_table = "CREATE TABLE " + table_name
        create_table += " (" + ",".join( k + " " + v for k,v in column_dict.items()) + ")"
        print(create_table)
        self.cursor.execute(create_table)

    def create_insert_query(self, column_dict, table_name):
        col = ",".join(list(column_dict.keys())[1:])
        values_data_mark = ",".join((len(column_dict)-1) * ["?"])
        query = "INSERT INTO {table} ({columns}) VALUES ({values})".format(table = table_name, columns = col, values = values_data_mark)
        print(column_dict)
        print(query)
        return query

    def commit(self):
        self.database.commit()
        
    def last_row_id(self):
        return self.cursor.lastrowid
    
class AdjacencyList(SqliteWrite):
    def __init__(self, path):
        super().__init__(path)
        self.columns = OrderedDict()
        self.closure_columns = OrderedDict()
        self.insert_query = ""
        self.insert_closure_query = ""
        
        self.set_columns()
        self.set_insert_query()
        self.create_table(self.columns, self.table_name)
       
        self.set_closure_table()
        
    def set_closure_table(self):
        self.set_closure_columns()
        table_name = "closure_" + self.table_name
        self.create_table(self.closure_columns, 'closure_' + table_name)
        col = ",".join(list(self.closure_columns.keys()))
        values_data_mark = ",".join((len(self.closure_columns)) * ["?"])
        self.insert_closure_query = ("INSERT INTO closure_{table} ({columns}) VALUES ({values})"
        .format(table = table_name, columns = col, values = values_data_mark))
    
    def set_columns(self):
        self.columns["row_id"] = "INTEGER PRIMARY KEY NOT NULL"
        self.columns["key"] = "TEXT"
        self.columns["value"] = "FLOAT"
        self.columns["parentID"] = "INTEGER"
    
    def set_closure_columns(self):
        self.closure_columns["ancestor"] = "INTEGER"
        self.closure_columns["descendant"] = "INTEGER"
        self.closure_columns["depth"] = "INTEGER"
    
    def set_insert_query(self):
        self.insert_query = self.create_insert_query(self.columns, self.table_name)
        print(self.insert_query)
        
    def push_to_db(self, key, value, parent_list = None):
        #print(self.insert_query, (key, value, parentID))
        #print(key, value, parent_list)
        if isinstance(value, list):
            for v in value:
                self.cursor.execute(self.insert_query, (key, v, parent_list[-1]))
        else:
            if not parent_list:
                self.cursor.execute(self.insert_query, (key, value, None))
            else:
                self.cursor.execute(self.insert_query, (key, value, parent_list[-1]))
        self.push_to_closure(parent_list)
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
            
class NestedSet(SqliteWrite):
    def __init__(self, path):
        super().__init__(path)
        self.columns = OrderedDict()
        self.len_parent_list = 0
        self.lft = 0
        self.rgt = 1
        
        self.set_columns()
        self.set_insert_query()
        self.create_table(self.columns, self.table_name)
        
    def set_insert_query(self):
        self.insert_query = self.create_insert_query(self.columns, self.table_name)
        print(self.insert_query )

    def set_columns(self):
        self.columns["row_id"] = "INTEGER PRIMARY KEY NOT NULL"
        self.columns["key"] = "TEXT"
        self.columns["value"] = "FLOAT"
        self.columns["lft"] = "INTEGER"
        self.columns["rgt"] = "INTEGER"


    def push_to_db(self, key, value, parent_list):
        query =('UPDATE data SET rgt = rgt + 2 WHERE row_id in ({id_list})'
                .format(id_list = ",".join(len(parent_list)*['?'])))
        #print(query)
        #print(parent_list)
        self.cursor.execute(query, parent_list)
        delta_len = len(parent_list) - self.len_parent_list
        if delta_len == 0:
            self.lft += 2
            self.rgt += 2
        elif delta_len > 0:
            self.lft += 1
            self.rgt += 1
        elif delta_len < 0:
            self.lft += 1 + abs(delta_len)
            self.rgt += 1 + abs(delta_len)

        self.cursor.execute(self.insert_query, (key, value, self.lft, self.rgt))
        self.len_parent_list = len(parent_list)
        return self.cursor.lastrowid