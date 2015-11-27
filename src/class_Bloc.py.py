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
        self._regex_tuple = list()
        self._reg_sep =  "/"
    def _get_regex(self):
        for repet, reg in zip(self.repet, self.regex):
            yield (repet, reg)
    def _set_regex(self, line):
        try:
            repetition = int(line[:line.find(self._reg_sep)].strip())
        except ValueError:
            repetition = 1
            print("Repetition set to 1 to the variable", self._name)
        regex = re.compile(line[line.find(self._reg_sep) + 1: line.rfind(self._reg_sep)])
        self._regex_tuple.append((regex, repetition))
    regex_tuple = property(_get_regex, _set_regex)

class Bloc:
    def __init__(self, path):
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
                    self._variable.append(Variable(line.split(".")[0:]))
                elif self._reg_sep in line[-1]:					
                    self._variable[-1].regex_tuple = line
                elif "!" in line[-1]:
                    self._regex_break.append([line[line.find('!') + 1:line.rfind('!')].strip()])
                elif re.match("\s*[N|n]\s*=\s*\d+", line):
                    self.repetition = int(re.match("\s*[N|n]\s*=\s*(\d+)", line).groups()[0])

    def __repr__(self):
        return "Bloc {0}\n".format(self.name)

class ParentBloc:
    def __init__(self, path):
        self.name = ""
        self._blocs = list()
        self._order_bloc = list()
        self._repetition = int(1)
        
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
        print(self._order_bloc)
        for bloc in self._order_bloc:
            if os.path.isfile(bloc):
                self.fill_file(bloc)
            elif os.path.isdir(bloc):
                self.fill_self(bloc)
                self.fill_folder(bloc)
                
    def __repr__(self):
        return "ParentBloc {0}\nBlocs : {1}".format(self.name, self._blocs)
    

a = ParentBloc(os.path.normpath("C:\\Users\\Maison\\Desktop\\python\\OUT"))
print(a)

def regex_limit(self):
    last_bloc = self.tree_dict[self.tree_dict["order_bloc"][-1]]
    self.tree_dict["breaking_regex"] = [next_regex(last_bloc)] #last
    def last_regex(objet_regex):
        for bloc_idx, bloc in enumerate(objet_regex["order_bloc"]):
            print("Bloc : ", bloc)
			
            child_bloc = objet_regex[bloc]
            child_bloc["breaking_regex"] = list()
            regex_temp = list() 
				
            if "regex_break" in child_bloc:
            # on ajoute les regex ajouté manuellement entre "!"
            # dans les fichiers de regex
                regex_temp.extend(child_bloc["regex_break"])
            if "regex" in child_bloc:
                # si le bloc est un bloc avec des variables et des regex (un fichier),
                # on ajoute la dernière regex du bloc
                regex_temp.append(child_bloc["regex"].values()[-1][-1]["regex"])
                if child_bloc["nb_bloc"] > 1:
                    # on ajoute la première regex du bloc si le bloc est répété plus d'une fois
                    first_reg = child_bloc["regex"].values()[0][-1]["regex"]
                    if first_reg not in regex_temp:
                        regex_temp.append(first_reg)
            else:
                # si le bloc est un dossier (donc pas de regex)
                # on ajoute la première regex du dossier
                regex_temp.append(next_regex(child_bloc))
				
            # on ajoute la première regex du bloc suivant si ce dernier existe
            # sinon on ajoute la première regex du bloc parent
            try:
                bloc_suivant = objet_regex[objet_regex["order_bloc"][bloc_idx + 1]]
                regex_temp.append(next_regex(bloc_suivant))
            except IndexError:
                regex_temp.append(objet_regex["breaking_regex"][0])
				
            # on ajoute les regex break du bloc parent si elles n'ont pas encore été ajoutés
            regex_temp.extend([r for r in objet_regex["breaking_regex"] if r not in regex_temp])
				
            child_bloc["breaking_regex"].extend(regex_temp)
            print(child_bloc["breaking_regex"])
				
            if "order_bloc" in child_bloc:
                last_regex(child_bloc)
    last_regex(self.tree_dict)