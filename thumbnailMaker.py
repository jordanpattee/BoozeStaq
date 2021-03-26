#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 19:09:44 2020
functions for processing images downloaded from a website

@author: Jordan Pattee
"""


import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
import pandas as pd
from os import walk

#save jpegs from the https links to a local directory
#links/names obtained from The CocktailDB's free API 
#df must include a list of links to images and corresponding drink name
def web_images_to_local(df):
    
    thumbnails =  df.Thumbnail.to_list() #list of https links
    drinks = df.Name.to_list() #drink names
    
    for i in range(0,len(df)):
        link = thumbnails[i]
        name = drinks[i]
        
        image = requests.get(link).content #get the image as a byte object
        image = Image.open(io.BytesIO(image)) #convert from bytes 
        image = image.save(path+name+'.jpeg') #save the image 
    
#get the names of all drinks from JPEG files in specified path    
def get_image_names(folder):
    f = []
    for(dirpath,dirnames,filenames) in walk(folder):
        f.extend(filenames)
        break
    return f
