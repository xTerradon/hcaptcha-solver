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
    def __init__(self, website_url, proxy = None):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_experimental_option('useAutomationExtension', False)

        self.website_url = website_url

        self.timeout = 10

        self.wd = None
        if proxy != None:
            self.timeout = 30
            options.add_argument('--proxy-server=%s' % proxy)

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


    def check_for_integrity(self):
        self.wd.implicitly_wait(0.5)
        if len(self.wd.find_elements(By.XPATH, "/html/body/pre")) == 0:
            self.wd.implicitly_wait(self.timeout)
            return
        else:
            print("Banned")
            self.wd.refresh()
            time.sleep(5)
            self.check_for_integrity()


    def load_captcha(self):
        
        self.wd.get(self.website_url)
        print("Loaded Website")

        self.check_for_integrity()

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[5]/form/fieldset/ul/li[2]/div/div/iframe")))
        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[1]/div/div/div[1]"))).click()
        print("Launched hCaptcha")

        self.get_all_and_skip()


    def get_all_and_skip(self):
        self.check_for_integrity()
        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, self.timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[6]/div[1]/iframe")))
        print("Loaded Captcha")

        captcha_str = self.wd.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[1]/h2/span").text
        print("Scraped hCaptcha string")

        urls = []
        for i in range(9):
            try:
                img_url = WebDriverWait(self.wd, self.timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                self.check_for_integrity()
                return self.load_captcha()
            img_url = urljoin(self.website_url, img_url)
            urls.append(img_url)
        print("Scraped Captcha Images")

        WebDriverWait(self.wd, self.timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[8]"))).click()

        return captcha_str, urls
    