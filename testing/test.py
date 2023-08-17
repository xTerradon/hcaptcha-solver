from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver

# setup chromedriver in english (other languages not supported yet)
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
driver = webdriver.Chrome(options=options)
driver.get("https://accounts.hcaptcha.com/demo") # open any url with hCaptcha

# create Captcha_Solver object and solve captcha
captcha_solver = hcaptcha_solver.Captcha_Solver(verbose=True)
captcha_solver.is_captcha_present(driver) # returns True
captcha_solver.solve_captcha(driver) # solves the hCaptcha

input("Click any button to continue...")