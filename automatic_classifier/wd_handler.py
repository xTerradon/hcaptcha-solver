import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


class Webdriver_Handler:
    def __init__(self, website_url):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_experimental_option('useAutomationExtension', False)

        self.website_url = website_url

        self.timeout = 10

        self.wd = None
        try:
            self.wd = webdriver.Chrome("F:/python/chromedriver/chromedriver.exe", options=options)
        except:
            print("chromedriver not found, trying different loc")
        if self.wd == None:
            try:
                self.wd = webdriver.Chrome("C:/Users/V61XNRQ/Desktop/Personal/apps/chromedriver_win32/chromedriver.exe", options=options)
            except:
                print("chromedriver not found, trying different loc")
                exit(-1)
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


    def load_captcha(self):
        
        self.wd.get(self.website_url)
        print("Loaded Website")

        try:
            WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha.com') and contains(@title,'checkbox')]")))
        except:
            print("No hCaptcha iframe found")
            return
        
        print("Switched to hCaptcha Launch iframe")
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[1]/div/div/div[1]"))).click()
        print("Launched hCaptcha")

        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha.com') and contains(@title,'Main content')]")))
        print("Switched to hCaptcha Challenge iframe")

    def get_string_and_images(self):
        captcha_str = self.wd.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[1]/h2/span").text
        captcha_str = captcha_str.replace("Please click each image containing an ","")
        captcha_str = captcha_str.replace("Please click each image containing a ","")
        print("Got hCaptcha string")

        images = []
        for i in range(9):
            try:
                img_url = WebDriverWait(self.wd, self.timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                self.check_for_integrity()
                return self.load_captcha()
            img_url = urljoin(self.website_url, img_url)
            img_content = requests.get(img_url, stream=True).content
            img = np.array(Image.open(BytesIO(img_content)))
            if img.shape != (160,160,3):
                img = resize(img, (160,160))
            else:
                img = img / 255

            images.append(img)
        print("Got Captcha Images")

        # select model based on captcha_str

        # model predictions

        # print predictions

  