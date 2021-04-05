#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 10:58:47 2020

@author: pi
"""


import pandas as pd
from gpiozero import LED
from time import sleep
import time
import re
import numpy as np


#1) self.percents[i] will be between 0-100 

#2) The length of self.percentages will depend on the number of liquid ingredients 
#for a sepcific recipe (up to six)

#3)The index of the holder/ingredients starts from 0 [0,1,2,3,4,5]),
#so self.percents[0] will be the percent associated with ingredient 0 and holder 0.

#4)sizes are be as follows: 0=shot, 1=regular, 2=batch
#self.size only returns one value
# if shot is selected, self.size = 0



class sensors_and_motors(object): 
    def _init_(self):
        self.percentages = gm.self.percentages # percents will be between (0-100)
        self.size = gm.self.size #size (0=shot,1=regular, 2 = batch)
        
    def pour_drink(self):
        #LED code for an example
        I1 = LED(12)
        I2 = LED(17)
        I3 = LED(15)
        I4 = LED(18)
        I5 = LED(19)
        I6 = LED(20)
        
        I = [I1,I2,I3,I4,I5,I6]
        print('percentages (index of element is bottle holder)=',self.percentages)
        
        for i in range(len(self.percentages)):
                I[i].on()
                sleep(self.percentages[i]/10)
                
                I[i].off()
                