#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 10:58:47 2020

@author: Kayce Serafin
"""

from time import sleep
import RPi.GPIO as GPIO
import numpy as np

#1) self.percents[i] will be between 0-100 

#2) The length of self.percentages will depend on the number of liquid ingredients 
#for a sepcific recipe (up to six)

#3)The index of the holder/ingredients starts from 0 [0,1,2,3,4,5]),
#so self.percents[0] will be the percent associated with ingredient 0 and holder 0.

#4)sizes are be as follows: 0=regular, 1=batch
#self.size only returns one value

class sensors_and_motors(object): 
    def _init_(self):
        self.percentages = gm.self.percentages # percents will be between (0-100)
        self.size = gm.self.size #size (0=regular, 1 = batch)
        
    def pour_drink(self):
        pulseHorizontal = 17  # Stepper Drive Pulses
        directionHorizontal = 27  # Controller Direction Bit (High for Controller default / LOW to Force a Direction Change).
        enableHorizontal = 22  # Controller Enable Bit (High to Enable / LOW to Disable).
        pulseVertical = 10
        directionVertical = 9
        enableVertical = 11

        GPIO.setmode(GPIO.BCM)

        GPIO.setwarnings(False)

        GPIO.setup(pulseHorizontal, GPIO.OUT)
        GPIO.setup(directionHorizontal, GPIO.OUT)
        GPIO.setup(enableHorizontal, GPIO.OUT)
        GPIO.setup(pulseVertical, GPIO.OUT)
        GPIO.setup(directionVertical, GPIO.OUT)
        GPIO.setup(enableVertical, GPIO.OUT)

        delay = 0.0000001 # This is actually a delay between PUL pulses - effectively sets the motor rotation speed.

        def left(durationLeft):
            GPIO.output(enableHorizontal, GPIO.HIGH)    
            sleep(.5) # pause due to a possible change direction
            GPIO.output(directionHorizontal, GPIO.LOW)  
            for x in range(durationLeft): 
                GPIO.output(pulseHorizontal, GPIO.HIGH)
                sleep(delay)
                GPIO.output(pulseHorizontal, GPIO.LOW)
                sleep(delay)
            GPIO.output(enableHorizontal, GPIO.LOW)
            sleep(.5) # pause for possible change direction
            return

        def right(durationRight):
            GPIO.output(enableHorizontal, GPIO.HIGH)    
            sleep(.5) # pause due to a possible change direction
            GPIO.output(directionHorizontal, GPIO.HIGH)
            for y in range(durationRight):
                GPIO.output(pulseHorizontal, GPIO.HIGH)
                sleep(delay)
                GPIO.output(pulseHorizontal, GPIO.LOW)
                sleep(delay)
            GPIO.output(enableHorizontal, GPIO.LOW)
            sleep(.5) # pause for possible change direction
            return

        def down(durationDown):
            GPIO.output(enableVertical, GPIO.HIGH)
            sleep(.5) # pause due to a possible change direction
            GPIO.output(directionVertical, GPIO.LOW)
            for x in range(durationDown): 
                GPIO.output(pulseVertical, GPIO.HIGH)
                sleep(delay)
                GPIO.output(pulseVertical, GPIO.LOW)
                sleep(delay)
            GPIO.output(enableVertical, GPIO.LOW)
            sleep(.5) # pause for possible change direction
            return

        def up(durationUp):
            GPIO.output(enableVertical, GPIO.HIGH)
            sleep(.5) # pause due to a possible change direction
            GPIO.output(directionVertical, GPIO.HIGH)
            for y in range(durationUp):
                GPIO.output(pulseVertical, GPIO.HIGH)
                sleep(delay)
                GPIO.output(pulseVertical, GPIO.LOW)
                sleep(delay)
            GPIO.output(enableVertical, GPIO.LOW)
            sleep(.5) # pause for possible change direction
            return
        
        def dispense():
            up(dispenseVal)
            sleep(1.5)
            down(dispenseVal)                 
        
        #print('percentages (index of element is bottle holder)=',self.percentages)
        bottles = np.count_nonzero(self.percentages)
        size = self.size        
        positions = 1
        loopcount = 0
        betweenBH = 8000
        dispenseVal = 4950
        toBH1 = 250
        #go to BH1
        right(toBH1)
        while bottles >= positions: #while we havn't been to every bottle we need to dispense from
            if loopcount != 0: #on first loop iteration, no need to move right, we are already at BH1
                right(betweenBH)
            if self.percentages[loopcount] != 0: #if ingredient is not zero
                if self.percentages[loopcount] < 10: # to avoid rounding an ingredient to zero
                    self.percentages[loopcount] = 10
                if self.size: #batch size 
                    for i in range( int(round(self.percentages[loopcount]/10))+1 ):
                        dispense()
                    positions = positions + 1
                else: #regular size
                    for i in range( int(round(self.percentages[loopcount]/10)) ):
                        dispense()
                    positions = positions + 1
            loopcount = loopcount + 1
        toHome = betweenBH*(loopcount - 1) + toBH1  #claculate steps returning to starting position      
        left(toHome) #return to start position
            
        GPIO.cleanup()
        GPIO.cleanup()
            
