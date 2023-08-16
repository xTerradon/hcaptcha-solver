# hcaptcha-solver

![PyPI - Status](https://img.shields.io/pypi/status/hcaptcha-solver)
![PyPI](https://img.shields.io/pypi/v/hcaptcha-solver?color=blue&link=https%3A%2F%2Fpypi.org%2Fproject%2Fhcaptcha-solver%2F)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hcaptcha-solver)


a lightweight Python library for solving hCaptcha challenges with selenium and neural networks
> _**NOTE: this package is still in early development.  
> If you encounter any issues or unexpected behaviours, please report them!**_

## Installation

```bash
pip install hcaptcha-solver
```

## Usage

```python
from hcaptcha_solver import hcaptcha_solver
from selenium import webdriver

# setup chromedriver in english (other languages not supported yet)
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
driver = webdriver.Chrome(options=options)
driver.get("https://accounts.hcaptcha.com/demo") # open any url with hCaptcha

# create Captcha_Solver object and solve Captcha
captcha_solver = hcaptcha_solver.Captcha_Solver(verbose=True)
captcha_solver.is_captcha_present(driver) # returns True
captcha_solver.solve_captcha(driver) # solves the hCaptcha
```

## Functionality

Only V1 hCaptchas are supported - any other captcha types will be skipped.  
The correct images are selected using Convolutional Neural Networks trained on labeled hCaptcha data.  
The models are chosen by inspecting the captcha header, so the language has to be english in order for the matching to work. (See [Issue #6](https://github.com/xTerradon/hcaptcha-solver/issues/6))

The package features models for a handful of hCaptcha tasks. The currently available models and their labeling accuracies are visualized in the figure below. The accuracy was measured on limited data and is therefore not exact.

[Functionality for V2 captchas](https://github.com/xTerradon/hcaptcha-solver/issues/7) is planned in a similar way to V1 captchas.

### Current Model Labeling Performance
![Model Labeling Accuracy](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/83571a17-4f5d-430d-a50d-87e6a4dedf23)

### Current Data Availability
![Data Availability](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/c26eed84-9a04-40b3-b560-a9fb6453703b)


## Contributing
If you encounter any bug, error or unexpected behaviour in general, please report them with an issue giving as much detail as possible - I will try to make this package easy-to-use for everyone.

Forks and pull requests are very welcome. You can also create issues to discuss possible changes or improvements.

To help collecting captchas, run `dev/main.ipynb` and submit the results. In this notebook you can also explore the data availability and train models.

> _updated 15/08/2023_
