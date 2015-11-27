# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
import sys, os
from collections import OrderedDict
import re

class Variable:
    def __init__(self, names):
        self._name = names
        self._regex = list()
        self._repetition = list()
        self._reg_sep =  "/"
        self._wrong_regex = False
    def _get_regex(self):
        return [r for r in zip(self._repetition, self._regex)]
    def _set_regex(self, line):
        try:
            self._repetition.append(int(line[:line.find(self._reg_sep)].strip()))
        except ValueError:
            self._repetition.append(1)
            print("Repetition set to 1 to the variable", self._name)
        try:
            regex = re.compile(line[line.find(self._reg_sep) + 1: line.rfind(self._reg_sep)])
        except :
            regex = re.compile("")
            self._wrong_regex = True
            print("Wrong regex with '{}' variable, in file {}".format(self._name, Bloc.current_path))
        self._regex.append(regex)
    regex = property(_get_regex, _set_regex)
    
    def __repr__(self):
        return "Class_Variable %s" %self._name

class Bloc:
    current_path = ""
    def __init__(self, path):
        current_path = path
        self.name = ""
        self._variable = list()
        self.repetition = int()
        self._reg_sep = "/"
        
        self._regex_break = list()
        self.fill_self(path)
        
    def fill_self(self, path):
        self.name = path[path.rfind(os.sep) + 1:]
        with open(path, 'r') as bloc_file:
            for line in bloc_file:
                line = line.strip()
                if line == "" or '#' in line[0]:
                    continue
                elif '.' in line[0]:
                    self._variable.append(Variable(line.split(".")[1:]))
                elif self._reg_sep in line[-1]:					
                    self._variable[-1].regex = line
                elif "!" in line[-1]:
                    self._regex_break.append([line[line.find('!') + 1:line.rfind('!')].strip()])
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])
    def first_reg(self):
        return self._variable[0].regex[-1][-1].pattern
    def last_reg(self):
        return self._variable[-1].regex[-1][-1].pattern
    
    def __repr__(self):
        return "Bloc {0}\n".format(self.name)

class ParentBloc:
    def __init__(self, path):
        self.name = ""
        self._blocs = list()
        self._order_bloc = list()
        self._repetition = int(1)
        self._breaking_regex = list()
        
        self.fill_self(path)
        self.fill(path)
        
    def fill_self(self, path):
        self.name = path[path.rfind(os.sep) + 1:]
        p = path + os.sep + self.name
        with open(p, 'r') as parent_bloc:
            for line in parent_bloc:
                line = line.strip()
                if '-->' in line[0:3]:
                    self._order_bloc = [path +os.sep + x.strip() for x in line[3:].split(",")]
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self._repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])
                    
    def fill_file(self, path):
        self._blocs.append(Bloc(path))
        
    def fill_folder(self, path):
        self._blocs.append(ParentBloc(path))
        
    def fill(self, path):
        for bloc in self._order_bloc:
            if os.path.isfile(bloc):
                self.fill_file(bloc)
            elif os.path.isdir(bloc):
                self.fill_self(bloc)
                self.fill_folder(bloc)
    
    def next_regex(self, bloc_idx):
        print(type(self._blocs[bloc_idx]))
        if isinstance(self._blocs[bloc_idx], Bloc):
            return self._blocs[bloc_idx].first_reg()
        elif isinstance(self._blocs[bloc_idx], ParentBloc):
            return ParentBloc.next_regex(self._blocs[bloc_idx], 0)

    def __repr__(self):
        return "ParentBloc {0}\nBlocs : {1}".format(self.name, self._blocs)
    
    def regex_limit(self):
        self._breaking_regex.append(self.next_regex(-1))
        for bloc in self._blocs:
            if isinstance(bloc, Bloc):
                pass
            elif isinstance(bloc, ParentBloc):
                pass

#a = ParentBloc(os.path.normpath("C:\\Users\\Maison\\Desktop\\python\\OUT"))
a = ParentBloc("/home/fabien/Bureau/last IA1/OUT")
print(a)

print(a.next_regex(-1))