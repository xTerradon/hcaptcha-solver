import sqlite3

import numpy as np


def add_new(name):
    if name == "captchas":
        return

    table_name = name.replace(" ","_")

    con = sqlite3.connect(table_name+".db")
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS """+table_name+"""(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captcha_string TEXT NOT NULL,
            captcha_type TEXT NOT NULL,
            correct INTEGER,
            image BLOB NOT NULL,)""")
    #cur.execute("DROP TABLE duck")
    #cur.execute("DELETE FROM captchas WHERE captcha_string = \'duck\'")
    cur.execute("INSERT INTO "+table_name+" SELECT * FROM captchas WHERE captcha_string = \'"+name+"\'")
    cur.execute("DROP TABLE captchas")
    con.commit()

    con2 = sqlite3.connect("captchas.db")
    cur2 = con2.cursor()

    cur2.execute("DELETE FROM captchas WHERE captcha_string = \'"+name+"\'")
    con2.commit()

def vacuum(name):
    con = sqlite3.connect(name+".db")
    con.execute("VACUUM")
    con.commit()

def add_column_correct(name):
    con = sqlite3.connect(name+".db")
    con.execute("UPDATE "+name+" SET correct = 1 where captcha_type=\'demo\'")
    con.commit()

def get_unique_captcha_strings(name):
    con = sqlite3.connect(name+".db")
    captcha_strings = np.array(con.execute("SELECT captcha_string, COUNT(*) as count FROM captchas GROUP BY captcha_string ORDER BY count DESC").fetchall())
    print("TOTAL")
    print(captcha_strings)
    captcha_strings = np.array(con.execute("SELECT captcha_string, COUNT(*) as count FROM captchas WHERE correct != 0 GROUP BY captcha_string ORDER BY count DESC").fetchall())
    print("LABELED")
    print(captcha_strings)

get_unique_captcha_strings("captchas")

#add_new("cactus in a pot")
#add_column_correct("duck")

