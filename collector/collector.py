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
import threading


def get_binary_from_image(filename):
    """converts digital data to binary format"""

    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def normalize_captcha_string(captcha_str):
    """normalizes the captcha string to a more readable format"""

    captcha_str = captcha_str.replace("\u0441","c")
    captcha_str = captcha_str.replace("\u043e","o")
    captcha_str = captcha_str.replace("\u0430","a")
    captcha_str = captcha_str.replace("\u0435","e")
    captcha_str = captcha_str.replace("\u043d","h")
    captcha_str = captcha_str.replace("\u0442","t")
    captcha_str = captcha_str.replace("\u043c","m")
    captcha_str = captcha_str.replace("\u043f","n")
    captcha_str = captcha_str.replace("\u0440","p")
    captcha_str = captcha_str.replace("\u0438","x")
    captcha_str = captcha_str.replace("\u043b","b")
    captcha_str = captcha_str.replace("\u0432","b")
    captcha_str = captcha_str.replace("\u044f","r")
    captcha_str = captcha_str.replace("\u0443","y")
    captcha_str = captcha_str.replace("\u0436","x")
    captcha_str = captcha_str.replace("\u043a","k")
    captcha_str = captcha_str.replace("\u0437","3")
    captcha_str = captcha_str.replace("\u0448","w")
    captcha_str = captcha_str.replace("\u0447","4")
    captcha_str = captcha_str.replace("\u0446","u")
    captcha_str = captcha_str.replace("\u0449","w")
    captcha_str = captcha_str.replace("\u044b","bl")

    captcha_str = unidecode(captcha_str)
    captcha_str = captcha_str.replace("Please click each image containing an ","")
    captcha_str = captcha_str.replace("Please click each image containing a ","")
    return captcha_str

def collect_data(db_handler, url="https://accounts.hcaptcha.com/demo", count=100):
    if type(url) == list:
        print(f"Starting Threads for {len(url)} URLs")
        [threading.Thread(target=lambda: collect_data(db_handler, single_url, count=count)).start() for single_url in url]
        return
    
    url_str = url.replace("https://","").replace("http://","")
    wd = wd_handler.Webdriver_Handler(url)
    wd.load_captcha()
    
    for i in range(count):
        captcha_str, captcha_urls = wd.get_all_and_skip()
        captcha_str = normalize_captcha_string(captcha_str)

        with requests.Session() as s:
            captcha_raw = [s.get(captcha_url).content for captcha_url in captcha_urls]

        captcha_images = [Image.open(BytesIO(img)) for img in captcha_raw]
        create_dir_if_not_exists(f"./src/images/v1/{captcha_str}")

        now = dt.now().strftime("%d-%H-%M-%S-%f")
        file_paths = [f"./src/images/v1/{captcha_str}/{now}_{i}.png" for i in range(len(captcha_images))]
        image_db_rows = [(file_path.replace("./src/images/v1",""), captcha_str, url_str, False, None) for file_path in file_paths]

        threading.Thread(target=save_images_async, args=(captcha_images,file_paths)).start()

        db_handler.add_images(image_db_rows)
        print("Added images to db")


def save_images_async(captcha_images, file_paths):
    for i in range(len(captcha_images)):
        captcha_images[i].save(file_paths[i])

def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
