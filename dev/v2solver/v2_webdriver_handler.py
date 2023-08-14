from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import time
import os
from PIL import Image
from io import BytesIO

def reload_page(wd : webdriver.Chrome):
    """reloads the current page"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    wd.refresh()
    print("Reloaded page")

def is_captcha_present(wd : webdriver.Chrome):
    """returns True if captcha is present, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"
    
    wd.switch_to.default_content()
    wd.switch_to.default_content()
    if wd.find_element(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]").is_displayed():
        return True
    else:
        return False

def is_challenge_present(wd : webdriver.Chrome):
    """returns True if challenge is present, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    if wd.find_element(By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]").is_displayed():
        return True
    else:
        return False

def launch_captcha(wd : webdriver.Chrome, timeout=5):
    """launch captcha from webdriver"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'checkbox')]")))
    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click() # click on body to launch captcha
    print("Launched hCaptcha")


def refresh_all_v2(wd : webdriver.Chrome, timeout=5):
    """skips all challenges until a v1 captcha is found"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    captcha_strs = wd.find_elements(By.XPATH, "//h2[@class='prompt-text']/span") # this span is only present in captcha v1
    if captcha_strs == []:
        print("Captcha V2 found, refreshing")
        refresh_challenge(wd, timeout)
        time.sleep(0.5)
        refresh_all_v2(wd, timeout)
    else:
        print("Captcha V1 found")

def refresh_all_v1(wd : webdriver.Chrome, timeout=5):
    """skips all challenges until a v2 captcha is found"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    captcha_strs = wd.find_elements(By.XPATH, "//h2[@class='prompt-text']/span") # this span is only present in captcha v1
    if captcha_strs != []:
        print("Captcha V1 found, refreshing")
        refresh_challenge(wd, timeout)
        time.sleep(0.5)
        refresh_all_v1(wd, timeout)
    else:
        if is_challenge_present(wd):
            print("Captcha V2 found")
        else:
            print("Captcha broke, starting again...")
            launch_captcha(wd)
            refresh_all_v1(wd)


def refresh_challenge(wd : webdriver.Chrome, timeout=5):
    """refreshes an opened challenge"""

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh button')]"))).click()


def get_challenge_data_v1(wd : webdriver.Chrome, timeout=5):
    """returns the captcha string and the image urls"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    captcha_str = wd.find_element(By.XPATH, "//h2[@class='prompt-text']/span").text

    image_divs = wd.find_elements(By.XPATH, "//div[@class='task-grid']//div[@class='image']") # challenge images
    image_style_strs = [image_div.get_attribute("style") for image_div in image_divs]

    assert len(image_divs) == 9, "Expected 9 images, got " + str(len(image_divs))

    urls = [image_style_str.split("url(\"")[1].split("\") ")[0] for image_style_str in image_style_strs]

    print("Got Captcha data")

    return captcha_str, urls

def get_challenge_data_v2(wd : webdriver.Chrome, timeout=5):
    """get a screenshot of the canvas"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    canvas_screenshot = wd.find_element(By.XPATH, "//div[@class='challenge-view']/canvas").screenshot_as_png
    image = Image.open(BytesIO(canvas_screenshot))

    return image


def abort(wd : webdriver.Chrome):
    """clicks on the plain html body to abort any captcha challenge"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body"))).click()
    print("Aborted Captcha")


def click_correct_v1(wd : webdriver.Chrome, is_correct : list, timeout=5):
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

    submit_captcha(wd, timeout)

def click_correct_v2(wd : webdriver.Chrome, x_position, y_position, timeout=5):
    """clicks on the specified position in an open challenge"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    canvas = wd.find_element(By.XPATH, "//div[@class='challenge-view']/canvas")

    ac = ActionChains(wd)

    print("clicking on", x_position, y_position)
    ac.move_to_element_with_offset(canvas, x_position-canvas.size["width"]/2, y_position-canvas.size["height"]/2).click().perform()

    time.sleep(5)

    submit_captcha(wd, timeout)

def click_along_borders(wd : webdriver.Chrome, bounding_box, timeout=5):

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))

    canvas = wd.find_element(By.XPATH, "//div[@class='challenge-view']/canvas")
    print(canvas.size)

    margin = 10
    upper_left = (margin + bounding_box[0] - canvas.size["width"]/2, margin + bounding_box[1] - canvas.size["height"]/2)
    upper_right = (-margin + bounding_box[2] - canvas.size["width"]/2, margin + bounding_box[1] - canvas.size["height"]/2)
    lower_left = (margin + bounding_box[0] - canvas.size["width"]/2, -margin + bounding_box[3] - canvas.size["height"]/2)
    lower_right = (-margin + bounding_box[2] - canvas.size["width"]/2, -margin + bounding_box[3] - canvas.size["height"]/2)

    ac = ActionChains(wd)
    while True:
        print("ul")
        ac.move_to_element_with_offset(canvas, upper_left[0], upper_left[1]).click().perform()
        time.sleep(0.5)
        ac.move_to_element_with_offset(canvas, upper_left[0]+15, upper_left[1]-15).click().perform()
        ac.move_to_element_with_offset(canvas, upper_right[0], upper_right[1]).click().perform()
        time.sleep(0.5)
        ac.move_to_element_with_offset(canvas, upper_right[0]+15, upper_right[1]-15).click().perform()
        ac.move_to_element_with_offset(canvas, lower_left[0], lower_left[1]).click().perform()
        time.sleep(0.5)
        ac.move_to_element_with_offset(canvas, lower_left[0]+15, lower_left[1]-15).click().perform()
        ac.move_to_element_with_offset(canvas, lower_right[0], lower_right[1]).click().perform()
        time.sleep(0.5)
        ac.move_to_element_with_offset(canvas, lower_right[0]+15, lower_right[1]-15).click().perform()


def draw_marker_on_canvas(wd : webdriver.Chrome, x_position, y_position, timeout=5):
    js_code = '''  
    function drawClickMarker(canvas, x, y) {  
        var ctx = canvas.getContext('2d');  
        ctx.beginPath();  
        ctx.arc(x, y, 5, 0, 2 * Math.PI, false);  
        ctx.fillStyle = 'red';  
        ctx.fill();  
        ctx.lineWidth = 2;  
        ctx.strokeStyle = '#003300';  
        ctx.stroke();  
    }  
    drawClickMarker(arguments[0], arguments[1], arguments[2]);  
    '''  
    
    wd.execute_script(js_code, wd.find_element(By.XPATH, "//canvas"), x_position, y_position)
    print("Marker drawn")


def submit_captcha(wd : webdriver.Chrome, timeout=5):
    """submits an open challenge"""

    WebDriverWait(wd, timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'submit button')]"))).click()

    print("Submitted captcha")

def is_captcha_solved(wd : webdriver.Chrome, timeout=5):
    """returns True if captcha is solved, False otherwise"""

    assert isinstance(wd, webdriver.Chrome), "webdriver must be a selenium.webdriver.Chrome instance"

    wd.switch_to.default_content()
    WebDriverWait(wd, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[contains(@src,'hcaptcha') and contains(@src,'challenge')]")))
    
    if wd.find_element(By.XPATH, "//div[@class='display-error']").get_attribute("aria-hidden") == "false":
        return False
    else:
        return True

    