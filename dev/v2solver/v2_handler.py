# get a screenshot of the canvas
# feed that into the cnn
# get the output location
# click that output location
# check if captcha was solved
# if yes, save the screenshot and the output location in the db

import v2_training
import v2_webdriver_handler as wh

import time
from datetime import datetime as dt


IMAGES_DIR_V2 = "data\\images\\v2\\"
CLICKABLE_AREA_BOUNDARIES = (83,194,417,527)
CLICKABLE_AREA_SIZE = (CLICKABLE_AREA_BOUNDARIES[2] - CLICKABLE_AREA_BOUNDARIES[0], CLICKABLE_AREA_BOUNDARIES[3] - CLICKABLE_AREA_BOUNDARIES[1])

class V2_Handler:
    def __init__(self, db2):
        self.model = v2_training.Model_Training()
        self.db2 = db2

    def solve_v2(self, wd):
        if not wh.is_challenge_present(wd):
            wh.launch_captcha(wd)
            time.sleep(3)
        wh.refresh_all_v1(wd)
        time.sleep(1)
        image, locations = self.solve_single_challenge_v2(wd)
        image2, locations2 = self.solve_single_challenge_v2(wd)

        if wh.is_captcha_solved(wd):
            current_url = wd.current_url
            self.save_image(current_url, image, locations)
            self.save_image(current_url, image2, locations2)
        else:
            print("Challenge was not solved, trying again...")
            time.sleep(5)
            self.solve_v2(wd)

    def solve_single_challenge_v2(self, wd):
        image = wh.get_challenge_data_v2(wd)

        print("Found Image:", image.size)
        display(image.resize((image.size[0]//2, image.size[1]//2)))
        display(image.crop(CLICKABLE_AREA_BOUNDARIES).resize((100,100)))

        click_position = self.predict_image(image)
        print(click_position)

        offset = 30
        img_click = image.crop((
            click_position[0]-offset, 
            click_position[1]-offset,  
            click_position[0]+offset, 
            click_position[1]+offset))
        
        display(img_click)

        wh.click_correct_v2(wd, click_position[0], click_position[1])

        time.sleep(2)

        return image, click_position

            
    def predict_image(self, image):
        pred = self.model.predict_pil(image)[0]
        print("prediction:", pred)

        # scale to image size
        click_absolute = pred * CLICKABLE_AREA_SIZE
        print("absolute click:", click_absolute)

        click_relative = (click_absolute[0] + CLICKABLE_AREA_BOUNDARIES[0], click_absolute[1] + CLICKABLE_AREA_BOUNDARIES[1])
        print("relative click:", click_relative)

        return click_relative

    
    def save_image(self, current_url, image, locations):
        now = dt.now().strftime("%d-%H-%M-%S-%f")
        relative_file_path = f"{now}.png"
        full_file_path = f"..\\..\\{IMAGES_DIR_V2}{relative_file_path}"

        image.save(full_file_path)
        self.db2.add_captcha(relative_file_path, current_url, locations[0], locations[1])
