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

        self.selection_frame = tk.Frame(self.window)

        self.info_label = tk.Label(self.selection_frame, text="Loading...")
        self.captcha_selection = tk.StringVar()
        self.captcha_selection.set(self.db_handler.get_most_unsolved_captcha_string())

        self.captcha_selector = ttk.Combobox(self.selection_frame, textvariable=self.captcha_selection)
        self.captcha_selector['values'] =  self.db_handler.get_captcha_strings()
        self.captcha_selector.config(state="readonly")
        self.captcha_selector.bind('<<ComboboxSelected>>', lambda h : self.update_data())

        self.captcha_label = tk.Label(self.selection_frame, text="Loading...", font=("Arial", 30))

        self.decision_frame = tk.Frame(self.window)
        self.set_images()
        self.set_info_label()

        self.menu_frame = tk.Frame(self.window, width=self.window.winfo_width(), height=10)
        self.go_back_button = tk.Button(self.menu_frame, text="Back", command=self.click_go_back, width=20, height=5)
        self.show_solved_button = tk.Button(self.menu_frame, text="Show Solved", command=self.show_all_solved, width=20, height=5) # TODO: new window with solved images
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
        self.set_images()
        self.set_info_label()
        self.window.update()
    
    def set_images(self):
        cs = self.captcha_selection.get()
        print(f"Setting images for {cs}")

        
        self.image_paths = self.db_handler.get_unsolved_images_paths(cs, number=9)
        self.selected_images = [False]*len(self.image_paths)

        images_pil = [Image.open(IMAGE_DIR+image_path).resize((150,150)) for image_path in self.image_paths]
        images_tk = [ImageTk.PhotoImage(image_pil, master=self.decision_frame) for image_pil in images_pil]

        self.image_buttons = []
        self.image_frames = []


        for i in range(9):
            if i > len(self.image_paths)-1:
                continue
            self.image_frames.append(tk.Frame(
                self.decision_frame,
                highlightbackground="gray",
                highlightthickness=5,
                bd=0, 
                height=160, 
                width=160))
            self.image_buttons.append(tk.Button(
                self.image_frames[-1], 
                image=images_tk[i],
                command=lambda button_index = i: self.clicked_button(button_index)))
            self.image_buttons[-1].image = images_tk[i]

            self.image_buttons[-1].pack()
            self.image_frames[-1].grid(row=i//3, column=i%3, padx=5, pady=5)


    
    def clicked_button(self, i):
        if self.selected_images[i] == False:
            # selected the image
            self.selected_images[i] = True
            self.image_frames[i].config({"highlightbackground":"blue", "highlightthickness":"5"})
        else:
            # unselected the image
            self.selected_images[i] = False
            self.image_frames[i].config({"highlightbackground":"gray", "highlightthickness":"5"})

    def click_continue(self):
        for i, selected in enumerate(self.selected_images):
            self.db_handler.label_image(self.image_paths[i], selected)
            print(f"labeled {self.image_paths[i]} as {selected}")
        self.id_history = pd.concat((self.id_history, pd.DataFrame({"id":self.image_paths, "action":self.selected_images})), ignore_index=True)
        self.update_data()
    
    def click_go_back(self):
        if len(self.id_history) >= 9:
            print("unlabeling", self.id_history["id"].values[-9:])
            self.db_handler.unlabel_images(self.id_history["id"].values[-9:].reshape((9,1)))
            self.id_history = self.id_history.iloc[:-9]
            self.update_data()
            print("undo last 9 actions")
        else:
            print("no actions to undo")
    
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
    
    def show_all_solved(self):
        self.extra_window = tk.Toplevel(self.window)
        self.extra_window.title("Solved Images")

        labeled_true = tk.Frame(self.extra_window, width=300, height=550)
        labeled_false = tk.Frame(self.extra_window, width=300, height=550)
        

        for i, image_path in enumerate(self.db_handler.get_labeled_true_images_paths(self.captcha_selection.get(), number=50)):
            image_pil = Image.open(IMAGE_DIR+image_path).resize((60,60))
            image_tk = ImageTk.PhotoImage(image_pil, master=self.extra_window)
            l = tk.Label(labeled_true, image=image_tk)
            l.image = image_tk
            l.grid(row=i//5, column=i%5, padx=2, pady=2)

        for i, image_path in enumerate(self.db_handler.get_labeled_false_images_paths(self.captcha_selection.get(), number=50)):
            image_pil = Image.open(IMAGE_DIR+image_path).resize((60,60))
            image_tk = ImageTk.PhotoImage(image_pil, master=self.extra_window)
            l = tk.Label(labeled_false, image=image_tk)
            l.image = image_tk
            l.grid(row=i//5, column=i%5, padx=2, pady=2)

        labeled_true.pack(side=tk.LEFT, padx=10, pady=5)
        labeled_false.pack(side=tk.RIGHT, padx=10, pady=5)

        self.extra_window.mainloop()