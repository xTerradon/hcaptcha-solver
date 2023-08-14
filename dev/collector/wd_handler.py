import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth

from datetime import datetime as dt
import os
import PIL.Image
from io import BytesIO

IMAGES_DIR_V2 = "../data/images/v2/"

class Webdriver_Handler:
    def __init__(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument("--window-size=800,820")

        options.add_experimental_option('useAutomationExtension', False)

        self.url = url

        self.timeout = 5

        self.wd = webdriver.Chrome(options=options)
        
        self.wd.implicitly_wait(self.timeout)
        stealth(
            self.wd,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        self.iframe = None


    def load_captcha(self):
        self.wd.get(self.url)
        print("Loaded Website")

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click()
        print("Launched hCaptcha")

        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, self.timeout).until(EC.visibility_of_element_located((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
        self.iframe_location = self.wd.find_element(By.XPATH, "//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]").location

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body")))

        print("Switched to Captcha")


    def get_all_and_skip(self, collect_v2=False):
        try: 
            self.wd.implicitly_wait(1)
            captcha_strs = self.wd.find_elements(By.XPATH, "//h2[@class='prompt-text']/span")
            self.wd.implicitly_wait(self.timeout)
            if captcha_strs == []:
                if collect_v2:
                    print("Captcha V2")

                    captcha_string = self.wd.find_element(By.XPATH, "//h2[@class='prompt-text']").text
                    captcha_string = captcha_string.replace("Please click on the ","").replace(" ","_")
                    
                    if captcha_string != "":
                        self.save_screenshot_of_canvas(captcha_string)
                    else:
                        print("No captcha string found, refreshing")
                    
                WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()
                return self.get_all_and_skip()

            print("Captcha V1")
            captcha_str = captcha_strs[0].text

            image_divs = self.wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='image']")

            urls = []
            for image_div in image_divs:
                ims = image_div.get_attribute("style")
                if "url" not in ims : continue

                img_url = ims.split("url(\"")[1].split("\") ")[0]
                urls.append(img_url)

            WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()
            # WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'submit button')]"))).click()

            return captcha_str, urls
        except Exception as e:
            print("ERROR:", e)
            self.load_captcha()
            return self.get_all_and_skip()
    
    def save_screenshot_of_canvas(self, captcha_string):
        now = dt.now().strftime("%d-%H-%M-%S-%f")
        if not os.path.exists(f"{IMAGES_DIR_V2}{captcha_string}"):
            os.makedirs(f"{IMAGES_DIR_V2}{captcha_string}")
        path = f"{IMAGES_DIR_V2}{captcha_string}/{now}.png"
        
        canvas_screenshot = self.wd.find_element(By.XPATH, "//div[@class='challenge-view']/canvas").screenshot_as_png

        PIL.Image.open(BytesIO(canvas_screenshot)).save(path)

        print(f"Saved screenshot to {path}")

