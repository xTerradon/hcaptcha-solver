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
    
    wd.switch_to.default_content()

    if len(wd.find_elements(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")) == 0:
        return False
    
    if wd.find_element(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]").is_displayed():
        return True
    else:
        return False

def is_challenge_present(wd : webdriver.Chrome):
    """returns True if challenge is present, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()

    if len(wd.find_elements(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")) == 0:
        return False
    
    if wd.find_element(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]").is_displayed():
        return True
    else:
        return False

def launch_captcha(wd : webdriver.Chrome, timeout=5):
    """launch captcha from webdriver"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    if not is_captcha_present(wd):
        raise Exception("No hCaptcha challenge box present")
    
    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click() # click on body to launch captcha

def get_number_of_crumbs(wd : webdriver.Chrome, timeout=5):
    """returns the number of crumbs in the captcha"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    if not is_challenge_present(wd):
        raise Exception("No hCaptcha challenge box present")
    
    wd.switch_to.default_content()

    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    return max(len(wd.find_elements(By.XPATH, "//div[@class='Crumb']")),1)

def refresh_all_v2(wd : webdriver.Chrome, timeout=5):
    """skips all challenges until a v1 captcha is found"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
    
    while wd.find_elements(By.XPATH, "//h2[@class='prompt-text']") == []:
        time.sleep(0.1)

    captcha_strs = wd.find_elements(By.XPATH, "//h2[@class='prompt-text']/span") # this span is only present in captcha v1
    if captcha_strs == []:
        refresh_challenge(wd, timeout)
        time.sleep(0.5)
        refresh_all_v2(wd, timeout)

def refresh_challenge(wd : webdriver.Chrome, timeout=5):
    """refreshes an opened challenge"""

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()

    time.sleep(2) # this is not clean, but I don't know how to check if the challenge is refreshed

def get_challenge_data(wd : webdriver.Chrome, timeout=5):
    """returns the captcha string and the image urls"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    captcha_str = wd.find_element(By.XPATH, "//h2[@class='prompt-text']/span").text

    image_divs = wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='image']") # challenge images
    image_style_strs = [image_div.get_attribute("style") for image_div in image_divs]

    assert len(image_divs) == 9, "Expected 9 images, got " + str(len(image_divs))

    urls = [image_style_str.split("url(\"")[1].split("\") ")[0] for image_style_str in image_style_strs]

    return captcha_str, urls

def abort(wd : webdriver.Chrome):
    """clicks on the plain html body to abort any captcha challenge"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click()


def click_correct(wd : webdriver.Chrome, is_correct : list, timeout=5):
    """clicks the correct images in an open challenge"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"
    assert isinstance(is_correct, list), "is_correct must be a list"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    image_divs = wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='border-focus']")

    assert len(image_divs) >= len(is_correct), f"Expected {len(is_correct)} images, got only {len(image_divs)}"

    for i in range(len(is_correct)):
        if is_correct[i]:
            image_divs[i].click()
            time.sleep(0.5)

    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'submit button')]"))).click()


def is_captcha_solved(wd : webdriver.Chrome, timeout=5):
    """returns True if captcha is solved, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
    
    if wd.find_element(By.XPATH, "//div[@class='display-error']").get_attribute("aria-hidden") == "false":
        return False
    else:
        return True

    