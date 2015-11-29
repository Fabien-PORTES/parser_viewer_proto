# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
from time import time
from class_Bloc import *

class FileLineWrapper(object):
    def __init__(self, f):
        self.f = f
        self.curseur = 0
    def close(self):
        return self.f.close()
    def readline(self):
        self.line = self.f.readline()
        try:
            assert self.line
        except:
            raise FileEnd()
        return self.line
    def tell(self):
        return self.f.tell()-len(self.line)
    def seek(self, curseur):
        self.f.seek(curseur)
    def match_regex(self, regex, breaking_regex):
        self.readline()
        regexMatch = regex.search(self.line)
        if regexMatch:
            #print("MATCH")
            #print(self.line.strip())
            self.curseur = self.tell()
            return regexMatch
        for reg in [r for r in breaking_regex if r != regex]:
            if re.search(reg, self.line):
                self.seek(self.curseur)
                self.readline()
                raise BlocEnd()

class Main():
    def __init__(self):
        self.shortcut = None
        self.regex_tree = None
        self.files_to_parse = list()
    
    def set_shortcut(self, path):
        self.shortcut = ParseRegex(path)
    
    def set_regex_tree(self, path):
        self.regex_tree = ParentBloc(path)
        self.regex_tree._breaking_regex.append(self.regex_tree.last_regex(-1))
        self.regex_tree.regex_limit()
        
    def set_file_to_parse(self, path):
        self.files_to_parse.append(path)
    
    def parse(self):
        start = time()
        for file_path in self.files_to_parse:
            try:
                self.regex_tree.parse(FileLineWrapper(open(file_path, 'r')))
            except FileEnd as error:
                print(error)
        end = time()
        elapsed = end - start
        print(elapsed)

app = Main()

app.set_shortcut("/home/fabien/Bureau/Last dev/regex/regex_shortcut")
Variable.shortcuts = app.shortcut.shortcuts
app.set_regex_tree("/home/fabien/Bureau/last IA1/OUT")
app.set_file_to_parse("/home/fabien/Bureau/last IA1/OUTPUT")
app.parse()
