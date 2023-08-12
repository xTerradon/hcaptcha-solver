from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time
import os
from PIL import Image

def is_captcha_present(wd : webdriver.Chrome):
    """returns True if captcha is present, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    try:
        WebDriverWait(wd, 1).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
        wd.switch_to.default_content()
        return True
    except:
        return False

def launch_captcha(wd : webdriver.Chrome, timeout=5):
    """launch captcha from webdriver"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click()
    print("Launched hCaptcha")

    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
    print("Switched to Captcha")


def get_challenge_data(wd : webdriver.Chrome, timeout=5):
    """returns the captcha string and the image urls"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    WebDriverWait(wd, timeout).until(EC.presence_of_element_located((By.XPATH, "//h2[@class='prompt-text']")))
    captcha_strs = wd.find_elements(By.XPATH, "//h2[@class='prompt-text']/span")
    if captcha_strs == []:
        print("Captcha V2 found, refreshing")
        WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()
        time.sleep(0.5)
        return get_challenge_data(wd, timeout)

    print("Captcha V1 found")
    captcha_str = captcha_strs[0].text
    print(captcha_str)

    image_divs = wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='image']")

    assert len(image_divs) == 9, "Expected 9 images, got " + str(len(image_divs))

    print([image_div.get_attribute("style") for image_div in image_divs])
    urls = [image_div.get_attribute("style").split("url(\"")[1].split("\") ")[0] for image_div in image_divs]

    return captcha_str, urls

def click_correct(wd : webdriver.Chrome, is_correct : list, timeout=5):
    """clicks the correct images"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"
    assert isinstance(is_correct, list), "is_correct must be a list"
    assert len(is_correct) == 9, "is_correct must be a list of length 9"

    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    image_divs = wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='border-focus']")

    assert len(image_divs) == 9, "Expected 9 images, got " + str(len(image_divs))

    for i in range(len(is_correct)):
        if is_correct[i]:
            image_divs[i].click()
            time.sleep(0.5)

    print("Clicked images")

    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'submit button')]"))).click()

    print("Submitted captcha")

    time.sleep(1.0)

    if wd.find_element(By.XPATH, "//div[@class='display-error']").get_attribute("aria-hidden") == "false":
        return False
    else:
        return True

    