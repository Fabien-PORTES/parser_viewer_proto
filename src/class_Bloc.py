# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
import os
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
            print("Wrong regex with '{}' variable, in file {}".format(self._name[-1], Bloc.current_path))
        self._regex.append(regex)
    regex = property(_get_regex, _set_regex)
    
    def __repr__(self):
        return "Class_Variable %s" %self._name

class BlocTemplate:
    def __init__(self):
        self.name = ""
        self.repetition = int()
        self._breaking_regex = list()
    
    def add_breaking_regex(self, regex):
        if isinstance(regex, list):
            for r in regex:
                if r not in self._breaking_regex:
                    self._breaking_regex.append(r)
        elif isinstance(regex, str):
            if regex not in self._breaking_regex:
                self._breaking_regex.append(regex)
    def depth(self, i):
        pass
        #if isinstance(self, ParentBloc):
        #    return max([depth(elt, i+1) for elt in self._blocs if isinstance(elt, ParentBloc)])
        #elif isinstance(self, Bloc):
        #        return i

class Bloc(BlocTemplate):
    def __init__(self, path):
        super().__init__()
        self._variable = list()
        self._reg_sep = "/"
        
        Bloc.current_path = path
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
                    self._breaking_regex.append(line[line.find('!') + 1:line.rfind('!')].strip())
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])
                    
    def first_reg(self):
        return self._variable[0].regex[-1][1].pattern
    
    def last_reg(self):
        return self._variable[-1].regex[-1][1].pattern
    
    def set_breaking_regex(self):
        self._breaking_regex.append(self.last_reg())
        if self.repetition > 1:
            self._breaking_regex.append(self.first_reg())
    
    def parse(self, file_to_parse):
        

    def __repr__(self):
        return "Bloc {0}\n".format(self.name)

class ParentBloc(BlocTemplate):
    def __init__(self, path):
        super().__init__()
        self._blocs = list()
        self._order_bloc = list()
        
        self.fill_self(path)
        self.fill()
        
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
        
    def fill(self):
        for bloc_path in self._order_bloc:
            if os.path.isfile(bloc_path):
                self._blocs.append(Bloc(bloc_path))
            elif os.path.isdir(bloc_path):
                #self.fill_self(bloc_path)
                self._blocs.append(ParentBloc(bloc_path))
        self._breaking_regex.append(self.last_regex(-1))

    def next_regex(self, bloc_idx):
        if isinstance(self._blocs[bloc_idx], Bloc):
            return self._blocs[bloc_idx].first_reg()
        elif isinstance(self._blocs[bloc_idx], ParentBloc):
            return ParentBloc.next_regex(self._blocs[bloc_idx], 0)
    
    def last_regex(self, bloc_idx):
        if isinstance(self._blocs[bloc_idx], Bloc):
            return self._blocs[bloc_idx].last_reg()
        elif isinstance(self._blocs[bloc_idx], ParentBloc):
            return ParentBloc.last_regex(self._blocs[bloc_idx], -1)

    def regex_limit(self):
        for (i, bloc) in enumerate(self._blocs):
            print(bloc.name)
            if isinstance(bloc, Bloc):
                bloc.set_breaking_regex()
            elif isinstance(bloc, ParentBloc):
                bloc.add_breaking_regex(self.next_regex(i))
            try:
                bloc.add_breaking_regex(self.next_regex(i+1))
            except IndexError:
                print("IndexError")
                bloc.add_breaking_regex(self._breaking_regex[0])
            bloc._breaking_regex.extend([r for r in self._breaking_regex if r not in bloc._breaking_regex])
            print(bloc._breaking_regex)
            if isinstance(bloc, ParentBloc):
                ParentBloc.regex_limit(bloc)

    def __repr__(self):
        return "ParentBloc {0}\nBlocs : {1}".format(self.name, self._blocs)
    

        
#a = ParentBloc(os.path.normpath("C:\\Users\\Maison\\Desktop\\python\\OUT"))


a = ParentBloc("/home/fabien/Bureau/last IA1/OUT")
print(a)

a.regex_limit()

print("tareum")
print(a.next_regex(-1))
print(a._breaking_regex)

print([a.name for a in a._blocs])

print(a.depth(0))