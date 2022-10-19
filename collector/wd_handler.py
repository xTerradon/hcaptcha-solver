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
    def __init__(self, proxy = None):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_experimental_option('useAutomationExtension', False)

        self.timeout = 5

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
        print(self.wd.get_cookies())


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


    def get_all(self, website_url : str, timeout : int = 10):
        self.wd.get(website_url)
        print("Loaded Website")

        self.check_for_integrity()

        WebDriverWait(self.wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[5]/form/fieldset/ul/li[2]/div/div/iframe")))
        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[1]/div/div/div[1]"))).click()
        print("Launched hCaptcha")

        self.check_for_integrity()
        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[6]/div[1]/iframe")))

        captcha_str = self.wd.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[1]/h2/span").text
        print("Scraped hCaptcha string")
        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]"))).click()

        self.check_for_integrity()
        demo_urls = []
        for i in range(3):
            try:
                img_url = WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div["+str(i+1)+"]/div[1]/div[2]"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                self.check_for_integrity()
                return self.get_all(website_url)
            img_url = urljoin(website_url, img_url)
            demo_urls.append(img_url)
        print("Scraped Demo Images")

        urls = []
        for i in range(9):
            try:
                img_url = WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                print(WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style"))
            img_url = urljoin(website_url, img_url)
            urls.append(img_url)
        print("Scraped Captcha Images")

        return captcha_str, demo_urls, urls
    