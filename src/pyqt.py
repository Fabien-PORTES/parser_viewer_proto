# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtWidgets, QtSql
from DataTree import *
from Main import *
from collections import OrderedDict
import pandas as pd
import sys

# defining the main object used in the programm
core = Main()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):               
        self.centralWidget = QtWidgets.QWidget()
        #self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.tree_view = QtWidgets.QTreeView()
        self.tree_model = Data()

        self.textEdit = QtWidgets.QPlainTextEdit()
        self.textEdit.setTabStopWidth(40) #40 is a number of pixel
        self.textEdit.setLineWrapMode(self.textEdit.NoWrap)
        
        self.table_view = QtWidgets.QTableView()
        self._tables = list()
        
        self.Hbox = QtWidgets.QHBoxLayout(self.centralWidget)
        self.Hbox.addWidget(self.tree_view)
        self.Hbox.addWidget(self.table_view)
        
        self.setCentralWidget(self.centralWidget)
        
        loadRegex_Action = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Load regex', self)
        loadRegex_Action.setStatusTip('Load regular expressions tree')
        loadRegex_Action.triggered.connect(self.load_regex_tree)
        
        loadFileToParse_Action = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Load file', self)
        loadFileToParse_Action.setStatusTip('Load file to parse')
        loadFileToParse_Action.triggered.connect(self.load_files_to_parse)
        
        parse_Action = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Parse', self)
        parse_Action.setStatusTip('Parse selected file thanks to selected tree')
        parse_Action.triggered.connect(self.parse)
        
        load_db = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Load database', self)
        load_db.setStatusTip('Display Matches')
        load_db.triggered.connect(self.load_database)
        
        displayAction = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Display', self)
        displayAction.setStatusTip('Display Matches')
        displayAction.triggered.connect(self.init_tree_view)

        self.statusBar()

        menubar = self.menuBar()
        parseMenu = menubar.addMenu('Fichier de sortie')
        parseMenu.addAction(loadRegex_Action)
        parseMenu.addAction(displayAction)
        parseMenu.addAction(load_db)

        toolbar = self.addToolBar('Load regex')
        toolbar.addAction(loadRegex_Action)
        toolbar1 = self.addToolBar('Load file')
        toolbar1.addAction(loadFileToParse_Action)
        toolbar2 = self.addToolBar('Parse')
        toolbar2.addAction(parse_Action)
        toolbar3 = self.addToolBar('Display matches')
        toolbar3.addAction(displayAction)
        
        self.setGeometry(1000, 200, 800, 800)
        self.setWindowTitle('Main window')    
        self.show()
    
    def load_files_to_parse(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames()[0]
        print(paths)
        for i, p in enumerate(paths):
            print(p)
            core.set_file_to_parse(os.path.normpath(p))
    
    def load_regex_tree(self):
        s = ParseRegex("/home/fabien/Bureau/Last dev/regex/regex_shortcut")
        Variable.set_shortcuts(s.get_shortcuts())
        path = os.path.normpath(QtWidgets.QFileDialog.getExistingDirectory())
        if path:
            core.set_regex_tree(path)

    def init_database(self):
        table_data = ( AdjacencyList(name = "data",\
            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),\
                       ("key", "TEXT"),\
                       ("value", "INTEGER"),\
                       ("parent_id", "INTEGER"),\
                       ("has_child", "INTEGER")]) )
        table_data.set_insert_query(1)
        core.create_database([table_data])
    
    def load_database(self):
        path = os.path.normpath(QtWidgets.QFileDialog.getOpenFileName()[0])
        #path = os.path.normpath("/home/fabien/Bureau/last_IA1/OUTPUT_15-12-2015_11:20:42.db")
        if path:
            core.init_database(path)
            Item.set_cursor(core.get_cursor())
        
    def parse(self):
        self.init_database()
        core.parse_files()
        Item.set_cursor(core.get_cursor())
    
    def selection_changed(self):
        item = self.selection_tree.selection()
        tree = self.item_tree(item)
        item = self.tree_model.get_deepest_child(tree)
        if not item.is_filled:
            print(item.get_data())
            if item.is_all:
                item.fill([x for it in item.brothers() for x in it.get_data()])
            else:
                item.fill(item.get_data())
        if item.is_data:
            query, all_tree, val = self.get_data_query(tree)
            a = pd.read_sql(query, core.get_connection())
            print("a done")
            print(a.to_csv(sep = "\t"))
            print(all_tree + [val])
            #print(val)
            if len(all_tree) > 1:
                print(a.groupby(all_tree))
                b = pd.pivot_table(a, index = all_tree[0], columns = all_tree[1:], values = val, aggfunc = lambda x: x.sum())
            elif len(all_tree) == 1:
                b = a.set_index(all_tree[0])
            elif len(all_tree) == 0:
                b = a
            print("b done")

            model = PandasModel(b)
            self._tables.append(model)
            self.init_table_view()
            
    
    def item_tree(self, item):
        for i in item.indexes():
            tree = [i.row()]
            while tree[-1] != -1:
                tree.append(i.parent().row())
                i = i.parent()
            del tree[-1]
            tree.reverse()
        return tree
    
    def get_data_query(self, tree):
        text_tree = OrderedDict()
        all_tree = list()
        
        key = ""
        for child in self.tree_model.yield_children(tree):
            if child.is_index:
                text_tree[key] = int(child.text())
            elif child.is_all:
                all_tree.append(key)
            else:
                text_tree[child.text()] = None
            key = child.text()
        print(text_tree)
        query = SqliteQuery()
        query.build_from_dict(text_tree, all_tree)
        print(query.get_query())
        return (query.get_query(), all_tree, list(text_tree.keys())[-1])

    def init_tree_view(self):
        #self.load_database()
        self.tree_view.setModel(self.tree_model)
        
        self.tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.selection_tree = self.tree_view.selectionModel()
        
        
        self.selection_tree.selectionChanged.connect(self.selection_changed)
        
        self.tree_model.setColumnCount(2)
        self.tree_model.fill_root()
    
    def init_table_view(self):
        self.table_view.setWordWrap(True)
        self.table_view.setModel(self._tables[-1])
        self.table_view.setColumnWidth(0, 80)
        self.table_view.resizeRowsToContents()
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()  

