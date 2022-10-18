import wd_handler
import numpy as np
import time
import sqlite3
import requests
from PIL import Image
from io import BytesIO

def get_binary_from_image(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def collect_data():
    strs = []
    url = "https://accounts.hcaptcha.com/demo"

    con = sqlite3.connect("captchas.db")
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS captchas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        captcha_string TEXT NOT NULL,
        captcha_type TEXT NOT NULL,
        image BLOB NOT NULL)""")

    wd = wd_handler.Webdriver_Handler("176.31.111.139:80")
    
    while True:
        captcha_str, demo_urls, captcha_urls = wd.get_all(url)
        captcha_str = captcha_str.replace("Please click each image containing a ","")

        for demo_url in demo_urls:
            demo_img = requests.get(demo_url, stream=True).content
            cur.execute("INSERT INTO captchas(captcha_string, captcha_type, image) VALUES(?,?,?)",(captcha_str, "demo", demo_img))
            con.commit()
        
        for captcha_url in captcha_urls:
            demo_img = requests.get(demo_url, stream=True).content
            cur.execute("INSERT INTO captchas(captcha_string, captcha_type, image) VALUES(?,?,?)",(captcha_str, "captcha", demo_img))
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