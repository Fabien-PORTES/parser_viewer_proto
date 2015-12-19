# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
from PyQt5 import QtGui, QtCore
from SqliteRead import *

class Item(QtGui.QStandardItem):
    select_query = 'SELECT *, count(distinct(key)) FROM data WHERE parent_id IN ({id_list}) group by key, value'
    cursor = None
    
    def __init__(self, string = None):
        super().__init__(string)
        self.is_filled = False
        self.row_id = []
        self.is_all = False
        self.is_data = False
        self.is_index = False
    
    @classmethod
    def set_cursor(cls, cursor):
        cls.cursor = cursor
    
    def has_child(self, child_text):
        for i in range(self.rowCount()):
            if self.child(i).text() == child_text:
                return i
        return -1
    
    def fill(self, parent_list=[1]):
        query = Item.select_query.format(id_list = ",".join(len(parent_list)*['?']))
        data = Item.cursor.execute(query, parent_list)
        while True:
            try:
                (row_id, key, key_idx, parent, has_child, count) = data.fetchone()
                print (row_id, key, key_idx, parent, has_child)
            except TypeError:
                break
            child = Item(key)
            #child.appendColumn([Item(str(count))])
            existing_child = Item.has_child(self, key)
            if key_idx is not None:
                if has_child:
                    if existing_child != -1:
                        child = Item(str(key_idx))
                        child.is_index = True
                        child.setData(row_id)
                        #child.appendColumn([Item(str(count))])
                        self.child(existing_child).appendRow(child)
                    else:
                        i = self.rowCount()
                        self.appendRow(child)
                        child = Item(str(key_idx))
                        #child.appendColumn([Item(str(count))])
                        child.setData(row_id)
                        child.is_index = True
                        all = Item("All")
                        #all.appendColumn([Item("count")])
                        all.is_all = True
                        self.child(i).appendRow(all)
                        self.child(i).appendRow(child)
                elif not has_child and existing_child == -1:
                    child.is_data = True
                    child.setData(row_id)
                    #child.appendColumn([Item(str(count))])
                    self.appendRow(child)
                    

            elif existing_child == -1:
                i = self.rowCount()
                self.appendRow(child)  
                self.child(i).setData(row_id)
            self.is_filled = True
    
    def brothers(self):
        own_idx = self.index().row()
        if self.parent:
            for i in range(1, self.parent().rowCount()):
                if i != own_idx:
                    yield self.parent().child(i)
    
    def setData(self, data):
        self.row_id.append(data)
    
    def get_data(self):
        return self.row_id

class Data(QtGui.QStandardItemModel):
    def __init__(self):
        super().__init__()

    def fill_root(self):
        self.clear()
        Item.fill(self.invisibleRootItem())
    
    def get_deepest_child(self, index_list):
        item = self.invisibleRootItem()
        for i in index_list:
            item = item.child(i)
        return item
    
    def yield_children(self, index_list):
        item = self.invisibleRootItem()
        for i in index_list:
            item = item.child(i)
            yield item

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        try:
            return self._data.columns.size
        except AttributeError:
            return 1
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self._data.columns[col])
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(self._data.index[col])
        return None
    
    