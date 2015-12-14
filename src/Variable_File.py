# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-


from collections import OrderedDict
import re

class FileEnd(Exception):
	pass			
class BlocEnd(Exception):
	pass

class FileLineWrapper(object):
    def __init__(self, f):
        self.f = f
        self.curseur = 0
        self.file_end = False
    def close(self):
        return self.f.close()
    def readline(self):
        self.line = self.f.readline()
        try:
            assert self.line
        except AssertionError:
            raise FileEnd()
        return self.line
    def tell(self):
        return self.f.tell()
    def seek(self, curseur):
        self.f.seek(curseur)
    def match_regex(self, regex, breaking_regex):
        self.readline()
        regexMatch = regex.search(self.line)
        if regexMatch:
            #print("MATCH")
            #print(self.line.strip())
            #print(regexMatch.groups())
            self.curseur = self.tell()
            return regexMatch
        for reg in [r for r in breaking_regex if r != regex]:
            if re.search(reg, self.line):
                self.seek(self.curseur)
                raise BlocEnd()

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
    
    @classmethod
    def set_shortcuts(cls, shortcuts):
        cls.shortcuts = shortcuts
    
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
    
    def get_shortcuts(self):
        return self.shortcuts

