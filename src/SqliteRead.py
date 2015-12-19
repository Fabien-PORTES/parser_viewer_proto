# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from sql import *
from usefull_functions import quote
from collections import OrderedDict

class SqliteQuery():
    def __init__(self):
        self._table = "data"
        self._sql_table = [Table(self._table)]
        self._query = ""
        self._join = list()
        self._key_value = OrderedDict()
    
    def join(self, key, value = None):
        self._key_value[key] = value
        key = quote(key)
        self._sql_table.append(Table(self._table))
        if self._join:
            join = self._join[-1].join(self._sql_table[-1])
            if value is None:
                join.condition = (join.right.parent_id == self._sql_table[-2].row_id) & (join.right.key == key)
            else:
                join.condition = (join.right.parent_id == self._sql_table[-2].row_id) & (join.right.key == key) & (join.right.value == value)
            self._join.append(join)
        else:
            join = self._sql_table[-2].join(self._sql_table[-1])
            if value is None:
                join.condition = (join.right.parent_id == self._sql_table[-2].row_id) & (join.right.key == key)
            else:
                join.condition = (join.right.parent_id == self._sql_table[-2].row_id) & (join.right.key == key) & (join.right.value == value)
            self._join.append(join)

    def select_join(self, is_all):
        tmp = []
        for i, k in enumerate(self._key_value.keys()):
            if k in is_all:
                tmp.append(self._join[i].right.value.as_(k))
        tmp.append(self._join[i].right.value.as_(k))
        select = self._join[-1].select(*tmp)
        select.where = self._sql_table[0].parent_id == None
        self._query = select
    
    def get_query(self):
        tup = tuple(self._query)[1]
        return (tuple(self._query)[0] % tuple(tup))
    
    def clear(self):
        self.__init__()
    
    def build_from_dict(self, dic, is_all):
        for k,v in dic.items():
            print(k,v)
            self.join(k,v)
        self.select_join(is_all)
        return self.get_query()
    





