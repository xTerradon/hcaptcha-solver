import sqlite3
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk


class Manual_Classifier:
    def __init__(self, name):
        self.name = name
        self.con = sqlite3.connect(self.name+".db")
        self.id_history = []
        print("Opened Table",self.name)
    
    def get_unique_captcha_strings(self):
        return list(np.array(self.con.execute("SELECT DISTINCT captcha_string FROM "+self.name+" ORDER BY captcha_string").fetchall())[:,0])
    
    def get_data(self):
        
        if self.captcha_selection.get() == "ALL":
            if len(self.id_history) == 0:
                max_id = 0
            else:
                max_id = max(self.id_history)
            self.number_total = self.con.execute("SELECT COUNT(rowid) FROM "+self.name).fetchone()[0]
            self.number_unclassified = self.con.execute("SELECT COUNT(rowid) FROM "+self.name+" WHERE correct = 0").fetchone()[0]
            element = self.con.execute("SELECT id, captcha_string, image, correct FROM "+self.name+" WHERE id > "+str(max_id)+" ORDER BY captcha_string LIMIT 1").fetchone()
        else:
            cs = self.captcha_selection.get()
            self.number_total = self.con.execute("SELECT COUNT(rowid) FROM "+self.name+" WHERE captcha_string = \'"+cs+"\'").fetchone()[0]
            self.number_unclassified = self.con.execute("SELECT COUNT(rowid) FROM "+self.name+" WHERE captcha_string = \'"+cs+"\' AND correct = 0").fetchone()[0]
            element = self.con.execute("SELECT id, captcha_string, image, correct FROM "+self.name+" WHERE captcha_string = \'"+cs+"\' AND correct = 0 ORDER BY captcha_string LIMIT 1").fetchone()
        if len(element) == 0:
            print("Could not resolve",self.captcha_selection.get())
            return
        self.img_id = element[0]
        self.id_history.append(self.img_id)
        self.captcha_string = element[1]
        img = Image.open(BytesIO(element[2])).resize((200,200))
        self.captcha_image = ImageTk.PhotoImage(img)
        self.current_correct = element[3]
    
    def mainloop(self):

        self.window = tk.Tk()
        self.window.bind("<Key>",self.key_input)

        self.info_label = tk.Label(self.window, text="Loading...")
        self.captcha_selection = tk.StringVar()
        self.captcha_selector = ttk.Combobox(self.window, textvariable=self.captcha_selection)
        print(self.get_unique_captcha_strings())
        self.captcha_selector['values'] = ["ALL"] + self.get_unique_captcha_strings()
        self.captcha_selector.config(state="readonly")
        self.captcha_selector.bind('<<ComboboxSelected>>', self.refresh_data)
        self.captcha_selection.set("ALL")
        self.captcha_label = tk.Label(self.window, text="Loading...")

        self.img_label = tk.Label()

        decision_frame = tk.Frame(self.window)

        yes_button = tk.Button(decision_frame, text="YES", command=lambda : self.update_correct_value(1), width=15, height=5)
        zero_button = tk.Button(decision_frame, text="0", command=lambda : self.update_correct_value(0), width=5, height=5)
        no_button = tk.Button(decision_frame, text="NO", command=lambda : self.update_correct_value(-1), width=15, height=5)

        revise_button = tk.Button(self.window, text="GO BACK", command=lambda : self.load_last(), width=15, height=2)

        self.captcha_selector.pack(padx=5, pady=5)
        self.info_label.pack(padx=50)
        self.captcha_label.pack(padx=20, pady=5)
        self.img_label.pack(padx=20, pady=5)
        
        yes_button.pack(side="left", padx=1, pady=1)
        zero_button.pack(side="left", padx=1, pady=1)
        no_button.pack(side="right", padx=1, pady=1)
        decision_frame.pack(padx=5, pady=5)

        revise_button.pack(padx=20, pady=5)

        self.get_data()
        self.load_data_to_ui()

        tk.mainloop()
    
    def key_input(self, event):
        if event.char == 'y':
            self.update_correct_value(1)
        elif event.char == 'n':
            self.update_correct_value(-1)
        elif event.char == 'r':
            self.load_last()
        else:
            print("KEYSTROKE NOT RECOGNIZED")
    
    def refresh_data(self, _):
        self.get_data()
        self.load_data_to_ui()

    def update_correct_value(self, value):
        self.set_correct_value(value)
        self.get_data()
        self.load_data_to_ui()
    
    def load_data_to_ui(self):
        self.info_label.config(text = "ID: "+str(self.img_id)+" "+str(self.current_correct)+" | Total: "+str(self.number_total)+" | Labeled: "+str(self.number_total-self.number_unclassified)+" "+str(round(100*(self.number_total-self.number_unclassified)/self.number_total))+"%")
        self.captcha_label.config(text=self.captcha_string)
        self.img_label.config(image = self.captcha_image)
        self.img_label.image = self.captcha_image
        self.window.update()
    
    def load_last(self):
        self.set_correct_value(0)
        if len(self.id_history) > 1:
            self.img_id = self.id_history[-2]
        else:
            print("No history")
            return
        self.set_correct_value(0)
        self.id_history = self.id_history[:-2]
        self.get_data()

        self.load_data_to_ui()
        

    def set_correct_value(self, value):
        if value != None:
            print("Setting",self.img_id,"to",value)
            self.con.execute("UPDATE "+self.name+" SET correct="+str(value)+" WHERE id="+str(self.img_id))
            self.con.commit()


mc = Manual_Classifier("captchas")
mc.mainloop()