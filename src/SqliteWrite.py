# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

# -*- coding: utf-8 -*-

import sqlite3

class TableDB():
    def __init__(self, name, columns):
        self.cursor = None
        self.name = name
        self.columns = columns
        self.insert_query = ""
        self.inserted_col_number = int()
        self.delete_query = "DELETE FROM {table} WHERE row_id = {id}"
    
    def set_cursor(self, cursor):
        self.cursor = cursor
    
    def delete_row(self, row_id):
        query = self.delete_query.format(table = self.name, id = row_id)
        self.cursor.execute(query)
    
    def create_update_query(self, len_id_list):
        query =('UPDATE data SET rgt = rgt + 2 WHERE row_id in ({id_list})'
                .format(id_list = ",".join(len_id_list*['?'])))
        return query
    
    def create_table_query(self):
        create_table = "CREATE TABLE " + self.name
        create_table += " (" + ",".join( k + " " + v for k,v in self.columns) + ")"
        print(create_table)
        return create_table

    def create_insert_query(self, first_col = 0):
        col = ",".join([n for n,p in self.columns][first_col:])
        values_data_mark = ",".join((len(self.columns)-first_col) * ["?"])
        query = "INSERT INTO {table} ({columns}) VALUES ({values})".format(table = self.name, columns = col, values = values_data_mark)
        #print(query)
        return query
    
    def set_insert_query(self, i=0):
        self.insert_query = self.create_insert_query(i)
        #print(self.insert_query)

class Tree(TableDB):
    def __init__(self, name, columns):
        super().__init__(name, columns)
    
    def push(self, key, idx, parent_list):
        #print(self.insert_query, (key, value, parentID))
        #print(key, value, parent_list)
        if not parent_list:
            self.cursor.execute(self.insert_query, (key, idx, None))
        else:
            self.cursor.execute(self.insert_query, (key, idx, parent_list[-1]))
        return self.cursor.lastrowid

class AdjacencyList(TableDB):
    def __init__(self, name, columns):
        super().__init__(name, columns)
    
    def push(self, key, value, parent_list = None, has_child = 0):
        #print(self.insert_query, (key, value, parentID))
        #print(key, value, parent_list)
        if isinstance(value, list):
            if not parent_list:
                for v in value:
                    self.cursor.execute(self.insert_query, (key, v, None, has_child))
            else:
                for v in value:

                    self.cursor.execute(self.insert_query, (key, v, parent_list[-1], has_child))
        else:
            if not parent_list:
                self.cursor.execute(self.insert_query, (key, value, None, has_child))
            else:
                self.cursor.execute(self.insert_query, (key, value, parent_list[-1], has_child))
        #self.push_to_closure(parent_list)
        return self.cursor.lastrowid

class NestedSet(TableDB):
    def __init__(self, name, columns):
        super().__init__(name, columns)
        self.insert_query = None
        self._len_parent_list = 0
        self._lft = 0
        self._rgt = 1

    def push(self, key, value, parent_list):
        query = self.create_update_query(len(parent_list))
        self.cursor.execute(query, parent_list)
        delta_len = len(parent_list) - self._len_parent_list
        if delta_len == 0:
            self._lft += 2
            self._rgt += 2
        elif delta_len > 0:
            self._lft += 1
            self._rgt += 1
        elif delta_len < 0:
            self._lft += 1 + abs(delta_len)
            self._rgt += 1 + abs(delta_len)

        self.cursor.execute(self.insert_query, (key, value, self._lft, self._rgt))
        self._len_parent_list = len(parent_list)
        return self.cursor.lastrowid

class Closure(TableDB):
    def __init__(self, name, columns):
        super().__init__(name, columns)

    def push(self, parent_list):
        l = len(parent_list)
        if l >1:
            for i, row_id in enumerate(parent_list):
                ancestor = row_id
                descendant = parent_list[-1]
                depth = l - (i + 1)
                self.cursor.execute(self.insert_query ,(ancestor, descendant, depth))
        else:
            ancestor = 1
            descendant = 1
            depth = 0
            #print(self.insert_query)
            self.cursor.execute(self.insert_query,(ancestor, descendant, depth))
        
class SqliteWrite():
    def __init__(self, path):
        self.path = ""
        self.database = None
        self.cursor = None
        self.table = list()
        self.add_closure = False
        
        self.set_db(path)
        
    def set_db(self, path):
        print(path)
        self.database = sqlite3.connect(path)
        self.cursor = self.database.cursor()
        self.cursor.execute('PRAGMA journal_mode = OFF')
        self.cursor.execute('PRAGMA synchronous = OFF')
        self.database.isolation_level = 'IMMEDIATE'
    
    def get_cursor(self):
        return self.cursor
    def get_connection(self):
        return self.database
        
    def init_table(self, table, add_closure = False):
        self.table.append(table)
        self.table[-1].set_cursor(self.cursor)
        if add_closure:
            self.add_closure = True
            self.set_closure_table()
            self.table[-1].set_cursor(self.cursor)

    def commit(self):
        self.database.commit()
        
    def last_row_id(self):
        return self.cursor.lastrowid
    
    def set_closure_table(self):
        closure = Closure(name = "closure_" + self.table[0].name,\
                          columns = [("ancestor", "INTEGER"),\
                                     ("descendant", "INTEGER"),\
                                     ("depth", "INTEGER")])
        closure.set_insert_query()
        self.table.append(closure)
        self.cursor.execute(self.table[-1].create_table_query())
    
    def create_index(self, column_name):
        query = 'CREATE INDEX {c0}_index ON data ({c1});'.format(c0 = column_name, c1 = column_name)
        self.cursor.execute(query)
