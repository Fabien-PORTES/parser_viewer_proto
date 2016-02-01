# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
from time import time
from RegexTree import *
from datetime import datetime

class Main():
    def __init__(self):
        self.shortcut = None
        self.regex_tree = None
        self.files_to_parse = list()
        self.database = None
        self.path = ""
    
    def set_shortcut(self, path):
        self.shortcut = ParseRegex(path)
    
    def set_regex_tree(self, path):
        self.regex_tree = ParentBloc(path)
        self.regex_tree.is_root = True
        self.regex_tree._breaking_regex.append(self.regex_tree.last_regex(-1))
        self.regex_tree.regex_limit()
        
    def set_file_to_parse(self, path):
        self.files_to_parse.append(path)
    
    def parse_files(self):
        start = time()
        if len(self.files_to_parse) == 1:
            self.parse_file(self.files_to_parse[0])
        else:
            self.database.table[0].push("root", None, None, 1)
            for file_path in self.files_to_parse:
                self.parse_file(file_path, [1])
        print('Creating index')
        self.database.create_index("parent_id")
        end = time()
        elapsed = end - start
        print(elapsed)

    def parse_file(self, file_path, parent_id = []):
        print("Processing file : {path}".format(path = file_path))
        try:
            file_to_parse = FileLineWrapper(open(file_path, 'r', encoding = "iso-8859-15"))
            self.regex_tree.parse(file_to_parse, self.database, parent_id)
        except FileEnd:
            print("End of file reached on file : {}".format(file_path))
        self.database.commit()
        
    
    def create_database(self, tables):
        format = "%d-%m-%Y_%H:%M:%S"
        now = datetime.strftime(datetime.now(), format)
        self.path = self.files_to_parse[0] + "_" + now + ".db"
        self.init_database(self.path)

        for table in tables:
            self.database.init_table(table)
            self.database.cursor.execute(table.create_table_query())
    
    def init_database(self, path):
        self.database = SqliteWrite(path)
    
    def get_cursor(self):
        if self.database is not None:
            return self.database.cursor
        else:
            print("None database has been initialiazed.")
    
    def get_connection(self):
        if self.database.get_connection() is not None:
            return self.database.get_connection()
        else:
            print("Database has nor been initialiazed")

tree_table = ( AdjacencyList(name = "tree",\
            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),
                       ("key", "TEXT"),\
                       ("value", "INTEGER"),\
                       ("parent_id", "INTEGER")]) )
tree_table.set_insert_query(1)

#table_data = ( NestedSet(name = "data",\
#            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),\
#                       ("key", "TEXT"),\
#                       ("value", "FLOAT"),\
#                       ("lft", "INTEGER"),\
#                       ("rgt", "INTEGER")]) )
#table_data.set_insert_query(1)

table_data = ( AdjacencyList(name = "data",\
            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),\
                       ("key", "TEXT"),\
                       ("value", "FLOAT"),\
                       ("parent_id", "INTEGER")]) )
table_data.set_insert_query(1)



#app.set_shortcut("/home/fabien/Bureau/Last dev/regex/regex_shortcut")
#Variable.shortcuts = app.shortcut.shortcuts
#app.set_regex_tree("/home/fabien/Bureau/last_IA1/OUT")
#app.set_file_to_parse("/home/fabien/Bureau/last_IA1/OUTPUTcut")
#app.init_database([table_data])
#app.parse()

