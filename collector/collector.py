import sqlite3
import threading
import time
from io import BytesIO

import numpy as np
import requests
import wd_handler
from PIL import Image
from datetime import datetime as dt
import os

from unidecode import unidecode


def get_binary_from_image(filename):
    """converts digital data to binary format"""

    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def normalize_captcha_string(captcha_str):
    captcha_str = unidecode(captcha_str)
    captcha_str = captcha_str.replace("Please click each image containing an ","")
    captcha_str = captcha_str.replace("Please click each image containing a ","")
    return captcha_str

def collect_data(db_handler, url="https://accounts.hcaptcha.com/demo"):
    url_str = url.replace("https://","").replace("http://","")
    wd = wd_handler.Webdriver_Handler()
    
    for i in range(10):
        captcha_str, captcha_urls = wd.load_captcha(url)
        captcha_str = normalize_captcha_string(captcha_str)

        for captcha_url in captcha_urls:
            img = requests.get(captcha_url, stream=True).content
            print(img, type(img))
            img = Image.open(BytesIO(img))
            # img.show()

            now = dt.now().strftime("%d-%H-%M-%S-%f")
            file_path = f"./src/images/{captcha_str}/{now}.png"
            create_dir_if_not_exists(f"./src/images/{captcha_str}")
            img.save(file_path)

            db_handler.add_image(file_path.replace("./src/images/",""), captcha_str, url_str, solved=False, category=None, commit=False)
            print("Added image to db")
    
        db_handler.commit()
        print("Committed to db")

def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
