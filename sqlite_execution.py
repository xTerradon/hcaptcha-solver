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
    
    def add_images(self, images, commit=True):
        """adds an image to the database"""
        self.cur.executemany(f"INSERT INTO {self.table_name}(file_path, captcha_string, source_url, solved, category) VALUES(?,?,?,?,?)",images)
        if commit : self.con.commit()

    def label_image(self, file_path, category, commit=True):
        """labels an image as solved with the given category"""

        assert category == True or category == False or category is None, "category must be a boolean or NONE"

        self.con.execute(f"UPDATE {self.table_name} SET solved = True, category = ? WHERE file_path = ?", (category, file_path))
        if commit : self.con.commit()

    def unlabel_images(self, file_paths, commit=True):
        """unlabels images as solved"""

        self.cur.executemany(f"UPDATE {self.table_name} SET solved = False, category = NULL WHERE file_path = ?", file_paths)
        if commit : self.con.commit()

    def get_amount_of_images(self):
        """returns the amount of images in the database for each captcha_string"""

        total_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} GROUP BY captcha_string").fetchall()
        return pd.Series([total_amount[1] for total_amount in total_amounts], index=[total_amount[0] for total_amount in total_amounts], name="total", dtype=int)
    
    def get_amount_of_solved_images(self):
        """returns the amount of solved images in the database for each captcha_string"""

        solved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} WHERE solved = True GROUP BY captcha_string").fetchall()

        return pd.Series([solved_amount[1] for solved_amount in solved_amounts], index=[solved_amount[0] for solved_amount in solved_amounts], name="solved", dtype=int)

    def get_amount_of_unsolved_images(self):
        """returns the amount of unsolved images in the database for each captcha_string"""

        unsolved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.table_name} WHERE solved = False GROUP BY captcha_string").fetchall()
        return pd.Series([unsolved_amount[1] for unsolved_amount in unsolved_amounts], index=[unsolved_amount[0] for unsolved_amount in unsolved_amounts], name="unsolved", dtype=int)

    def get_solved_unsolved_for_captcha_string(self, captcha_string):
        """retuns the amount of solvede and unsolved captchas for a given captcha string"""

        solved_unsolved = self.cur.execute(f"SELECT COUNT(*), solved FROM {self.table_name} WHERE captcha_string = ? GROUP BY solved ORDER BY solved", (captcha_string,)).fetchall()
        if len(solved_unsolved) == 1:
            # only solved
            return pd.Series([solved_unsolved[0][0], 0], index=["unsolved", "solved"], name=captcha_string, dtype=int)
        return pd.Series([solved_unsolved[0][0], solved_unsolved[1][0]], index=["unsolved", "solved"], name=captcha_string, dtype=int)

    def get_info(self):
        """get a df denoting total, unsolved and solved"""

        total_amounts = self.get_amount_of_images()
        solved_amounts = self.get_amount_of_solved_images()
        unsolved_amounts = self.get_amount_of_unsolved_images()
        return pd.concat((total_amounts, solved_amounts, unsolved_amounts), axis=1)

    def get_most_unsolved_captcha_string(self):
        """returns the captcha_string with the most unsolved captchas"""

        return self.get_amount_of_unsolved_images().sort_values(ascending=False).index[0]

    def get_captcha_strings(self):
        """returns all captcha_strings in the database"""

        return [a[0] for a in self.cur.execute(f"SELECT DISTINCT captcha_string FROM {self.table_name}").fetchall()]

    def get_unsolved_images_paths(self, captcha_string, number=9):
        """returns paths of unsolved images belonging to a captcha_string"""

        paths = self.cur.execute(f"SELECT file_path FROM {self.table_name} WHERE solved = False AND captcha_string = ? LIMIT {number}", (captcha_string,)).fetchall()
        return [path[0] for path in paths]

    def get_most_unsolved_images_paths(self, number=9):
        """returns paths of unsolved images belonging to the captcha_string with the most unsolved captchas"""

        return self.get_unsolved_images_paths(self.get_most_unsolved_captcha_string(), number=number)


    def commit(self):
        """commits changes to the database"""

        self.con.commit()
