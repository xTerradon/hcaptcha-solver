from flask import Flask
from flask_restful import Resource, Api, reqparse

import sys 
import os
sys.path.append(os.getcwd()+"\\captcha_solver")
print(sys.path)
from captcha_solver import Captcha_Solver

import time



class Captcha_API:
    class EchoService(Resource):
        def get(self):
            return {"data":"Hello There!"}, 200

    class SolvingService(Resource):
        def __init__(self):
            self.cs = Captcha_Solver()

        def get(self):
            return {"available_models":[]}, 200
        
        def post(self):
            start_time = time.time()
            parser = reqparse.RequestParser()
        
            parser.add_argument("captcha_string", type=str, help="The string denoting the objects to select in the hCaptcha challenge")
            parser.add_argument("images", help="The jpeg images to select in the hCaptcha challenge")
            
            args = parser.parse_args()
            captcha_string = args["captcha_string"]
            print("Captcha String:", captcha_string)

            normalized_string = self.cs.normalize_string(captcha_string)
            if normalized_string == "":
                return {"error":"could not find a model associated to the string \'captcha_string\'"}, 400

            images = args["images"]
            print("Images", images)

            if type(images) == dict:
                print("Converting image dictionary to list")
                images = list(images.values())

            
            predictions = list(self.cs.solve_captcha(captcha_string, images))

            total_time = time.time() - start_time

            return {
                "request_time":total_time, 
                "captcha_string":captcha_string,
                "normalized_string":normalized_string,
                "predictions":predictions
                }, 200
            

    def __init__(self):
        self.app = Flask("hCaptcha_solver")
        self.api = Api(self.app)

        self.api.add_resource(self.EchoService, "/echo")
        self.api.add_resource(self.SolvingService, "/solve")
    
    def run_api(self):
        self.app.run(debug=False)

if __name__ == "__main__":
    c_app = Captcha_API()
    c_app.run_api()

