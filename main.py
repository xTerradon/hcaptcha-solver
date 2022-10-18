import math
import os
import sys
import time

import numpy as np

import img_classifier
import img_comparator
import wd_handler


def get_solutions(website_url):
    print("GETTING SOLUTIONS FOR", website_url)

    wd = wd_handler.Webdriver_Handler()
    print("WEBDRIVER INITIALIZED")
    
    demo_urls, captcha_urls = wd.get_all_images(website_url)

    print("DEMO IMGS", len(demo_urls))
    print("CAPTCHA IMGS", len(captcha_urls))

    model = img_classifier.Image_Classifier()
    print("NEURAL NET INITIALIZED")

    demo_preds = model.get_predictions_from_urls(demo_urls)
    captcha_preds = model.get_predictions_from_urls(captcha_urls)

    print("TOTAL PREDICTIONS",demo_preds.size + captcha_preds.size)

    result = img_comparator.get_best_indexes(demo_preds, captcha_preds)


if __name__ == "__main__":
    website_url = "https://accounts.hcaptcha.com/demo"
    get_solutions(website_url)