# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtWidgets, QtCore
from DataTree import *
from Main import *
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
        self.tree_view = QtWidgets.QColumnView()
       
        #self.tree_view.setHeaderLabels(["Tree Matches", "Size"])
        #for i in range(self.tree_view.columnCount()):
        #    self.tree_view.resizeColumnToContents(i)
        
        self.tree_model = Data()

        
        
        self.textEdit = QtWidgets.QPlainTextEdit()
        self.textEdit.setTabStopWidth(40) #40 is a number of pixel
        self.textEdit.setLineWrapMode(self.textEdit.NoWrap)
        
        self.Hbox = QtWidgets.QVBoxLayout(self.centralWidget)
        self.Hbox.addWidget(self.tree_view)
        self.Hbox.addWidget(self.textEdit)
        
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
        displayAction.triggered.connect(self.init_view)

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
        table_tree = ( AdjacencyList(name = "data",\
            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),\
                       ("key", "TEXT"),\
                       ("value", "FLOAT"),\
                       ("parent_id", "INTEGER")]) )
        table_tree.set_insert_query(1)
        table_data = ( AdjacencyList(name = "tree",\
            columns = [("row_id", "INTEGER PRIMARY KEY NOT NULL"),\
                       ("key", "TEXT"),\
                       ("value", "INTEGER"),\
                       ("parent_id", "INTEGER")]) )
        table_data.set_insert_query(1)
        core.create_database([table_tree, table_data])
    
    def load_database(self):
        path = os.path.normpath(QtWidgets.QFileDialog.getOpenFileName()[0])
        if path:
            core.init_database(path)
            self.tree_model.set_cursor(core.get_cursor())
        
    def parse(self):
        self.init_database()
        core.parse()
        self.tree_model.set_cursor(core.get_cursor())
    
    def selection_changed(self):
        selection = self.selection_model.selection()
        for i in selection.indexes():
            tree = [i.row()]
            while tree[-1] != -1:
                tree.append(i.parent().row())
                i = i.parent()
            del tree[-1]
            tree.reverse()
            item = self.tree_model.get_child(tree)
        if not item.is_filled:
            print(item.get_data())
            self.tree_model.fill_item(item, item.get_data())
        self.textEdit.insertPlainText(str(item.get_data()))
        
    def init_view(self):
        self.tree_view.setModel(self.tree_model)
        self.selection_model = self.tree_view.selectionModel()
        
        self.selection_model.selectionChanged.connect(self.selection_changed)
        self.tree_model.fill_root()
        
        
        

    
    
        
    
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()  

