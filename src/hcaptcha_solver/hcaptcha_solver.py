from . import webdriver_handler as wh
from . import model_handler as mh

from PIL import Image
from io import BytesIO
import requests
from requests import Session
from unidecode import unidecode

from matplotlib import pyplot as plt
import time

class Captcha_Solver:
    def __init__(self, verbose=True):
        self.verbose = verbose
        if self.verbose : print("Captcha_Solver is starting in verbose mode by default. To silence messages, pass verbose=False to constructor")
        self.models = mh.Model_Handler(verbose=self.verbose)

    def is_captcha_present(self, wd):
        """
        Checks if a hCaptcha is present on the currently viewed webdriver page.
        Returns True if a captcha is present, False otherwise.

        :param driver: The web driver instance representing the browser session.
        :type driver: WebDriver
        :return: True if a CAPTCHA is detected, False otherwise.
        :rtype: bool
        """

        return wh.is_captcha_present(wd)
    
    def solve_captcha(self, wd):
        """
        Solves a hCaptcha Checkbox on the currently viewed webdriver page.

        :param driver: The web driver instance representing the browser session.
        :type driver: WebDriver
        """

        if not wh.is_challenge_present(wd):
            if self.verbose : print("Launching hCaptcha...")
            wh.launch_captcha(wd)

        wh.refresh_all_v2(wd)
        if self.verbose : print("Found V1 Captcha")
        return self.solve_challenge(wd)


    def solve_challenge(self, wd, debug=False):
        """
        Solves an opened hCaptcha Challenge on the currently viewed webdriver page.
        
        :param driver: The web driver instance representing the browser session.
        :type driver: WebDriver
        """

        if not wh.is_challenge_present(wd):
            if self.verbose : print("No active hCaptcha challenge present. Try using solve_captcha() instead")
            return self.solve_captcha(wd)

        challenge_steps = wh.get_number_of_crumbs(wd)
        for i in range(challenge_steps):
            try:
                captcha_instructions, captcha_urls = wh.get_challenge_data(wd)
            except Exception as e:
                if self.verbose : print("Failed to get challenge data, trying again..."); print(e)
                wh.refresh_challenge(wd)
                return self.solve_captcha(wd)
                
            captcha_str = normalize_captcha_string(captcha_instructions)
            if self.verbose : print(f"Found Captcha task: {captcha_str}")

            if captcha_str not in list(self.models.models.keys()):
                if self.verbose : print(f"Model for captcha string {captcha_str} not found, trying again...")
                wh.refresh_challenge(wd)
                return self.solve_captcha(wd)
            
            if self.verbose : print("Found model for captcha string")

            with Session() as s:
                captcha_images = [Image.open(BytesIO(s.get(captcha_url).content)) for captcha_url in captcha_urls]

            try:
                image_labels = self.models.get_labels(captcha_str, captcha_images)
            except Exception as e:
                if self.verbose : print("Failed to get image labels, trying again..."); print(e)
                wh.refresh_challenge(wd)
                return self.solve_captcha(wd)

            try:
                wh.click_correct(wd, image_labels)
            except Exception as e:
                if self.verbose : print("Failed to click correct images, trying again..."); print(e)
                wh.refresh_challenge(wd)
                return self.solve_captcha(wd)

            if self.verbose : print("Clicked correct images")

            time.sleep(3)

        if not wh.is_captcha_solved(wd):
            if self.verbose : print("Captcha solving failed, trying again...")
            self.solve_challenge(wd)
        else:
            if self.verbose : print("Captcha solved successfully")
            return True


def normalize_captcha_string(captcha_str):
    """normalizes the captcha string"""

    if "Please click" not in captcha_str:
        print("""[WARNING] The captcha string does not appear to be english. \
        This version of hcaptcha-solver only supports english captchas, \
        consider changing the language of the webhandler""")

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
    captcha_str = captcha_str.replace("Please click each image containing ","")
    captcha_str = captcha_str.replace("Please click on all images containing a ","")
    captcha_str = captcha_str.replace("Please click on all images containing ","")
    return captcha_str