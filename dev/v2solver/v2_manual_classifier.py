import sqlite3
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from copy import deepcopy as copy

IMAGES_DIR_V2 = "../../data/images/v2/"
CLICKABLE_AREA_BOUNDARIES = (83,194,417,527)


class Manual_Classifier:
    def __init__(self, db2):
        self.db2 = db2
        self.id_history = pd.DataFrame([], columns=["id","action"])

        self.window = tk.Tk()
        self.window.bind("<Key>",self.key_input)

        self.selection_frame = tk.Frame(self.window)

        self.info_label = tk.Label(self.selection_frame, text="Loading...")
        self.captcha_selection = tk.StringVar()
        self.captcha_selection.set(self.db2.get_captcha_strings()[0])

        self.captcha_selector = ttk.Combobox(self.selection_frame, textvariable=self.captcha_selection)
        self.captcha_selector['values'] =  self.db2.get_captcha_strings()
        self.captcha_selector.config(state="readonly")
        self.captcha_selector.bind('<<ComboboxSelected>>', lambda h : self.update_data())

        self.captcha_label = tk.Label(self.selection_frame, text="Loading...", font=("Arial", 30))

        self.decision_frame = tk.Frame(self.window)
        self.canvas = tk.Canvas(self.decision_frame, width=500, height=536)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click) 

        self.set_image()
        self.set_info_label()

        self.menu_frame = tk.Frame(self.window, width=self.window.winfo_width(), height=10)
        self.go_back_button = tk.Button(self.menu_frame, text="Back", command=self.click_go_back, width=20, height=5)
        self.show_solved_button = tk.Button(self.menu_frame, text="Show Solved", command=self.show_all_solved, width=20, height=5)
        self.continue_button = tk.Button(self.menu_frame, text="Continue", command=self.click_continue, width=20, height=5)

        self.selection_frame.pack(padx=5, pady=5)
        self.captcha_selector.pack(side=tk.LEFT, padx=5, pady=5)
        self.info_label.pack(side=tk.RIGHT, padx=50)
        self.captcha_label.pack(side=tk.LEFT, padx=20, pady=5)

        self.decision_frame.pack(padx=5, pady=5)

        self.go_back_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.show_solved_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.continue_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.menu_frame.pack(padx=5, pady=5)
        

        tk.mainloop()
    
    def update_data(self):
        self.set_image()
        self.set_info_label()
        self.window.update()
    
    def set_image(self):
        cs = self.captcha_selection.get()
        print(f"Setting images for {cs}")

        self.image_path = self.db2.get_unsolved_captchas(captcha_string=cs, count=1)[0]

        self.image_pil = Image.open(IMAGES_DIR_V2 + self.image_path)
        print(self.image_pil.size)
        display(self.image_pil)
        self.image_tk = ImageTk.PhotoImage(self.image_pil, master=self.decision_frame)

        self.canvas.create_image(0,0,anchor=tk.NW, image=self.image_tk)

        self.circle_marker = None
        self.x_position = None
        self.y_position = None

    def on_canvas_click(self, event):  
        if event.x > CLICKABLE_AREA_BOUNDARIES[0] and event.x < CLICKABLE_AREA_BOUNDARIES[2] and event.y > CLICKABLE_AREA_BOUNDARIES[1] and event.y < CLICKABLE_AREA_BOUNDARIES[3]:
            self.x_position = event.x - CLICKABLE_AREA_BOUNDARIES[0]
            self.y_position = event.y - CLICKABLE_AREA_BOUNDARIES[1]
            print(f"Clicked at x={self.x_position}, y={self.y_position}")  

            if self.circle_marker:
                self.canvas.delete(self.circle_marker)
            circle_size = 40
            self.circle_marker = self.canvas.create_oval(
                event.x-circle_size, 
                event.y-circle_size, 
                event.x+circle_size, 
                event.y+circle_size, 
                fill="", 
                outline="red",
                width=3)



    def click_continue(self):
        if self.x_position is None or self.y_position is None:
            print("No position selected")
            return
        self.db2.add_position(self.image_path, self.x_position, self.y_position)
        print(f"labeled {self.image_path} as {self.x_position}, {self.y_position}")
        self.id_history = pd.concat((self.id_history, pd.DataFrame({"id":[self.image_path], "x_position":[self.x_position], "y_position":[self.y_position]})), ignore_index=True)
        self.update_data()
    
    def click_go_back(self):
        if len(self.id_history) >= 1:
            print("unlabeling", self.id_history["id"].values[-1])
            self.db2.remove_postion(self.id_history["id"].values[-1])
            self.id_history = self.id_history.iloc[:-1]
            self.update_data()
            print("undo last action")
        else:
            print("no actions to undo")
    
    def set_info_label(self):
        solvedinfo = self.db2.get_solved_unsolved_for_captcha_string(self.captcha_selection.get())
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
    
    def show_all_solved(self):
        self.extra_window = tk.Toplevel(self.window)
        self.extra_window.title("Solved Images")

        frame = tk.Frame(self.extra_window, width=300, height=550)
        

        for i, (image_path, position) in enumerate(self.db2.get_solved_captchas(self.captcha_selection.get(), number=50)):
            image_pil = Image.open(image_path).resize((250,250))
            image_tk = ImageTk.PhotoImage(image_pil, master=self.extra_window)
            l = tk.Label(frame, image=image_tk)
            l.image = image_tk
            l.pack(padx=2, pady=2)

        frame.pack(side=tk.LEFT, padx=10, pady=5)

        self.extra_window.mainloop()