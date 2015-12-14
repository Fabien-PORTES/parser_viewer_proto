# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
import os
import re
from collections import OrderedDict
from usefull_functions import *
from Variable_File import *
from SqliteWrite import *

class BlocTemplate:
    def __init__(self, path):
        self.name = ""
        self.set_name(path)
        self.repetition = int(1)
        self._breaking_regex = list()
        self._obj_list = list()
    
    def set_name(self, path):
        self.name = path[path.rfind(os.sep) + 1:]
    
    def add_breaking_regex(self, regex):
        if isinstance(regex, list):
            for r in regex:
                if r not in self._breaking_regex:
                    self._breaking_regex.append(r)
        elif isinstance(regex, str):
            if regex not in self._breaking_regex:
                self._breaking_regex.append(regex)

    def empty(self):
        if not self._obj_list:
            print("{} is empty".format(self)) 
            return True
        else: 
            return False
            

class Bloc(BlocTemplate):
    def __init__(self, path):
        super().__init__(path)
        self._reg_sep = "/"
        
        Bloc.current_path = path
        self.fill_self(path)

    def fill_self(self, path):
        with open(path, 'r') as bloc_file:
            for line in bloc_file:
                line = line.strip()
                if line == "" or '#' in line[0]:
                    continue
                elif '.' in line[0]:
                    self._obj_list.append(Variable(line.split(".")[1:]))
                elif self._reg_sep in line[-1]:					
                    self._obj_list[-1].regex = line
                elif "!" in line[-1]:
                    self._breaking_regex.append(line[line.find('!') + 1:line.rfind('!')].strip())
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])
                    
    def first_reg(self):
        return self._obj_list[0].first_reg()
    
    def last_reg(self):
        return self._obj_list[-1].last_reg()
    
    def set_breaking_regex(self):
        self._breaking_regex.append(self.last_reg())
        if self.repetition > 1:
            self._breaking_regex.append(self.first_reg())
            
    def get_breaking_regex(self, var_idx):
        try:
            breaking_regex = [self._obj_list[var_idx+1].first_reg()] + self._breaking_regex
            return breaking_regex
        except IndexError:
            return self._breaking_regex
    
    def parse(self, file_to_parse):
        """Parse a file and try to match the regex of regexDict. If match, store matches in attributes.
		If no match but file is read, return 1
		"""
        data_dict = OrderedDict()
        for var_idx, variable in enumerate(self._obj_list):
            temp_match_list = list()
            breaking_regex = self.get_breaking_regex(var_idx)
            for (repetition, regex) in variable.regex:
                for _ in range(repetition):
                    regexMatch = False
                    while not regexMatch:
                        try:
                            regexMatch = file_to_parse.match_regex(regex, breaking_regex)
                        except BlocEnd:
                            break
                        except FileEnd:
                            create_dict(variable._name, temp_match_list, data_dict)
                            print("End of file reached on :\n\tRegex bloc  : {b}\n\tVariable : {v}\n\t"
                                "Regex : {r}".format(b = self.name, v = variable._name, r = regex.pattern))
                            raise FileEnd(data_dict)
                    else:
                        for elt in regexMatch.groups():
                            if elt is not None:
                                try:
                                    temp_match_list.append(float(elt))
                                except ValueError:
                                    temp_match_list.append(elt)
            create_dict(variable._name, temp_match_list, data_dict)
        return data_dict
    
    def __repr__(self):
        return "Bloc {0}".format(self.name)

