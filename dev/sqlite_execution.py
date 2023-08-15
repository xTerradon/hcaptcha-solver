import sqlite3
import numpy as np
import pandas as pd
import os
from pathlib import Path
import PIL.Image
from scipy.stats import binom
import shutil



DATABASES_DIR = "../data/databases/"
IMAGES_DIR_V1 = "../data/images/v1/"
IMAGES_DIR_V2 = "../data/images/v2/"
MODEL_DIR_V1 = "../data/models/"
MODEL_DIR_SRC = "../src/hcaptcha_solver/models/"

class DB_V1:
    def __init__(self, name="captchas", dir_prefix=""):
        self.dir_prefix = dir_prefix
        self.con = sqlite3.connect(f"{dir_prefix}{DATABASES_DIR}/{name}.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.captchas_table_name = self.create_captchas_table()
        self.models_table_name = self.create_models_table()

    def create_captchas_table(self, table_name="captchas_v1"):
        """creates a table for captchas if it does not yet exist"""

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                captcha_string TEXT NOT NULL,
                source_url TEXT NOT NULL,
                solved BOOLEAN NOT NULL,
                category BOOLEAN)""")
        return table_name

    def create_models_table(self, table_name="models_v1"):
        """creates a table for models if it does not yet exist"""

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_path TEXT NOT NULL,
                captcha_string TEXT NOT NULL,
                date TEXT NOT NULL,
                training_samples INTEGER NOT NULL,
                testing_samples INTEGER NOT NULL,
                accuracy REAL NOT NULL,
                better_than_90 REAL NOT NULL,
                better_than_95 REAL NOT NULL)""")
        return table_name

    def add_model(self, model_path, captcha_string, training_samples, testing_samples, accuracy):
        """adds a model to the database"""

        better_than_90 = binom.cdf(int(round(testing_samples*accuracy)), testing_samples, 0.9)
        better_than_95 = binom.cdf(int(round(testing_samples*accuracy)), testing_samples, 0.95)

        self.cur.execute(f"INSERT INTO {self.models_table_name}(model_path, captcha_string, date, training_samples, testing_samples, accuracy, better_than_90, better_than_95) VALUES(?,?,?,?,?,?,?,?)",(model_path, captcha_string, str(pd.Timestamp.now()), training_samples, testing_samples, accuracy, better_than_90, better_than_95))
        self.con.commit()
    
    def get_model_info(self):
        """returns a df with the most accurate models for each captcha_string"""

        data = pd.DataFrame(
            self.cur.execute("""SELECT captcha_string, date, model_path, training_samples, testing_samples, MAX(accuracy) as accuracy, better_than_90, better_than_95 FROM models_v1 GROUP BY captcha_string ORDER BY accuracy DESC""").fetchall(), 
            columns=["captcha_string","date","path", "train_samples","test_samples","accuracy","better_than_90","better_than_95"])
        data.set_index("captcha_string",drop=True, inplace=True)
        data.rename_axis(None, inplace=True)
        data.date = pd.to_datetime(data.date).dt.date
        return data
    
    def load_models_into_src(self, threshold=0.9):
        model_info = self.get_model_info()
        model_info = model_info[model_info.accuracy > threshold]
        for captcha_string, path in list(zip(model_info.index, model_info.path)):
            print(captcha_string, path)
            destination_file = f'{MODEL_DIR_SRC}/{captcha_string}'
            shutil.copy(MODEL_DIR_V1 + path, destination_file)
            print(f'File copied and renamed to: {destination_file}')

    def add_image(self, file_path, captcha_string, source_url, solved=False, category=None, commit=True):
        """adds an image to the database"""
        self.cur.execute(f"INSERT INTO {self.captchas_table_name}(file_path, captcha_string, source_url, solved, category) VALUES(?,?,?,?,?)",(file_path, captcha_string, source_url, solved, category))
        if commit : self.con.commit()
    
    def add_images(self, images, commit=True):
        """adds an image to the database"""
        self.cur.executemany(f"INSERT INTO {self.captchas_table_name}(file_path, captcha_string, source_url, solved, category) VALUES(?,?,?,?,?)",images)
        if commit : self.con.commit()

    def label_image(self, file_path, category, commit=True):
        """labels an image as solved with the given category"""

        assert category == True or category == False or category is None, "category must be a boolean or NONE"

        self.con.execute(f"UPDATE {self.captchas_table_name} SET solved = True, category = ? WHERE file_path = ?", (category, file_path))
        if commit : self.con.commit()

    def unlabel_images(self, file_paths, commit=True):
        """unlabels images as solved"""

        self.cur.executemany(f"UPDATE {self.captchas_table_name} SET solved = False, category = NULL WHERE file_path = ?", file_paths)
        if commit : self.con.commit()

    def get_amount_of_images(self):
        """returns the amount of images in the database for each captcha_string"""

        total_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.captchas_table_name} GROUP BY captcha_string").fetchall()
        return pd.Series([total_amount[1] for total_amount in total_amounts], index=[total_amount[0] for total_amount in total_amounts], name="total", dtype=int)
    
    def get_amount_of_solved_images(self):
        """returns the amount of solved images in the database for each captcha_string"""

        solved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.captchas_table_name} WHERE solved = True GROUP BY captcha_string").fetchall()

        return pd.Series([solved_amount[1] for solved_amount in solved_amounts], index=[solved_amount[0] for solved_amount in solved_amounts], name="solved", dtype=int)

    def get_amount_of_unsolved_images(self):
        """returns the amount of unsolved images in the database for each captcha_string"""

        unsolved_amounts = self.cur.execute(f"SELECT captcha_string, COUNT(*) FROM {self.captchas_table_name} WHERE solved = False GROUP BY captcha_string").fetchall()
        return pd.Series([unsolved_amount[1] for unsolved_amount in unsolved_amounts], index=[unsolved_amount[0] for unsolved_amount in unsolved_amounts], name="unsolved", dtype=int)

    def get_solved_unsolved_for_captcha_string(self, captcha_string):
        """retuns the amount of solvede and unsolved captchas for a given captcha string"""

        solved_unsolved = self.cur.execute(f"SELECT COUNT(*), solved FROM {self.captchas_table_name} WHERE captcha_string = ? GROUP BY solved ORDER BY solved", (captcha_string,)).fetchall()
        if len(solved_unsolved) == 1:
            # either only solved or unsolved
            if solved_unsolved[0][1] == 1:
                return pd.Series([0, solved_unsolved[0][0]], index=["unsolved", "solved"], name=captcha_string, dtype=int)
            else:
                return pd.Series([solved_unsolved[0][0], 0], index=["unsolved", "solved"], name=captcha_string, dtype=int)
        return pd.Series([solved_unsolved[0][0], solved_unsolved[1][0]], index=["unsolved", "solved"], name=captcha_string, dtype=int)

    def get_info(self):
        """get a df denoting total, unsolved and solved"""

        total_amounts = self.get_amount_of_images()
        solved_amounts = self.get_amount_of_solved_images()
        unsolved_amounts = self.get_amount_of_unsolved_images()
        return pd.concat((total_amounts, solved_amounts, unsolved_amounts), axis=1).fillna(0).astype(int).sort_values(by=["solved","total"], ascending=False)

    def get_most_unsolved_captcha_string(self):
        """returns the captcha_string with the most unsolved captchas"""

        return self.get_amount_of_unsolved_images().sort_values(ascending=False).index[0]
    
    def get_most_solved_captcha_string(self):
        """returns the captcha_string with the most solved captchas"""

        return self.get_amount_of_solved_images().sort_values(ascending=False).index[0]

    def get_captcha_strings(self):
        """returns all captcha_strings in the database"""

        return [a[0] for a in self.cur.execute(f"SELECT DISTINCT captcha_string FROM {self.captchas_table_name}").fetchall()]

    def get_unsolved_images_paths(self, captcha_string, number=9, random=True):
        """returns paths of unsolved images belonging to a captcha_string"""
        
        if random:
            paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE id IN (SELECT id FROM {self.captchas_table_name} WHERE solved = False AND captcha_string = ? ORDER BY RANDOM() LIMIT {number})", (captcha_string,)).fetchall()
        else:
            paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = False AND captcha_string = ? LIMIT {number}", (captcha_string,)).fetchall()
        return [path[0] for path in paths]

    def get_solved_images_paths(self, captcha_string, number=9, random=True):
        """returns paths of solved images belonging to a captcha_string"""

        if random:
            paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE id IN (SELECT id FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = ? ORDER BY RANDOM() LIMIT {number})", (captcha_string,)).fetchall()
        else:
            paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = ? LIMIT {number}", (captcha_string,)).fetchall()
        return [path[0] for path in paths]

    def get_labeled_true_images_paths(self, captcha_string, number=9):
        """returns paths of labeled true images belonging to a captcha_string"""

        paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = ? AND category = True LIMIT {number}", (captcha_string,)).fetchall()
        return [path[0] for path in paths]
    
    def get_labeled_false_images_paths(self, captcha_string, number=9):
        """returns paths of labeled false images belonging to a captcha_string"""

        paths = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = ? AND category = False LIMIT {number}", (captcha_string,)).fetchall()
        return [path[0] for path in paths]

    def get_most_unsolved_images_paths(self, number=9):
        """returns paths of unsolved images belonging to the captcha_string with the most unsolved captchas"""

        return self.get_unsolved_images_paths(self.get_most_unsolved_captcha_string(), number=number)

    def get_solved_data(self, captcha_string, number=9):
        """returns data of solved images belonging to a captcha_string"""

        return pd.DataFrame(
            self.cur.execute(f"SELECT file_path, category FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = ? LIMIT {number}", (captcha_string,)).fetchall(), 
            columns=["path", "category"])


    def commit(self):
        """commits changes to the database"""
        
        self.con.commit()

    def remove_nonexisting_images(self, commit=True):
        """removes images from the database that do not exist anymore"""

        all_file_paths = [f[0] for f in self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name}").fetchall()]
        print(f"Found {len(all_file_paths)} images in database")

        removed = 0
        for file_path in all_file_paths:
            if not os.path.exists(IMAGES_DIR_V1+file_path):
                self.cur.execute(f"DELETE FROM {self.captchas_table_name} WHERE file_path = ?", (file_path,))
                removed += 1
        print(f"Removed {removed} non-existing images")
        if commit : self.commit()

    def drop_duplicates(self, commit=True):
        """drops duplicates in the database"""

        self.remove_nonexisting_images(commit=False)

        all_file_paths = [f[0] for f in self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name}").fetchall()]

        hashed = [np.asarray(PIL.Image.open(IMAGES_DIR_V1+file_path)).data.tobytes() for file_path in all_file_paths]
        un = np.unique(hashed, return_index=True, return_counts=True)

        duplicate_indexes = np.delete(np.arange(len(all_file_paths)),un[1])
        duplicate_filepaths = [(all_file_paths[i],) for i in duplicate_indexes]
        
        self.cur.executemany(f"DELETE FROM {self.captchas_table_name} WHERE file_path = ?", duplicate_filepaths)

        for file_path in duplicate_filepaths:
            os.remove(IMAGES_DIR_V1+file_path[0])

        if commit : self.commit()

        print(f"Removed {len(duplicate_filepaths)} duplicates from database")

