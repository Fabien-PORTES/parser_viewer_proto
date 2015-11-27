# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import sys, os
from collections import OrderedDict
import re

class Variable:
    def __init__(self, names):
        self._name = names
        self.regex_tuple = list()
    def _get_regex(self):
        for repet, reg in zip(self.repet, self.regex):
            yield (repet, reg)
    def _set_regex(self, line):
        try:
            repetition = int(line[:line.find(SEP)].strip())
        except ValueError:
            repetition = 1
            print("Repetition set to 1 to the variable", self._name)
        regex = line[line.find(SEP) + 1: line.rfind(SEP)]
        self._regex_tuple.append((regex, repetition))
    regex_tuple = property(_get_regex, _set_regex)

class Bloc:
    def __init__(self, path):
        self._variable = list()
        self.repetition = int()
        self._regex_break = list()
        self.fill_self(path)
        
    def fill_self(self, path):
        SEP = "/"
        print(path)
        with open(path, 'r') as bloc_file:
            for line in bloc_file:
                if line == "" or '#' in line[0]:
                    continue
                elif '.' in line[0]:
                    self._variable.append(Variable(line.split(".")))
                elif SEP in line[-1]:					
                    self._variable[-1].regex_tuple = line
                elif "!" in line[-1]:
                    self._regex_break.append([line[line.find('!') + 1:line.rfind('!')].strip()])
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])

class ParentBloc:
    def __init__(self, path):
        self._bloc = list()
        self._order_bloc = list()
        self._repetition = int(1)
        self.fill_self(path)
        self.fill(path)
        
    def fill_self(self, path):
        p = path + os.sep + path[path.rfind(os.sep) + 1:]
        print(p)
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

        print(self._order_bloc)
        for bloc in self._order_bloc:
            if os.path.isfile(bloc):
                self.fill_file(bloc)
            elif os.path.isdir(bloc):
                self.fill_self(bloc)
                self.fill_folder(bloc)

a = ParentBloc(os.path.normpath("C:\\Users\\Maison\\Desktop\\python\\OUT"))
