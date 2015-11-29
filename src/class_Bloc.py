# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-
import os
import re
from collections import OrderedDict

class FileEnd(Exception):
	pass			
class BlocEnd(Exception):
	pass

class ParseRegex():
    def __init__(self, path):
        self.path = path
        self.shortcuts = OrderedDict()
        self.split_sign = ";;"
        self.load_shortcuts()
        
    def load_shortcuts(self):
        with open(self.path, 'r') as shortcut_file:
            for line in shortcut_file:
                line = line.strip()
                if line == "" or '#' in line[0]:
                    continue
                elif self.split_sign in line:
                    tup = line.split(self.split_sign)
                    self.shortcuts[tup[0]] = tup[1]

class Variable:
    shortcuts = OrderedDict()
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
        regex = line[line.find(self._reg_sep) + 1: line.rfind(self._reg_sep)]
        regex = self.parse_regex(regex)
        try:
            regex = re.compile(regex)
        except:
            regex = re.compile("")
            self._wrong_regex = True
            print("Wrong regex with '{}' variable, in file {}".format(self._name[-1], Bloc.current_path))
        self._regex.append(regex)
    regex = property(_get_regex, _set_regex)
    
    def parse_regex(self, regex):
        for k,v in Variable.shortcuts.items():
            regex = re.sub(re.escape(k), v, regex)
        return regex
    
    def first_reg(self):
        return self._regex[0].pattern
    def last_reg(self):
        return self._regex[-1].pattern
    
    def __repr__(self):
        return "Class_Variable [{}]".format(",".join(self._name))

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
        def create_dict(var_list, match_list):
            for data, var in zip(match_list, var_list):
                data_dict[var] = data
            if len(match_list) > len(var_list):
                data_dict[var] = match_list[len(var_list)-1:]
        data_dict = OrderedDict()
        for var_idx, variable in enumerate(self._obj_list):
            temp_match_list = list()
            breaking_regex = self.get_breaking_regex(var_idx)
            for (repetition, regex) in variable.regex:
                for compteur in range(repetition):
                    regexMatch = False
                    while not regexMatch:
                        try:
                            regexMatch = file_to_parse.match_regex(regex, breaking_regex)
                        except BlocEnd:
                            break
                        except FileEnd:
                            create_dict(variable._name, temp_match_list)
                            print("Fin du fichier atteint sur :\nVariable :", variable._name, "\nRegex :", self.name)
                            raise FileEnd(data_dict)
                    else:
                        for elt in regexMatch.groups():
                            if elt is not None:
                                try:
                                    temp_match_list.append(float(elt))
                                except ValueError:
                                    temp_match_list.append(elt)
            create_dict(variable._name, temp_match_list)
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
                print("IndexError")
                bloc.add_breaking_regex(self._breaking_regex[0])
            bloc._breaking_regex.extend([r for r in self._breaking_regex if r not in bloc._breaking_regex])
            #print(bloc._breaking_regex)
            if isinstance(bloc, ParentBloc):
                ParentBloc.regex_limit(bloc)

    def __repr__(self):
        return "ParentBloc {0}\nBlocs : {1}\n".format(self.name, self._obj_list)
    
    def parse(self, file_to_parse):
        for i in range(self.repetition):
            for bloc in self._obj_list:
                if isinstance(bloc, Bloc):
                    for j in range(bloc.repetition):
                        bloc.parse(file_to_parse)
                elif isinstance(bloc, ParentBloc):
                    ParentBloc.parse(bloc, file_to_parse)

        
