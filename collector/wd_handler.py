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
    def __init__(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
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


    def load_captcha(self):
        self.wd.get(self.url)
        print("Loaded Website")

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click()
        print("Launched hCaptcha")

        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
        print("Switched to Captcha")


    def get_all_and_skip(self):
        try:
            captcha_str = self.wd.find_element(By.XPATH, "//h2[@class='prompt-text']/span").text
            print("Scraped hCaptcha string:", captcha_str)

            image_divs = self.wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='image']")
            print("Found image divs", image_divs)

            urls = []
            for image_div in image_divs:
                ims = image_div.get_attribute("style")
                if "url" not in ims : continue

                img_url = ims.split("url(\"")[1].split("\") ")[0]
                urls.append(img_url)

            print("Scraped Captcha Images")
            print(urls)

            WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()

            return captcha_str, urls
        except:
            self.load_captcha()
            return self.get_all_and_skip()
    