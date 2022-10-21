import nn_handler
import wd_handler

import numpy as np

if __name__ == "__main__":
    nnh = nn_handler.NN_Handler()
    wdh = wd_handler.Webdriver_Handler("https://accounts.hcaptcha.com/demo")

    wdh.load_captcha()

    captcha_string, images = wdh.get_string_and_images()
    while nnh.has_model(captcha_string) == False:
        wdh.skip_to_next_captcha()
        captcha_string, images = wdh.get_string_and_images()
    
    predictions = nnh.predict_images(captcha_string, images)
    print(predictions.reshape((3,3)))
    print(np.array(predictions > 0.5).reshape((3,3)))

    # click images

    # click next

    # scrape
    # predict
    # click images

    # click submit

    # check verification
    