class ParentBloc(BlocTemplate):
    def __init__(self, path):
        super().__init__(path)
        self._obj_list = list()
        self._order_bloc = list()
        
        self.fill_self(path)
        self.fill()
        
    def fill_self(self, path):
        p = path + os.sep + self.name
        with open(p, 'r') as parent_bloc:
            for line in parent_bloc:
                line = line.strip()
                if '-->' in line[0:3]:
                    self._order_bloc = [path +os.sep + x.strip() for x in line[3:].split(",")]
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])
        
    def fill(self):
        for bloc_path in self._order_bloc:
            if os.path.isfile(bloc_path):
                self._obj_list.append(Bloc(bloc_path))
            elif os.path.isdir(bloc_path):
                self._obj_list.append(ParentBloc(bloc_path))

    def next_regex(self, bloc_idx):
        if isinstance(self._obj_list[bloc_idx], Bloc):
            return self._obj_list[bloc_idx].first_reg()
        elif isinstance(self._obj_list[bloc_idx], ParentBloc):
            return ParentBloc.next_regex(self._obj_list[bloc_idx], 0)
    
    def last_regex(self, bloc_idx):
        if isinstance(self._obj_list[bloc_idx], Bloc):
            return self._obj_list[bloc_idx].last_reg()
        elif isinstance(self._obj_list[bloc_idx], ParentBloc):
            return ParentBloc.last_regex(self._obj_list[bloc_idx], -1)

    def regex_limit(self):
        for (i, bloc) in enumerate(self._obj_list):
            #print(bloc.name)
            if isinstance(bloc, Bloc):
                bloc.set_breaking_regex()
            elif isinstance(bloc, ParentBloc):
                bloc.add_breaking_regex(self.next_regex(i))
            try:
                bloc.add_breaking_regex(self.next_regex(i+1))
            except IndexError:
                bloc.add_breaking_regex(self._breaking_regex[0])
            bloc._breaking_regex.extend([r for r in self._breaking_regex if r not in bloc._breaking_regex])
            #print(bloc._breaking_regex)
            if isinstance(bloc, ParentBloc):
                ParentBloc.regex_limit(bloc)

    def parse(self, file_to_parse, database, parentID = [], depth = 0):
        file_end = False
        for i in range(self.repetition):
            key = self.name
            value = i+1 if self.repetition > 1 else None
            #parentID.append(database.table[0].push(key, value, parentID)) nested set and adjacency list
            #database.table[1].push(parentID)
            parentID.append(database.table[0].push(key, value, parentID))
            #print(parentID)
            database.commit()
            for bloc in self._obj_list:
                if isinstance(bloc, Bloc):
                    for j in range(bloc.repetition):
                        try:
                            data_dict = bloc.parse(file_to_parse)
                        except FileEnd as e:
                            file_end = True
                            data_dict = e.args[0]
                            if not data_dict:
                                raise
                        if not data_dict:
                            break
                        
                        if "name" not in data_dict.keys():
                            for key, value in data_dict.items():
                                #parentID.append(database.table[0].push(key, value, parentID)) nested set and adjacency list
                                #database.table[1].push(parentID)
                                database.table[1].push(key, value, parentID)
                                database.table[0].push(key, value, parentID)
                                #print(parentID)
                                #del parentID[-1]
                                pass
                        else:
                            depth += 1
                            #This is a 3 level dict (a table has been matched
                            keys = [k for k in data_dict.keys() if "name" not in k]
                            for (i, row) in enumerate(data_dict["name"]):
                                parentID.append(database.table[0].push(row, None, parentID))
                                #parentID.append(database.table[0].push(row, None, parentID))
                                #database.table[1].push(parentID)
                                for k in keys:
                                    try:
                                        val = data_dict[k][i]
                                        #parentID.append(database.table[0].push(k, val, parentID)) nested set and adjacency list
                                        #database.table[1].push(parentID)
                                        database.table[1].push(k, val, parentID)
                                        database.table[0].push(key, value, parentID)
                                        #print(parentID)
                                    except IndexError:
                                        print("Less value than header. Value set to 'None'")
                                    #del parentID[-1]
                                del parentID[-1]
                            depth -= 1
                        if file_end:
                            raise FileEnd()
                    
                elif isinstance(bloc, ParentBloc):
                    ParentBloc.parse(bloc, file_to_parse, database, parentID, depth+1)
            del parentID[-1]
            #print(parentID)
            

    def __repr__(self):
        return "ParentBloc {0}\nBlocs : {1}\n".format(self.name, self._obj_list)
    


        
