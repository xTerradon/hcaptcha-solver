import nn_handler
import wd_handler

import numpy as np


if __name__ == "__main__":
    nnh = nn_handler.NN_Handler()
    available_models = nnh.get_all_models()
    #wdh = wd_handler.Webdriver_Handler("https://accounts.hcaptcha.com/demo")
    wdh = wd_handler.Webdriver_Handler("https://freebitco.in/login",available_models)

    wdh.load_captcha()

    wdh.focus_on_captcha_frame()
    captcha_string = wdh.get_string()
    while nnh.has_model(captcha_string) == False:
        wdh.click_refresh()
        captcha_string= wdh.get_string()
    
    images = wdh.get_images()
    predictions = nnh.predict_images(captcha_string, images)
    print(np.round(predictions.reshape((3,3)),2))

    wdh.click_correct_images(predictions)

    wdh.focus_on_captcha_frame()
    captcha_string = wdh.get_string()
    while nnh.has_model(captcha_string) == False:
        wdh.click_refresh()
        captcha_string= wdh.get_string()
    
    images = wdh.get_images()
    predictions = nnh.predict_images(captcha_string, images)
    print(np.round(predictions.reshape((3,3)),2))

    wdh.click_correct_images(predictions)

    # check verification


    