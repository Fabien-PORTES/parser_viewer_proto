# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
from class_Bloc import *

class FileEnd(Exception):
	pass			
class BlocEnd(Exception):
	pass

class FileLineWrapper(object):
    def __init__(self, f):
        self.f = f
        self.curseur = 0
    def close(self):
        return self.f.close()
    def readline(self):
        self.line = self.f.readline()
        #print ">>>>>", str(self.line.strip())
        try:
            assert self.line
        except:
            raise FileEnd()
        return self.line
    def tell(self):
        return self.f.tell()-len(self.line)
    def seek(self, curseur):
        self.f.seek(curseur)

class Data():
    def __init__(self, path):
        self.paths = list()
        


print("tareumaaa")
