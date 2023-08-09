import sqlite3
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from copy import deepcopy as copy

IMAGE_DIR = "./src/images/"


class Manual_Classifier:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.id_history = pd.DataFrame([], columns=["id","action"])

        self.window = tk.Tk()
        self.window.bind("<Key>",self.key_input)

        self.info_label = tk.Label(self.window, text="Loading...")
        self.captcha_selection = tk.StringVar()
        self.captcha_selection.set(self.db_handler.get_most_unsolved_captcha_string())

        self.captcha_selector = ttk.Combobox(self.window, textvariable=self.captcha_selection)
        self.captcha_selector['values'] =  self.db_handler.get_captcha_strings()
        self.captcha_selector.config(state="readonly")
        self.captcha_selector.bind('<<ComboboxSelected>>', lambda h : self.update_data())

        self.captcha_label = tk.Label(self.window, text="Loading...")

        self.decision_frame = tk.Frame(self.window)
        self.set_images()
        self.set_info_label()

        self.menu_frame = tk.Frame(self.window)
        self.go_back_button = tk.Button(self.menu_frame, text="Back")
        self.show_solved_button = tk.Button(self.menu_frame, text="Show Solved")
        self.continue_button = tk.Button(self.menu_frame, text="Continue")


        self.captcha_selector.pack(padx=5, pady=5)
        self.info_label.pack(padx=50)
        self.captcha_label.pack(padx=20, pady=5)
        self.decision_frame.pack(padx=5, pady=5)
        self.menu_frame.pack(padx=5, pady=5)

        self.go_back_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.show_solved_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.continue_button.pack(side=tk.LEFT, padx=5, pady=5)

        tk.mainloop()
    
    def update_data(self):
        self.set_images()
        self.set_info_label()
        self.window.update()
    
    def set_images(self):
        cs = self.captcha_selection.get()
        print(f"Setting images for {cs}")

        image_paths = self.db_handler.get_unsolved_images_paths(cs, number=9)
        images_pil = [Image.open(IMAGE_DIR+image_path).resize((200,200)) for image_path in image_paths]
        images_tk = [ImageTk.PhotoImage(image_pil, master=self.decision_frame) for image_pil in images_pil]

        self.image_buttons = []
        self.image_frames = []
        for i in range(9):
            self.image_frames.append(tk.Frame(
                self.decision_frame,
                highlightbackground="red",
                highlightthickness=10,
                bd=0, 
                height=210, 
                width=210))
            self.image_buttons.append(tk.Button(
                self.image_frames[-1], 
                image=images_tk[i],
                command=lambda : self.turn_red(self.image_frames[-1])))
            self.image_buttons[-1].image = images_tk[i]

            self.image_buttons[-1].pack()
            self.image_frames[-1].grid(row=i//3, column=i%3, padx=5, pady=5)


    
    def turn_red(self, i):
        print(i)
        i.config({"highlightbackground":"green"})
    
    def set_info_label(self):
        solvedinfo = self.db_handler.get_solved_unsolved_for_captcha_string(self.captcha_selection.get())
        self.info_label.config(text = f"Solved: {solvedinfo['solved']}, Unsolved: {solvedinfo['unsolved']}, Percentage: {round(solvedinfo['solved']/(solvedinfo['solved']+solvedinfo['unsolved'])*100,2)}%")
        self.captcha_label.config(text=self.captcha_selection.get())


    def key_input(self, event):
        if event.char == 'y':
            self.update_correct_value(1)
        elif event.char == 'n':
            self.update_correct_value(-1)
        elif event.char == 'r':
            self.load_last()
        else:
            print("KEYSTROKE NOT RECOGNIZED")