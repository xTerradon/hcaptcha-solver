import nn_handler
import wd_handler

import numpy as np

class Captcha_Solver:
    def __init__(self, website_url):
        self.nh = nn_handler.NN_Handler()
        available_models = self.nh.get_all_models()
        self.wh = wd_handler.Webdriver_Handler(website_url,available_models)
    
    def solve_captcha(self):
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

if __name__ == "__main__":
    cs = Captcha_Solver("https://accounts.hcaptcha.com/demo")
    cs.solve_captcha()
    #wdh = wd_handler.Webdriver_Handler("https://accounts.hcaptcha.com/demo")
    #wdh = wd_handler.Webdriver_Handler("https://account.proton.me/signup?plan=free&billing=12&minimumCycle=12&currency=EUR&language=en",available_models)
    #wdh = wd_handler.Webdriver_Handler("https://freebitco.in/login",available_models)