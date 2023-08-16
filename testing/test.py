from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def solve_hcaptcha_page(driver):
    captcha_solver = hcaptcha_solver.Captcha_Solver(verbose=True)
    captcha_solver.is_captcha_present(driver)  # Returns True
    captcha_solver.solve_captcha(driver)  # Solves the hCaptcha

def main():
    # setup chromedriver in English (other languages not supported yet)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    driver = webdriver.Chrome(options=options)
    driver.get("https://accounts.hcaptcha.com/demo")  # Open any URL with hCaptcha

    try:
        # Solve both pages of hCaptcha
        solve_hcaptcha_page(driver)
        solve_hcaptcha_page(driver)

        input("Press Enter to close the browser tab...")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
