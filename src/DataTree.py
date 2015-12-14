# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
from PyQt5 import QtGui
from collections import OrderedDict

class Data(QtGui.QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.cursor = None
        
    def fill_item(self, item):
        query = 'SELECT * FROM tree'
        print(query)
        data = self.cursor.execute(query)
        (row_id, key, key_idx, parent) = data.fetchone()
        item.setData(row_id)
        item.setText(key)
        row_id_depth = OrderedDict({1:[0]})
        
        while True:
            try:
                (row_id, key, key_idx, parent) = data.fetchone()
            except TypeError:
                break
            item = self.invisibleRootItem()
            child = QtGui.QStandardItem(key)

            idx = list(row_id_depth.keys()).index(parent)
            for index in list(row_id_depth.values())[1:idx+1]:
                for i in index:
                    item = item.child(i)
            for k in row_id_depth.keys():
                if k > parent:
                    del row_id_depth[k]
                
            if key_idx is not None:
                bla = False
                for i in range(item.rowCount()):
                    if item.child(i).text() == child.text():
                        n = item.child(i).rowCount()
                        child = QtGui.QStandardItem(str(n + 1))
                        item.child(i).appendRow(child)
                        bla = True
                        row_id_depth[row_id] = [i, n]
                if not bla:
                    item.appendRow(child)
                    child = QtGui.QStandardItem("1")
                    i = item.rowCount()-1
                    item.child(i).appendRow(child)
                    row_id_depth[row_id] = [i, 0]
            else:
                n = item.rowCount()
                item.appendRow(child)                     
                row_id_depth[row_id] = [n]

    def fill_tree(self):
        self.clear()     
        self.fill_item(self.invisibleRootItem())
        print("end")
    
    def get_child(self, index_list):
        item = self.invisibleRootItem()
        for i in index_list:
            item = item.child(i)
        return item
            
    
    def set_cursor(self, cursor):
        self.cursor = cursor

#app = QtWidgets.QApplication(sys.argv)
#
#a = Data()
#a.fill_tree(cursor)
##a.setHeaderLabels(["Tree Matches", "Size"])
#
#
# 
## Our main window will be a QListView
#list = QtWidgets.QColumnView()
#list.setWindowTitle('Example List')
#list.setMinimumSize(600, 400)
#
# 
## Create an empty model for the list's data
#model = QtGui.QStandardItemModel(list)
#model.setHorizontalHeaderLabels(('walou', "tareum"))
# 
## Add some textual items
#foods = [
#    'Cookie dough', # Must be store-bought
#    'Hummus', # Must be homemade
#    'Spaghetti', # Must be saucy
#    'Dal makhani', # Must be spicy
#    'Chocolate whipped cream' # Must be plentiful
#]
# 
#for food in foods:
#    # create an item with a caption
#    item = QtGui.QStandardItem(food)
# 
#    # add a checkbox to it
#    #item.setCheckable(True)
#    
#    valu = QtGui.QStandardItem("food")
#    # Add the item to the model
#    model.appendRow((item, valu))
#
# 
## Apply the model to the list view
#list.setModel(a)
# 
## Show the window and run the app
#list.show()
#app.exec_()
    
    
    
        
