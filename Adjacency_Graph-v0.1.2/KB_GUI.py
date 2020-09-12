# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 23:08:57 2019

@author: cosmic being
"""

import tkinter as tk
window=tk.Tk()
window.title("test")
window.geometry('500x300')
l=tk.Label(window,text='KB',bg='black',font=('Arial,12'),width=40,height=10)
l.pack()
window.mainloop