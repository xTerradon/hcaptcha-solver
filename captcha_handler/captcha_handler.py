import nn_handler
import captcha_wd_handler

import numpy as np

class Captcha_Handler:
    def __init__(self, ref):
        self.ref = ref
        self.wd = self.ref.wh.wd

        self.nh = nn_handler.NN_Handler()
        self.available_models = self.nh.get_all_models()
        
        self.wh = captcha_wd_handler.Captcha_Webdriver_Handler(self)

    
    def solve_captcha(self):
        print("Solving Captcha...")

        self.wh.load_captcha()

        while self.wh.get_verification_status() == False:
            captcha_string = self.wh.get_string()
            while self.nh.has_model(captcha_string) == False:
                self.wh.click_refresh()
                captcha_string= self.wh.get_string()
            
            images = self.wh.get_images()
            predictions = self.nh.predict_images(captcha_string, images)
            print(np.round(predictions.reshape((3,3)),2))

            self.wh.click_correct_images(predictions)
        print("Succesfully solved captcha!")

