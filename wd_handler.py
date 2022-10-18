from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Webdriver_Handler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')

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


    def get_all_images(self, website_url : str, timeout : int = 10):
        
        self.wd.get(website_url)
        print("Loaded Website")

        WebDriverWait(self.wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[5]/form/fieldset/ul/li[2]/div/div/iframe")))
        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[1]/div/div/div[1]"))).click()
        print("Launched hCaptcha")

        self.wd.switch_to.default_content()

        WebDriverWait(self.wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[6]/div[1]/iframe")))
        WebDriverWait(self.wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]"))).click()
        print("Extended Demo Images")

        demo_urls = []
        for i in range(3):
            try:
                img_url = WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div["+str(i+1)+"]/div[1]/div[2]"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                print(WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div["+str(i+1)+"]/div[1]/div[2]"))).get_attribute("style"))
            img_url = urljoin(website_url, img_url)
            demo_urls.append(img_url)
        print("Added Demo Images")

        urls = []
        for i in range(9):
            try:
                img_url = WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
            except:
                print(WebDriverWait(self.wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style"))
            img_url = urljoin(website_url, img_url)
            urls.append(img_url)
        print("Added Captcha Images")

        return demo_urls, urls