#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 12:10:49 2020

@author: pi
"""

import pandas as pd
import re
from fractions import Fraction
from collections import Counter



def get_operator_pos(split_entry):
    try:
        for i in range(0,len(temp)):
            r1 = re.search(r'^\*',temp[i])
            
            if (r1 != None):
                index = i
                break
            else: index = None
    except:
        pass
    
    return index
    
def get_new_value(split_entry,index):
    multiplier = re.sub(r'^\*','',split_entry[index])
    if (index == 2):
        new_val = float(Fraction(split_entry[0]+split_entry[1]))*int(multiplier)
    else:
        new_val = float(Fraction(split_entry[0]))*int(multiplier)
        
        
    return new_val
    

df = pd.read_csv('/home/pi/Desktop/recipe files/recipesV8_11_14_2020.csv')
df = df[df.Measure7.isnull()]
df = df.drop(columns = ['Measure7','Measure8','Measure9',\
                                                        'Measure10','Measure11','Measure12',\
                                                        'Measure13','Measure14','Measure15',\
                                                        'Ingredient7','Ingredient8','Ingredient9',\
                                                        'Ingredient10','Ingredient11','Ingredient12',\
                                                        'Ingredient13','Ingredient14','Ingredient15'])

df = df[df.Alcoholic == 'Alcoholic']
df = df.reset_index(drop=True)
df.Measure1 = df.Measure1.fillna('0')
df.Measure2 = df.Measure2.fillna('0')
df.Measure3 = df.Measure3.fillna('0')
df.Measure4 = df.Measure4.fillna('0')
df.Measure5 = df.Measure5.fillna('0')
df.Measure6 = df.Measure6.fillna('0')

updated_frame = []
for i in range(len(df)):
    total_ingredients = [df.Measure1.iloc[i],df.Measure2.iloc[i],df.Measure3.iloc[i],\
                         df.Measure4.iloc[i],df.Measure5.iloc[i],df.Measure6.iloc[i]]
    
    
    replace_vals = []
    
    for i in range(len(total_ingredients)):
            try:
                temp = total_ingredients[i].split()
                
            
                index = get_operator_pos(temp)
                
                if (index!=None):
                    new_entry = get_new_value(temp,index)
                    print(new_entry)
                    
                else:
                    try:
                        new_entry = float(Fraction(total_ingredients[i]))
                        print(new_entry)
                    except:
                        new_entry = total_ingredients[i]
                        
                    
                replace_vals.append(new_entry)
                    
            
            except:
                continue
            
    updated_frame.append(replace_vals)

df2 = pd.DataFrame(updated_frame)
df2.columns = ['Measure1 (ml)','Measure2 (ml)', 'Measure3 (ml)',\
                              'Measure4 (ml)', 'Measure5 (ml)', 'Measure6 (ml)']
df3 = pd.concat([df,df2],axis=1)
    


                                
    
    
    
                
        
        