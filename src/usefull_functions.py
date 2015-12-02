# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# -*- coding: utf-8 -*-

def create_dict(var_list, match_list, data_dict):
    for data, var in zip(match_list, var_list):
        data_dict[var] = data
    if len(match_list) > len(var_list):
        data_dict[var] = match_list[len(var_list)-1:]
    # if len(match_list) < len(var_list): nothing
    # variable without matched data are not created