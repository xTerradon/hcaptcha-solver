# hcaptcha-solver

hcaptcha-solver is a lightweight Python library for solving hCaptcha challenges with selenium.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
py -m pip install --index-url https://test.pypi.org/simple/ --no-deps hcaptcha-solver
```

## Usage

```python
from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver

# create Captcha_Solver object to load ML models
captcha_solver = hcaptcha_solver.Captcha_Solver()

# create webdriver and access website with hCaptcha
driver = webdriver.Chrome()
driver.get("https://accounts.hcaptcha.com/demo")

# check for hCaptcha
captcha_solver.is_captcha_present(driver)

# solve hCaptcha
captcha_solver.solve_captcha(driver)

```

## Functionality

Currently, only v1 hCaptchas are supported. Any other captcha types will be skipped.
The correct images are selected using Convolutional Neural Networks trained on labeled hCaptcha data.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

You can also help collecting captchas using the `collector.py`.


## License

[MIT](https://choosealicense.com/licenses/mit/)
