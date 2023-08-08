import sqlite3
import numpy as np
import pandas as pd
import os
from pathlib import Path

DB_FOLDER_PATH = Path("./src/databases/")

class Sqlite_Handler:
    def __init__(self, name="captchas"):
        self.con = sqlite3.connect(f"{DB_FOLDER_PATH}/{name}.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.table_name = self.create_captchas_table()

    def create_captchas_table(self, table_name="captchas"):
        """creates a table for captchas if it does not yet exist"""

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                captcha_string TEXT NOT NULL,
                source_url TEXT NOT NULL,
                solved BOOLEAN NOT NULL,
                category BOOLEAN)""")
        return table_name

    
    def add_image(self, file_path, captcha_string, source_url, solved=False, category=None, commit=True):
        """adds an image to the database"""
        self.cur.execute(f"INSERT INTO {self.table_name}(file_path, captcha_string, source_url, solved, category) VALUES(?,?,?,?,?)",(file_path, captcha_string, source_url, solved, category))
        if commit : self.con.commit()

    def label_image(self, file_path, category, commit=True):
        """labels an image as solved with the given category"""

        assert category == True or category == False or category is None, "category must be a boolean or NONE"

        self.con.execute(f"UPDATE {self.table_name} SET solved = True, category = ? WHERE file_path = ?", (category, file_path))
        if commit : self.con.commit()

    def get_amount_of_images(self):
        """returns the amount of images in the database for each captcha_string"""

        total_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} GROUP BY captcha_string").fetchall()
        return total_amounts
    
    def get_amount_of_solved_images(self):
        """returns the amount of solved images in the database for each captcha_string"""

        solved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} WHERE solved = True GROUP BY captcha_string").fetchall()
        return solved_amounts

    def get_amount_of_unsolved_images(self):
        """returns the amount of unsolved images in the database for each captcha_string"""

        unsolved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} WHERE solved = False GROUP BY captcha_string").fetchall()
        return unsolved_amounts

    def get_unsolved_images_paths(self, captcha_string):
        """returns paths of unsolved images belonging to a captcha_string"""

        paths = self.cur.execute(f"SELECT file_path FROM {self.table_name} WHERE solved = False AND captcha_string = ?", (captcha_string,)).fetchall()
        return paths

    def commit(self):
        """commits changes to the database"""

        self.con.commit()