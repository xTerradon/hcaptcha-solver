from transformers import ViTFeatureExtractor, ViTForImageClassification

from PIL import Image

import requests
import os
from urllib.parse import urljoin, urlparse
import sys

import numpy as np
import math
import time

from copy import deepcopy as copy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument('disable-infobars')

wd = webdriver.Chrome("F:/python/chromedriver/chromedriver.exe", options=options)


feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

timeout = 5

def get_all_images(website_url):
    
    wd.get(website_url)
    print("Loaded Website")

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[5]/form/fieldset/ul/li[2]/div/div/iframe")))
    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div[1]/div/div/div[1]"))).click()
    print("Launched hCaptcha")

    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[6]/div[1]/iframe")))
    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]"))).click()
    print("Extended Demo Images")

    demo_urls = []
    for i in range(3):
        try:
            img_url = WebDriverWait(wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div["+str(i+1)+"]/div[1]/div[2]"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
        except:
            print(WebDriverWait(wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div[3]/div["+str(i+1)+"]/div[1]/div[2]"))).get_attribute("style"))
        img_url = urljoin(website_url, img_url)
        demo_urls.append(img_url)
    print("Added Demo Images")

    urls = []
    for i in range(9):
        try:
            img_url = WebDriverWait(wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style").split("url(\"")[1].split("\") ")[0]
        except:
            print(WebDriverWait(wd, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div["+str(i+1)+"]/div[2]/div"))).get_attribute("style"))
        img_url = urljoin(website_url, img_url)
        urls.append(img_url)
    print("Added Captcha Images")

    return demo_urls, urls

demo_urls, urls = get_all_images("https://accounts.hcaptcha.com/demo")

demo_counts = np.zeros(1000, dtype=int)
for i in range(3):
    url = demo_urls[i]

    print("DEMO IMAGE",i+1)
    raw_data = requests.get(url, stream=True).raw

    image = Image.open(raw_data)

    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    l = logits.sort(-1)[1].numpy()[0]

    demo_counts[l] += np.arange(1000)

    print([model.config.id2label[b] for b in l[-10:]])
    print()

demo_counts = np.array(demo_counts/3, dtype=int)

print("------------------------------")

counts = np.zeros((9,1000), dtype=int)

for i in range(9):
    url = urls[i]

    print("IMAGE",i+1)
    raw_data = requests.get(url, stream=True).raw

    image = Image.open(raw_data)

    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    l = logits.sort(-1)[1].numpy()[0]

    counts[i, l] += np.arange(1000)

    print([model.config.id2label[b] for b in l[-10:]])
    print()


sort_demo_counts = copy(demo_counts).argsort()
relevant_categories = sort_demo_counts[:50]

diffs = np.zeros(9)
for i in range(9):
    diffs[i] = np.sum(counts[i][relevant_categories])

res = np.array([model.config.id2label[b] for b in relevant_categories])
print("DEMO CATEGORIES", res)

print("DIFFS")
print(diffs.reshape((3,3)))
print("MEAN DIFF", round(diffs.mean()))
print("ANSWERS")
print((diffs < diffs.mean()).reshape((3,3)))