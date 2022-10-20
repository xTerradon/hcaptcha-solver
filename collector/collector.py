import sqlite3
import threading
import time
from io import BytesIO

import numpy as np
import requests
import wd_handler
from PIL import Image


def get_binary_from_image(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def collect_data():
    strs = []
    url = "https://accounts.hcaptcha.com/demo"

    con = sqlite3.connect("captchas.db", check_same_thread=False)
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS captchas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        captcha_string TEXT NOT NULL,
        captcha_type TEXT NOT NULL,
        correct INTEGER,
        image BLOB NOT NULL)""")

    wd = wd_handler.Webdriver_Handler(url)
    wd.load_captcha()
    
    while True:
        
        captcha_str, captcha_urls = wd.get_all_and_skip()
        captcha_str = captcha_str.replace("Please click each image containing an ","")
        captcha_str = captcha_str.replace("Please click each image containing a ","")
        
        for captcha_url in captcha_urls:
            demo_img = requests.get(captcha_url, stream=True).content
            cur.execute("INSERT INTO captchas(captcha_string, captcha_type, correct, image) VALUES(?,?,0,?)",(captcha_str, "captcha", demo_img))
            con.commit()
    
    img_content = cur.execute("SELECT image FROM captchas LIMIT 1").fetchone()[0]
    image = Image.open(BytesIO(img_content))
    image.show()
        
    # connect to url
    # click captcha
    # get string
    # get demo imgs
    # get captcha imgs
    # save all to db

if __name__ == '__main__':
    collect_data()
    