class DB_V2:
    def __init__(self, name="captchas", dir_prefix=""):
        self.dir_prefix = dir_prefix
        self.con = sqlite3.connect(f"{dir_prefix}{DATABASES_DIR}/{name}.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.captchas_table_name = self.create_captchas_table()

    def create_captchas_table(self, table_name="captchas_v2"):
        """creates a table for captchas if it does not yet exist"""

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                captcha_string TEXT NOT NULL,
                file_path TEXT NOT NULL,
                source_url TEXT NOT NULL,
                solved BOOLEAN NOT NULL,
                position_x INTEGER,
                position_y INTEGER)""")
        return table_name

    def commit(self):
        """commits changes to the database"""
        
        self.con.commit()

    def add_image(self, file_path, captcha_string, source_url, commit=True):
        """adds a captcha to the database"""

        self.cur.execute(f"INSERT INTO {self.captchas_table_name}(captcha_string, file_path, source_url, solved) VALUES(?,?,?,?)",(captcha_string, file_path, source_url, False))

        if commit : self.commit()
    
    
    def remove_nonexisting_images(self, commit=True):
        """removes images from the database that do not exist anymore"""

        all_file_paths = [f[0] for f in self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name}").fetchall()]
        print(f"Found {len(all_file_paths)} images in database")

        removed = 0
        for file_path in all_file_paths:
            if not os.path.exists(IMAGES_DIR_V2+file_path):
                self.cur.execute(f"DELETE FROM {self.captchas_table_name} WHERE file_path = ?", (file_path,))
                removed += 1
        print(f"Removed {removed} non-existing images")

        if commit : self.commit()

    def get_solved_captchas(self, count=10, captcha_string=None):
        """returns a list of captchas from the database"""

        if captcha_string is None:
            data = self.cur.execute(f"SELECT file_path, position_x, position_y FROM {self.captchas_table_name} WHERE solved = True LIMIT {count}").fetchall()
        else:
            data = self.cur.execute(f"SELECT file_path, position_x, position_y FROM {self.captchas_table_name} WHERE solved = True AND captcha_string = {captcha_string} LIMIT {count}").fetchall()

        image_paths = [IMAGES_DIR_V2+d[0] for d in data]
        positions = [(d[1], d[2]) for d in data]
        return image_paths, positions

    def get_unsolved_captchas(self, count=10, captcha_string=None):
        """returns a list of unsolved captchas from the database"""

        if captcha_string is None:
            data = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = False LIMIT {count}").fetchall()
        else:
            data = self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name} WHERE solved = False AND captcha_string = {captcha_string} LIMIT {count}").fetchall()

        image_paths = [IMAGES_DIR_V2+d[0] for d in data]
        return image_paths
    

    def add_position(self, file_path, position_x, position_y, commit=True):
        """adds a position to a captcha in the database"""

        self.cur.execute(f"UPDATE {self.captchas_table_name} SET solved = ?, position_x = ?, position_y = ? WHERE file_path = ?", (True, int(position_x), int(position_y), file_path))

        if commit : self.commit()

    def add_untracked_images(self, captcha_string):
        """adds existing images as unsolved captchas to the database"""

        all_file_paths = [f[0] for f in self.cur.execute(f"SELECT file_path FROM {self.captchas_table_name}").fetchall()]

        added = 0
        for file_path in os.listdir(self.dir_prefix + IMAGES_DIR_V2 + "/" + captcha_string): # this is terrible pathing
            if captcha_string + "/" + file_path not in all_file_paths:
                added += 1
                self.add_image(captcha_string + "/" + file_path, captcha_string, "unknown", commit=False)
        print(f"Added {added} untracked images")

        self.commit() 