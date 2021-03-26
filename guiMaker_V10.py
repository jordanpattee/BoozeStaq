#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 19:09:44 2020
Version 5

library of functions for making the BoozeStaq Gui 

*To use the web_images_to_local function, the df must contain https thumbnails

*To use get_image_name, the folder argument(path to folder) must contain images labeled with drink name

@author: Jordan Pattee
"""


import requests
#from PIL import Image, ImageTk
from PIL import Image, ImageTk
import io
import tkinter as tk
from tkinter import ttk
import pandas as pd
from os import walk
import os 
from gpiozero import LED
from time import sleep
import time
import re
import numpy as np
import sensors_and_motors_12_29_2020 as sm
from collections import Counter

class guiFuncs(object):
    path = '/home/pi/Desktop/Thumbnails/'
    
    window = tk.Tk()
    window.geometry('800x1200')
    tk.Grid.columnconfigure(window,0,weight=1)
    tk.Grid.rowconfigure(window,0,weight=1)
    
    large_font = 15
    small_font = 15
    thumbnail_font = 14

    image_size = (80,80)
    header_font = 'Georgia' #serif for header text
    header_font = 'Calibri' #serif for header text
    body_font = 'Calibri' #sans serif for body text
    
    large_padx = 100

    large_pady = 150
    
    grey_hex = '#efeff7'
    #grey_hex = '#f2f2f7'
    blue_green_hex = '#4ed4b3'
    blue_hex = '#5889cd'
    dark_grey_hex = '#575757'
    purple_hex = '#5856d6'
    blue2_hex ='#14729f'
    
    # edit the following three paths to math the location of the files
    main_image_path = '/home/pi/Desktop/main10.png'
    prev_set_path = '/home/pi/Desktop/recipe files/bottle_config.csv'
    main_menu_path = '/home/pi/Desktop/recipe files/updated_menu_2_28_2021V2.csv'
    
    default_bottles = ['Gin','Tequila','Sweet Vermouth','Bourbon','Whiskey','Amaretto']

    def create_frames(self):
        self.frame1 = tk.Frame(master=self.window, bg=self.grey_hex)
        self.frame1.grid(row=0, column=0, sticky='nswe')
            
        self.frame2 = tk.Frame(master=self.window, bg=self.grey_hex,highlightbackground=self.grey_hex,bd=10)
        self.frame2.grid(row=1, column=0, sticky='nswe')
            
        self.frame3 = tk.Frame(master=self.window, bg=self.grey_hex)
        self.frame3.grid(row=2, column=0, sticky='nswe')
       
            
    #get the names of all drinks from JPEG files in specified path    
    def get_image_names(self):
        
        f = []
        for(dirpath,dirnames,filenames) in walk(self.path):
            f.extend(filenames)
            break
        return f
    

    #clear all frames 
    def refresh_window(self): 
        try:
            self.frame1.destroy()
            self.frame2.destroy()
            self.frame3.destroy()
        except:
            self.create_frames()
            
    def get_main_image(self):
        main_img = Image.open(self.main_image_path)
        width, height = (800,400)
        main_img = ImageTk.PhotoImage(Image.open(self.main_image_path).resize((round(width*1),round(height*1))))
        
        return main_img
        
        
    def check_age(self):        
        SUI.selected = 0
        FUI.selected = 0 #reset sel sigs
        
        img_list, drinks = self.gen_thumbnails()
                
        pairs = {key:value for key,value in zip(drinks,img_list)} 
        sorted_pairs = sorted(pairs.items(), key=lambda x:x[0], reverse=False)
       
        self.drinks = [sorted_pairs[i][0] for i in range(len(sorted_pairs))]
        self.img_list = [sorted_pairs[i][1] for i in range(len(sorted_pairs))]
        
        self.refresh_window()
        self.create_frames()
        tk.Grid.rowconfigure(self.frame1,0,weight=1)
        tk.Grid.columnconfigure(self.frame1,0,weight=1)
       
        main_img = self.get_main_image()
        
        #welcome message
        tk.Label(self.frame1, image=main_img,bg=self.grey_hex,font=(self.header_font, self.large_font)).grid(row=0,column=0)
        
                 
        tk.Label(self.frame2, text='Are you over 21 years old?',padx=10,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        tk.Button(self.frame2,text='Yes',padx=self.large_padx, wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, self.large_font),relief='flat',command=self.choose_UI).grid(row=0,column=1,sticky='se')
        tk.Button(self.frame2,text = 'No',padx=self.large_padx,wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, self.large_font),relief='flat',command=self.timeout).grid(row=0,column=2,sticky='se')
      
        self.window.mainloop()
        
        
    def timeout(self):
        self.refresh_window()
        self.create_frames()
        tk.Label(self.frame1, text='Access denied. Timeout initiated.',bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        
        
        self.window.update()
        self.check_age()
        
    def choose_UI(self):
        self.refresh_window()
        self.create_frames()
        tk.Label(self.frame1, text='Please select an interface.',bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        
        tk.Button(self.frame2,text='Standard',padx = 150,pady = self.large_pady, wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, 18),relief='flat',command=SUI.open_menu).grid(row=0,column=1,sticky='news')
        tk.Button(self.frame2,text = 'Flexible',padx = 150,pady = self.large_pady,wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, 18),relief='flat',command=FUI.check_bottles).grid(row=0,column=2,sticky='news')
      
        self.window.mainloop()
        
    
    def gen_thumbnails(self):
        img_list = []
        drink_list = []
        
        path = self.path
        drinks = self.get_image_names()
        
        drinks_no_ext = [re.sub(r'.jpeg','',drinks[i]) for i in range(len(drinks))]
        self.menu = pd.read_csv(self.main_menu_path)
        
        
        for i in range(len(drinks_no_ext)):
            if(drinks_no_ext[i] in (self.menu.Name.to_list())):
               
                size = (100,100)
                img = ImageTk.PhotoImage(Image.open(path+drinks[i]).resize(size))
                
                img_list.append(img)
                drink_list.append(drinks_no_ext[i])
                
                
        return img_list, drink_list
            
        
                
    #get the drink names and tell user where to insert each ingredient
    def drink_info(self):
        self.refresh_window()
        self.create_frames()
        
        if(SUI.selected == 1):
            drink_choice = self.drinks[SUI.drink_choice.get() + SUI.shift]
            self.size = SUI.size_choice.get()
        elif(FUI.selected == 1):
            drink_choice = FUI.drinks[FUI.drink_choice.get() + FUI.shift]
            self.size = FUI.size_choice.get()
        
        self.recipe = self.menu[self.menu.Name == str(drink_choice)]
        
        
        ingredients = [self.recipe.Ingredient1.values[0],self.recipe.Ingredient2.values[0],self.recipe.Ingredient3.values[0],\
                       self.recipe.Ingredient4.values[0],self.recipe.Ingredient5.values[0],self.recipe.Ingredient6.values[0]]
        
        
        temp = np.array(ingredients)
        index = np.argwhere(temp == 'Empty')
        temp = np.delete(temp,index)
        
        ingredients = temp
        
        percentages = [self.recipe['Measure1 (percent)'].values[0],self.recipe['Measure2 (percent)'].values[0],self.recipe['Measure3 (percent)'].values[0],\
                       self.recipe['Measure4 (percent)'].values[0],self.recipe['Measure5 (percent)'].values[0],self.recipe['Measure6 (percent)'].values[0]]
        self.percentages = []
        self.ingredients = []
        
        #print(FUI.user_ingredients)
        
        
        dry_ingred = ['Orange Wedge', 'Olive','Maraschino Cherry']
        dashed_ingred = ['Angostura Bitters']
        juices = ['Lemon Juice', 'Lime Juice', 'Grapefruit Juice', 'Pineapple Juice', 'Orange Juice']
        
        bot_idx = 1
        
        self.fui_idxs = []
        for i in range(len(ingredients)):
            
            if ((ingredients[i] in dry_ingred) or (ingredients[i] in dashed_ingred) or (ingredients[i] in juices)):
                
                for j in range(len(dry_ingred)):
                    if(re.search(dry_ingred[j],ingredients[i],re.IGNORECASE) != None):
                        var = tk.StringVar()
                        var.set('Please add a/an ' +dry_ingred[j]+ ' after the drink is poured')
                        tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i+3,column=0,sticky='w') 
               
                for j in range(len(dashed_ingred)):   
                    if(re.search(dashed_ingred[j],ingredients[i],re.IGNORECASE) != None):
                        var = tk.StringVar()
                        var.set('Please add a dash of ' + dashed_ingred[j] +' after the drink is poured')
                        tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i+3,column=0,sticky='w') 
                
                for j in range(len(juices)):     
                    if(re.search(juices[j],ingredients[i],re.IGNORECASE) != None):
                        var = tk.StringVar()
                        var.set('Please add '+ juices[j] +' to taste after the drink is poured')
                        tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i+3,column=0,sticky='w') 
                          
            else:
                self.percentages.append(percentages[i])
                self.ingredients.append(ingredients[i])
                
                if(SUI.selected == 1):
                    var = tk.StringVar()
                    var.set('Please insert ' + ingredients[i] + ' into holder ' + str(bot_idx))
                    tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i,column=0,sticky='w')

                else:
                    rec = np.array(ingredients)
                    bot_locs = np.array(FUI.user_ingredients)
                    
                    for i in range(len(rec)):
                        if (not((rec[i] in dry_ingred) or (rec[i] in dashed_ingred) or (rec[i] in juices))):
                            loc = np.argwhere(bot_locs == rec[i])
                            self.fui_idxs.append(loc[0][0])

                            var = tk.StringVar()
                            var.set(ingredients[i] + ' is in holder ' + str(self.fui_idxs[i]+1))
                            tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i,column=0,sticky='w') 
                            
                
                bot_idx += 1
                
        

        tk.Grid.rowconfigure(self.frame2,0,weight=1)
        tk.Grid.columnconfigure(self.frame2,0,weight=1) 
        if(SUI.selected ==1):
            if (SUI.shift == 0):    
                tk.Button(self.frame2,text='Go Back to Menu', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=SUI.open_menu).grid(row=0,column=0,sticky='e') 
            elif(SUI.shift == 8):
                tk.Button(self.frame2,text='Go Back to Menu', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=SUI.page2).grid(row=0,column=0,sticky='e') 
            elif(SUI.shift == 16):    
                tk.Button(self.frame2,text='Go Back to Menu', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=SUI.page3).grid(row=0,column=0,sticky='e') 
            else:
                tk.Button(self.frame2,text='Go Back to Menu', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=SUI.page4).grid(row=0,column=0,sticky='e') 
        else:   
                tk.Button(self.frame2,text='Go Back to Menu', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=FUI.open_menu).grid(row=0,column=0,sticky='e') 

        tk.Button(self.frame2,text='Continue', wraplength=200,bg=self.grey_hex,fg='black',font=(self.header_font,self.large_font),relief='flat',padx=100,bd=0,highlightbackground=self.grey_hex,command=self.modify_recipe).grid(row=0,column=1,sticky='w') 

        self.window.mainloop()
        
    def modify_recipe(self):
        self.refresh_window()
        self.create_frames()
        for i in range(len(self.percentages)):
             var = tk.StringVar()
             var.set('This recipe calls for ' + str(self.percentages[i])+'% of ' + str(self.ingredients[i]) )
             tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i,column=0,sticky='w') 

        tk.Label(self.frame2, text='Would you like to adjust these percentages?',bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        tk.Button(self.frame2,text='Yes',padx=self.large_padx, wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, self.large_font),relief='flat',command=self.new_percentages).grid(row=0,column=1,sticky='se')
        tk.Button(self.frame2,text = 'No',padx=self.large_padx,wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, self.large_font),relief='flat',command=self.insert_cup).grid(row=0,column=2,sticky='se')

        self.window.mainloop()
        
    def new_percentages(self):
        self.refresh_window()
        self.create_frames()
        
        self.entries = []
        for i in range(len(self.percentages)):
             var = tk.StringVar()
             var.set(str(self.ingredients[i]))
             
             tk.Label(self.frame1 ,textvariable = var, wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=i,column=0,sticky='w') 
             self.entries.append(tk.Scale(self.frame1,from_=0,to=100,orient=tk.HORIZONTAL,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex))
             self.entries[i].grid(row=i,column=1,sticky='w')

        tk.Button(self.frame1,text = 'Enter',wraplength=200,padx=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.body_font, self.large_font),relief='flat',command=self.get_percentages).grid(row=7,column=0,sticky='nswe')

        self.window.mainloop()
        
        
    def get_percentages(self):
        self.percentages = [int(self.entries[i].get()) for i in range(len(self.entries))]
        if(sum(self.percentages)== 100):
            self.insert_cup()
        else:
            tk.Label(self.frame3 ,text='The sum of the percentages for the ingredients must add to 100. Please adjust the percentages and press Enter'\
                     , wraplength=500,bg=self.grey_hex,fg='black',font=(self.body_font, self.small_font),relief='flat',pady=10,bd=0,highlightbackground=self.grey_hex).grid(row=0,column=0,sticky='w') 


    def insert_cup(self):
        self.refresh_window()
        self.create_frames()
        
        var = tk.StringVar()
        small_cup = 'Please insert BoozeStaq CUP with desired amount of ice into cupholder.'
        large_cup = 'Please insert BoozeStaq PITCHER with desired amount of ice into cupholder.'
        
        if (self.size == 0):
            var.set(small_cup)
            tk.Label(self.frame1, textvariable = var,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        else:
            var.set(large_cup)
            tk.Label(self.frame1, textvariable = var,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
            
        tk.Button(self.frame2,text = 'Go Back',wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.header_font, self.large_font),relief='flat',padx=100,command=self.drink_info).grid(row=0,column=0,sticky='w')
        tk.Button(self.frame2,text='Make Drink', wraplength=200,bg=self.grey_hex,fg='black',highlightbackground=self.grey_hex,font=(self.header_font, self.large_font),relief='flat',padx=100,command=self.waiting_screen).grid(row=0,column=1,sticky='e')

        self.window.mainloop()

    def waiting_screen(self):
        self.refresh_window()
        self.create_frames()
        tk.Label(self.frame1, text='Please wait while your drink is being made...',bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        
        
        self.window.update()
        self.make_drink()
        
    #code for making the drink
    def make_drink(self):
        
      print('this is where drink making code goes')
      if(SUI.selected == 1):
          while(len(self.percentages)!= 6):
              self.percentages.append(0)
      else:
          temp = np.array(np.zeros(6),dtype='int64')
          for i in range(len(self.percentages)):
              temp[self.fui_idxs[i]] = self.percentages[i]
          self.percentages = list(temp)
          
       
      sm.sensors_and_motors.pour_drink(self)
      self.drink_made()

        
    def drink_made(self):
        tk.Label(self.frame2, text='Your drink is ready. Make another?',bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font)).grid(row=0,column=0)
        if(SUI.selected == 1):
            tk.Button(self.frame2,text='Yes' ,padx=self.large_padx,wraplength=200,highlightbackground=self.grey_hex,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font),relief='flat',command=SUI.open_menu).grid(row=0,column=1,sticky='se')

        elif(FUI.selected == 1):
            tk.Button(self.frame2,text='Yes' ,padx=self.large_padx,wraplength=200,highlightbackground=self.grey_hex,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font),relief='flat',command=FUI.open_menu).grid(row=0,column=1,sticky='se')
     
    
        tk.Button(self.frame2,text = 'No',padx=self.large_padx,wraplength=200,highlightbackground=self.grey_hex,bg=self.grey_hex,fg='black',font=(self.body_font, self.large_font),relief='flat',command=self.check_age).grid(row=0,column=2,sticky='se')
        
        self.window.mainloop()

        

            
            
class standard_UI(object):
    shift = 0
    selected = 0
    drink_choice = tk.IntVar(value=0)
    size_choice = tk.IntVar(value=0)
    #create a menu 
    #path of the folder containing the labelled images
    def open_menu(self):
        self.selected = 1
        gf.refresh_window()
        gf.create_frames()
        
        #make the drinks label      
        tk.Label(gf.frame1,text='Choose a Drink', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        tk.Label(gf.frame1,text='Page 1/4', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=3)       
        
        row = 1
        col = 0
        
        for i in range(8):            
            tk.Grid.rowconfigure(gf.frame1,row,weight=1)
            tk.Grid.columnconfigure(gf.frame1,col,weight=1)
            tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)

            if (i%2 == 0):     
                tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            else:
                tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue2_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            col += 1  
            
            if(col == 4):
                col = 0
                row += 1
            
        tk.Button(gf.frame1,text='Next Page',command = self.page2, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=3)
         
        #make the size label       
        tk.Label(gf.frame2,text='Choose a Size'+'\t', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
        #create the size buttons
        for j in range(2):
            row = 0
            col = j+1
            sizes =['Regular','Batch']
            
            tk.Grid.rowconfigure(gf.frame2,row,weight=1)
            tk.Grid.columnconfigure(gf.frame2,col,weight=1)
            tk.Radiobutton(gf.frame2,text=sizes[j],font=(gf.header_font, gf.large_font),variable=self.size_choice, value=j, bg=gf.grey_hex,fg='black',bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col,sticky='w')
        
        
        #make drink button
        tk.Grid.rowconfigure(gf.frame3,0,weight=1)
        tk.Grid.columnconfigure(gf.frame3,0,weight=1)
        tk.Button(gf.frame3,text='Continue', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=150,bd=0,highlightbackground=gf.grey_hex,command=gf.drink_info).grid(row=0,column=0) 
        tk.Button(gf.frame3,text='Cancel', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=20,bd=0,highlightbackground=gf.grey_hex,command=gf.check_age).grid(row=0,column=3) 
                
        self.shift = 0
        
        self.window_width = gf.window.winfo_width()
        self.window_height = gf.window.winfo_height()
        
        gf.window.mainloop()
        
    #page2
    def page2(self):
        gf.refresh_window()
        gf.create_frames()

        #make the drinks label      
        tk.Label(gf.frame1,text='Choose a Drink', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        tk.Label(gf.frame1,text='Page 2/4', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=3)       
        
        row = 1
        col = 0
        
        for i in range(8):            
            tk.Grid.rowconfigure(gf.frame1,row,weight=1)
            tk.Grid.columnconfigure(gf.frame1,col,weight=1)
            tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)

            if (i%2 == 0):     
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+8],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+8], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            else:
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+8],variable=self.drink_choice, value=i, bg=gf.blue2_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+8], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            col += 1  
            
            if(col == 4):
                col = 0
                row += 1
            
        tk.Button(gf.frame1,text='Next Page',command = self.page3, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=3)
        tk.Button(gf.frame1,text='Previous Page',command = self.open_menu, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=0)
                 
        #make the size label       
        tk.Label(gf.frame2,text='Choose a Size'+'\t', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
        #create the size buttons
        for j in range(2):
            row = 0
            col = j+1
            sizes =['Regular','Batch']
            
            tk.Grid.rowconfigure(gf.frame2,row,weight=1)
            tk.Grid.columnconfigure(gf.frame2,col,weight=1)
            tk.Radiobutton(gf.frame2,text=sizes[j],font=(gf.header_font, gf.large_font),variable=self.size_choice, value=j, bg=gf.grey_hex,fg='black',bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col,sticky='w')
        
        
        #make drink button
        tk.Grid.rowconfigure(gf.frame3,0,weight=1)
        tk.Grid.columnconfigure(gf.frame3,0,weight=1)
        tk.Button(gf.frame3,text='Continue', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=200,bd=0,highlightbackground=gf.grey_hex,command=gf.drink_info).grid(row=0,column=0) 
        tk.Button(gf.frame3,text='Cancel', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=20,bd=0,highlightbackground=gf.grey_hex,command=gf.check_age).grid(row=0,column=3) 
                
        self.shift = 8
        self.window_width = gf.window.winfo_width()
        self.window_height = gf.window.winfo_height()
        
        gf.window.mainloop()

     
    #page3
    def page3(self):
        gf.refresh_window()
        gf.create_frames()

        #make the drinks label      
        tk.Label(gf.frame1,text='Choose a Drink', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        tk.Label(gf.frame1,text='Page 3/4', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=3)       
        row = 1
        col = 0
        
        for i in range(8):            
            tk.Grid.rowconfigure(gf.frame1,row,weight=1)
            tk.Grid.columnconfigure(gf.frame1,col,weight=1)
            tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)

            if (i%2 == 0):     
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+16],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+16], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            else:
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+16],variable=self.drink_choice, value=i, bg=gf.blue2_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+16], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            col += 1  
            
            if(col == 4):
                col = 0
                row += 1
            
        tk.Button(gf.frame1,text='Next Page',command = self.page4, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=3)
        tk.Button(gf.frame1,text='Previous Page',command = self.page2, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=0)
                 
        #make the size label       
        tk.Label(gf.frame2,text='Choose a Size'+'\t', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
        #create the size buttons
        for j in range(2):
            row = 0
            col = j+1
            sizes =['Regular','Batch']
            
            tk.Grid.rowconfigure(gf.frame2,row,weight=1)
            tk.Grid.columnconfigure(gf.frame2,col,weight=1)
            tk.Radiobutton(gf.frame2,text=sizes[j],font=(gf.header_font, gf.large_font),variable=self.size_choice, value=j, bg=gf.grey_hex,fg='black',bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col,sticky='w')
        
        
        #make drink button
        tk.Grid.rowconfigure(gf.frame3,0,weight=1)
        tk.Grid.columnconfigure(gf.frame3,0,weight=1)
        tk.Button(gf.frame3,text='Continue', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=200,bd=0,highlightbackground=gf.grey_hex,command=gf.drink_info).grid(row=0,column=0) 
        tk.Button(gf.frame3,text='Cancel', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=20,bd=0,highlightbackground=gf.grey_hex,command=gf.check_age).grid(row=0,column=3) 
                
        self.shift = 16
        
        self.window_width = gf.window.winfo_width()
        self.window_height = gf.window.winfo_height()
        
        gf.window.mainloop()
        
     
    #page3
    def page4(self):
        gf.refresh_window()
        gf.create_frames()
        
        #make the drinks label      
        tk.Label(gf.frame1,text='Choose a Drink', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        tk.Label(gf.frame1,text='Page 4/4', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=3)       
       
        row = 1
        col = 0
        
        for i in range(8):            
            tk.Grid.rowconfigure(gf.frame1,row,weight=1)
            tk.Grid.columnconfigure(gf.frame1,col,weight=1)
            tk.Radiobutton(gf.frame1,image=gf.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)

            if (i%2 == 0):     
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+24],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+24], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            else:
                tk.Radiobutton(gf.frame1,image=gf.img_list[i+24],variable=self.drink_choice, value=i, bg=gf.blue2_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=gf.drinks[i+24], wraplength=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col,sticky='se')

            col += 1  
            
            if(col == 4):
                col = 0
                row += 1
            
       
        tk.Button(gf.frame1,text='Previous Page',command = self.page3, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=0)
                 
        #make the size label       
        tk.Label(gf.frame2,text='Choose a Size'+'\t', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
        #create the size buttons
        for j in range(2):
            row = 0
            col = j+1
            sizes =['Regular','Batch']
            
            tk.Grid.rowconfigure(gf.frame2,row,weight=1)
            tk.Grid.columnconfigure(gf.frame2,col,weight=1)
            tk.Radiobutton(gf.frame2,text=sizes[j],font=(gf.header_font, gf.large_font),variable=self.size_choice, value=j, bg=gf.grey_hex,fg='black',bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col,sticky='w')
        
        
        #make drink button
        tk.Grid.rowconfigure(gf.frame3,0,weight=1)
        tk.Grid.columnconfigure(gf.frame3,0,weight=1)
        tk.Button(gf.frame3,text='Continue', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=200,bd=0,highlightbackground=gf.grey_hex,command=gf.drink_info).grid(row=0,column=0) 
        tk.Button(gf.frame3,text='Cancel', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=20,bd=0,highlightbackground=gf.grey_hex,command=gf.check_age).grid(row=0,column=3) 
                
        
        self.window_width = gf.window.winfo_width()
        self.window_height = gf.window.winfo_height()
        
        self.shift = 24
        
        gf.window.mainloop()
        
class flex_UI(object):
    shift = 0
    selected = 0
    drink_choice = tk.IntVar(value=0)
    size_choice = tk.IntVar(value=0)
    
            
    other_ingredients = ['Lemon Juice','Lime Juice','Olive','Orange Wedge','Maraschino Cherry',\
                        'Angostura Bitters','Grapefruit Juice', 'Pineapple Juice']
    
    def check_bottles(self):
        self.selected = 1
        gf.refresh_window()
        gf.create_frames()
       
        try:
            bottle_mem = pd.read_csv(gf.prev_set_path)
            self.bottle_config = bottle_mem.to_numpy()
            self.bottle_config = self.bottle_config.flatten()
        except:
            self.bottle_config = gf.default_bottles
            
        tk.Label(gf.frame1 ,text='Please confirm the location of the bottles', wraplength=500,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.large_font),relief='flat',pady=10,bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0,sticky='w')
            
        for i in range(len(self.bottle_config)):
            var = tk.StringVar()
            var.set(self.bottle_config[i] + ' is currently in holder ' + str(i+1))
            tk.Label(gf.frame2 ,textvariable = var, wraplength=500,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.small_font),relief='flat',pady=10,bd=0,highlightbackground=gf.grey_hex).grid(row=i,column=0,sticky='w')
        
        tk.Button(gf.frame3,text='Confirm',command = self.prev_bottles, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=3)
        tk.Button(gf.frame3,text='Change Bottles',command = self.set_bottles, font=(gf.header_font, gf.large_font),bg=gf.grey_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=3,column=0)
        
    
    def set_bottles(self):
        
        gf.refresh_window()
        gf.create_frames()
        
        tk.Label(gf.frame1, text='Please select your ingredients in the bottle holders',bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.large_font)).grid(row=0,column=0)
        
        total_ingredients = gf.menu.iloc[:,7:13]
        total_ingredients = total_ingredients.to_numpy()
        total_ingredients = total_ingredients.flatten().tolist()
        
        
        index = np.argwhere(total_ingredients == 'nan')
        total_ingredients = np.delete(total_ingredients,index)
      
        
        ingredient_dict = Counter(total_ingredients)
        ingredient_dict_sort = sorted(ingredient_dict.items(),key=lambda x: x[1], reverse=True)
        #print(ingredient_dict_sort)
       
                       
        ingredient_keys = sorted([i[0] for i in ingredient_dict_sort])
        #ingredient_values = [i[1] for i in ingredient_dict_sort]
        
        ingredient_keys[0] = 'Empty'
        #ingredient_values[0] = 0
        
        #print(ingredient_keys)

        for name in self.other_ingredients:
            try:
                ingredient_keys.remove(name)
            except:continue
            
        bottles = ['Holder 1','Holder 2','Holder 3','Holder 4','Holder 5','Holder 6']
        self.entries = []
        self.vars = []
        for i in range(len(bottles)):
             var = tk.StringVar()
             var.set(bottles[i])
             
             self.vars.append(tk.StringVar())
             self.vars[i].set(self.bottle_config[i])
             
             tk.Label(gf.frame2 ,textvariable = var, wraplength=500,padx=100,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.small_font),relief='flat',pady=10,bd=0,highlightbackground=gf.grey_hex).grid(row=i,column=0,sticky='w') 
             self.entries.append(ttk.Combobox(gf.frame2,textvariable = self.vars[i],width='20',values=[ingredient_keys[i] for i in range(len(ingredient_keys))]))
             self.entries[i].grid(row=i,column=1,sticky='w')
             
        tk.Button(gf.frame3,text = 'Enter',wraplength=200,padx=200,bg=gf.grey_hex,fg='black',highlightbackground=gf.grey_hex,font=(gf.body_font, gf.large_font),relief='flat',command=self.get_user_ingredients).grid(row=7,column=0,sticky='nswe')
        gf.window.mainloop()
        
    def get_user_ingredients(self,*args):
        self.user_ingredients=[self.vars[i].get() for i in range(len(self.vars))]
                
        df = pd.DataFrame({'Holder 1':[self.user_ingredients[0]],\
                          'Holder 2':[self.user_ingredients[1]],\
                          'Holder 3':[self.user_ingredients[2]],\
                          'Holder 4':[self.user_ingredients[3]],\
                          'Holder 5':[self.user_ingredients[4]],\
                          'Holder 6':[self.user_ingredients[5]]})
                          
        df.to_csv(gf.prev_set_path,header=True,index=False, mode='w') # EDIT PATH
        self.filter_recipes()

    def prev_bottles(self):
        self.user_ingredients = self.bottle_config
        self.filter_recipes()

    def filter_recipes(self):
        self.custom_menu = gf.menu
        temp = []
        self.user_ingredients = list(self.user_ingredients)
        self.user_ingredients.append('Empty')

        
        for i in range(len(self.custom_menu)):
            
            if((self.custom_menu.Ingredient1[i] in self.user_ingredients or self.custom_menu.Ingredient1[i] in self.other_ingredients)\
               and (self.custom_menu.Ingredient2[i] in self.user_ingredients or self.custom_menu.Ingredient2[i] in self.other_ingredients)\
               and (self.custom_menu.Ingredient3[i] in self.user_ingredients or self.custom_menu.Ingredient3[i] in self.other_ingredients)\
               and (self.custom_menu.Ingredient4[i] in self.user_ingredients or self.custom_menu.Ingredient4[i] in self.other_ingredients)\
               and (self.custom_menu.Ingredient5[i] in self.user_ingredients or self.custom_menu.Ingredient5[i] in self.other_ingredients)\
               and (self.custom_menu.Ingredient6[i] in self.user_ingredients or self.custom_menu.Ingredient6[i] in self.other_ingredients)):
                print()
               
            else:
                temp.append(i)
              
        self.custom_menu = self.custom_menu.drop(temp,axis=0)
        
        self.user_ingredients.pop()
        
        self.filter_thumbnails()
    
    def filter_thumbnails(self):
        user_drink_names = self.custom_menu.Name.to_numpy()
        all_drinks = np.array(gf.drinks)
        
        index = np.array([np.where(all_drinks == user_drink_names[i]) for i in range(len(user_drink_names))]).flatten()
        self.drinks = [gf.drinks[i] for i in index]
        self.img_list = [gf.img_list[i] for i in index]
        
        self.open_menu()
        
    #create a menu 
    #path of the folder containing the labelled images
    def open_menu(self):
        gf.refresh_window()
        gf.create_frames()
        
        #make the drinks label      
        tk.Label(gf.frame1,text='Choose a Drink', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        tk.Label(gf.frame1,text='Page 1/1', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=3)       
        
        row = 1
        col = 0
        
        for i in range(len(self.drinks)):            
            tk.Grid.rowconfigure(gf.frame1,row,weight=1)
            tk.Grid.columnconfigure(gf.frame1,col,weight=1)
            tk.Radiobutton(gf.frame1,image=self.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)

            if (i%2 == 0):     
                tk.Radiobutton(gf.frame1,image=self.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=self.drinks[i], wraplength=90,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col)

            else:
                tk.Radiobutton(gf.frame1,image=self.img_list[i],variable=self.drink_choice, value=i, bg=gf.blue2_hex,bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col)
                tk.Label(gf.frame1,text=self.drinks[i], wraplength=90,bg=gf.grey_hex,fg='black',font=(gf.body_font, gf.thumbnail_font,'bold'),relief='flat').grid(row=row,column=col)

            col += 1  
            
            if(col == 4):
                col = 0
                row += 1
            
        #make the size label       
        tk.Label(gf.frame2,text='Choose a Size'+'\t', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
        if(len(self.drinks) != 0):
            #create the size buttons
            for j in range(2):
                row = 0
                col = j+1
                sizes =['Regular','Batch']
                
                tk.Grid.rowconfigure(gf.frame2,row,weight=1)
                tk.Grid.columnconfigure(gf.frame2,col,weight=1)
                tk.Radiobutton(gf.frame2,text=sizes[j],font=(gf.header_font, gf.large_font),variable=self.size_choice, value=j, bg=gf.grey_hex,fg='black',bd=0,highlightbackground=gf.grey_hex).grid(row=row,column=col,sticky='w')
        else:
            tk.Grid.rowconfigure(gf.frame2,0,weight=1)
            tk.Grid.columnconfigure(gf.frame2,0,weight=1)
            tk.Label(gf.frame2,text='Sorry, you cannot make any drinks with this combination of ingredients. Check out the standard UI to view the cocktail recipes!', wraplength=gf.window.winfo_width(),bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',bd=0,highlightbackground=gf.grey_hex).grid(row=0,column=0) 
        
            
            
        #make drink button
        tk.Grid.rowconfigure(gf.frame3,0,weight=1)
        tk.Grid.columnconfigure(gf.frame3,0,weight=1)
        
        if(len(self.drinks) != 0):
           tk.Button(gf.frame3,text='Continue', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=100,bd=0,highlightbackground=gf.grey_hex,command=gf.drink_info).grid(row=0,column=1) 
        
        tk.Button(gf.frame3,text='Go Back', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=100,bd=0,highlightbackground=gf.grey_hex,command=self.check_bottles).grid(row=0,column=0) 
        tk.Button(gf.frame3,text='Cancel', wraplength=200,bg=gf.grey_hex,fg='black',font=(gf.header_font, gf.large_font),relief='flat',padx=50,bd=0,highlightbackground=gf.grey_hex,command=gf.check_age).grid(row=0,column=3) 
                
        self.shift = 0
        
        self.window_width = gf.window.winfo_width()
        self.window_height = gf.window.winfo_height()
        
        gf.window.mainloop()
        

gf = guiFuncs()
SUI = standard_UI()
FUI = flex_UI()

gf.check_age()
    
    
