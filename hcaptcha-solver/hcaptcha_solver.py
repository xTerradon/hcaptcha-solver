import webdriver_handler as wh
import model_handler as mh

from PIL import Image
from io import BytesIO
import requests
from requests import Session
from unidecode import unidecode


class Captcha_Solver:
    def __init__(self):
        self.models = mh.Model_Handler()
        pass

    def is_captcha_present(self, wd):
        return wh.is_captcha_present(wd)
    
    def solve_captcha(self, wd):
        wh.launch_captcha(wd)
        self.solve_challenge(wd)

    def solve_challenge(self, wd):
        captcha_instructions, captcha_urls = wh.get_challenge_data(wd)

        with Session() as s:
            captcha_images = [Image.open(BytesIO(s.get(captcha_url).content)) for captcha_url in captcha_urls]
        captcha_str = normalize_captcha_string(captcha_instructions)
        print(captcha_str)
        [display(img) for img in captcha_images]

        is_correct = self.models.solve_images(captcha_str, captcha_images)

        if not wh.click_correct(wd, is_correct):
            print("Captcha solving failed, trying again...")
            self.solve_challenge(wd)
        else:
            print("Captcha solved successfully")
            return True



def normalize_captcha_string(captcha_str):
    """normalizes the captcha string"""

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