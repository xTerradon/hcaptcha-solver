# get a screenshot of the canvas
# feed that into the cnn
# get the output location
# click that output location
# check if captcha was solved
# if yes, save the screenshot and the output location in the db

import v2_training

IMAGES_DIR_V2 = "dev\\images\\v2\\"

class V2_Handler:
    def __init__(self, db2):
        self.model = v2_training.Model_Training()
        self.db2 = db2
    
    def predict_image(self, image):
        pred = self.model.predict_pil(image)[0]
        print("prediction:", pred)

        clickable_area = image.crop((83,194,image.size[0]-83,527)).size
        print("clickable area:", clickable_area)

        # scale to image size
        pred = pred * clickable_area
        print("prediction:", pred)

        return pred

    
    def save_image(self, image, location_x, location_y):
        now = dt.now().strftime("%d-%H-%M-%S-%f")
        file_path = f"{IMAGES_DIR_V2}{now}.png"

        image.save(file_path)
        self.db2.add_image(file_path, location_x, location_y)
