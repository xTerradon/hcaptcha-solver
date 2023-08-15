from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver

# create Captcha_Solver object to load ML models
captcha_solver = hcaptcha_solver.Captcha_Solver()

# create webdriver and access website with hCaptcha
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'}) # set to english
driver = webdriver.Chrome(options=options)
driver.get("https://accounts.hcaptcha.com/demo")

# check for hCaptcha
captcha_solver.is_captcha_present(driver)

# solve hCaptcha
captcha_solver.solve_captcha(driver)
