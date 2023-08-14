import time
from urllib.parse import urljoin, urlparse

import numpy as np
import requests
from PIL import Image
from skimage.transform import resize
from io import BytesIO

from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from difflib import SequenceMatcher

class Captcha_Webdriver_Handler:
    def __init__(self, ref):
        self.ref = ref
        self.wd = self.ref.wd
        print(self.wd.current_url)
        self.widget_state = 0
        self.timeout = 3

    
    def normalize_string(self, string):
        
        ratios = []
        for model_name in self.ref.available_models:
            ratios.append(SequenceMatcher(a=string,b=model_name).ratio())
        print(ratios)
        if max(ratios) > 0.5:
            return self.ref.available_models[np.argmax(np.array(ratios))]
        return "--unidentified--"


    def focus_on_root_frame(self):
        self.wd.switch_to.default_content()
        self.widget_state = 0
        print("Switched to root iframe")

    def focus_on_container_frame(self):
        self.wd.switch_to.default_content()
        iframe_titles = [iframe.get_attribute("title") for iframe in self.wd.find_elements(By.XPATH, "//iframe")]
        print(iframe_titles)
        for iframe_title in iframe_titles:
            self.wd.switch_to.default_content()
            iframe = self.wd.find_element(By.XPATH, "//iframe[@title=\""+iframe_title+"\"]")
            src = iframe.get_attribute("src")
            title = iframe.get_attribute("title")
            print("Looking in iframe",title)

            self.wd.switch_to.frame(iframe)
            if "hcaptcha.com" in src and "checkbox" in title:
                self.widget_state = 1
                print("Switched to hCaptcha Container iframe")
                return
            else:
                time.sleep(0.5)
                iframe_titles = [iframe.get_attribute("title") for iframe in self.wd.find_elements(By.XPATH, "//iframe")]
                print(iframe_titles)
                for iframe_title in iframe_titles:
                    iframe = self.wd.find_element(By.XPATH, "//iframe[@title=\""+iframe_title+"\"]")
                    src = iframe.get_attribute("src")
                    title = iframe.get_attribute("title")
                    print("Looking in iframe",title)
                    self.wd.switch_to.frame(iframe)
                    if "hcaptcha.com" in src and "checkbox" in title:
                        self.widget_state = 1
                        print("Switched to hCaptcha Container iframe")
                        return

        raise Exception("Could not switch to challenge hCaptcha container")
        

    def focus_on_challenge_frame(self):
        self.wd.switch_to.default_content()
        iframe_titles = [iframe.get_attribute("title") for iframe in self.wd.find_elements(By.XPATH, "//iframe")]
        print(iframe_titles)
        for iframe_title in iframe_titles:
            self.wd.switch_to.default_content()
            iframe = self.wd.find_element(By.XPATH, "//iframe[@title=\""+iframe_title+"\"]")
            src = iframe.get_attribute("src")
            title = iframe.get_attribute("title")
            print("Looking in iframe",title)

            self.wd.switch_to.frame(iframe)
            if "hcaptcha.com" in src and "Main content" in title:
                self.widget_state = 2
                print("Switched to hCaptcha Challenge iframe")
                return
            else:
                time.sleep(0.5)
                iframe_titles = [iframe.get_attribute("title") for iframe in self.wd.find_elements(By.XPATH, "//iframe")]
                print("2", iframe_titles)
                for iframe_title in iframe_titles:
                    iframe = self.wd.find_element(By.XPATH, "//iframe[@title=\""+iframe_title+"\"]")
                    src = iframe.get_attribute("src")
                    title = iframe.get_attribute("title")
                    print("Looking in iframe",title)
                    if "hcaptcha.com" in src and "Main content" in title:
                        self.wd.switch_to.frame(iframe)
                        self.widget_state = 2
                        print("Switched to hCaptcha Challenge iframe")
                        return

        raise Exception("Could not switch to hCaptcha challenge")

    
    def focus_on_frame(self, target_frame):
        if target_frame == self.widget_state:
            return
        
        if target_frame == 0:
            self.focus_on_root_frame()
            return
        if target_frame == 1:
            self.focus_on_root_frame()
            self.focus_on_container_frame()
            return
        if target_frame == 2:
            self.focus_on_root_frame()
            self.focus_on_challenge_frame()
            return


    def load_captcha(self):
        self.focus_on_frame(1)
        
        # click hCaptcha container
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div"))).click()
        print("Launched hCaptcha")


    def get_string(self):
        self.focus_on_frame(2)

        print("Trying to get captcha string")
        try:
            captcha_str = self.wd.find_element(By.XPATH, "//span[contains(text(),'click') and contains(text(),'image')]").text
        except:
            captcha_str = self.wd.find_element(By.XPATH, "//span[contains(text(),'click') and contains(text(),'image')]").text
        captcha_str = captcha_str.replace("Please click each image containing an ","")
        captcha_str = captcha_str.replace("Please click each image containing a ","")
        captcha_str = self.normalize_string(captcha_str)
        captcha_str = captcha_str.replace(" ","_")
        print("Got hCaptcha string:",captcha_str)
        return captcha_str
    
    def get_images(self):
        self.focus_on_frame(2)

        images = []
        print("Trying to get images")
        for i in range(9):
            try:
                img_url = WebDriverWait(self.wd, self.timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div")))
                img_url = img_url.get_attribute("style")
                img_url = img_url.split("url(\"")[1]
                img_url = img_url.split("\") ")[0]
            except:
                print("Cannot find Image",i+1)
            img_url = urljoin(self.wd.current_url, img_url)
            img_content = requests.get(img_url, stream=True).content
            img = np.array(Image.open(BytesIO(img_content)))
            if img.shape != (160,160,3):
                img = resize(img, (160,160))
            else:
                img = img / 255

            images.append(img)
        images = np.array(images)
        print("Got Captcha Images")
        return images
    
    def click_correct_images(self, predictions):
        self.focus_on_frame(2)

        corr = (predictions > 0.5)
        for i in range(9):
            if corr[i]:
                try:
                    print("Trying to click image", i+1)
                    WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]"))).click()
                    print("Clicked Image",i+1)
                except:
                    print("Cannot find Image",i+1)
                time.sleep(0.5)
        time.sleep(2.0)
        
        print("Trying to click next")
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'button-submit')]"))).click()
        print("Clicked next")
        time.sleep(0.2)
        
        
    def click_refresh(self):
        print("Trying to refresh")
        try:
            WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh-off')]//*[name()='svg']"))).click()
        except:
            WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh-on')]//*[name()='svg']"))).click()
        print("Clicked \"refresh\" button")
        time.sleep(0.2)


    def get_verification_status(self):
        self.focus_on_frame(1)

        check_div = WebDriverWait(self.wd, self.timeout).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'check')]")))
        print(check_div.value_of_css_property("display"))
        if check_div.value_of_css_property("display") == "block":
            return True
        return False