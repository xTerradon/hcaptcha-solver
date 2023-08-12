> **This project is not packaged yet, but its functionality is shown in [./hcaptcha-solver/testing.ipynb](https://github.com/xTerradon/hcaptcha-solver/blob/main/hcaptcha-solver/testing.ipynb)**

## Intended Functionality
`Captcha_Solver` is the parent class from which one can call:
- `is_captcha_present(selenium.webdriver)`: returns True if a solvable hCaptcha is present, otherwise False
- `solve_captcha(selenium.webdriver)`: navigates to an available hCaptcha and solves it by clicking the correct images

## Current Functionality
- **Automated Captcha Scraping** with `selenium`
- **Manual Labeling Interface** with `tkinter`
- **Data Storage / Retrieval** with `sqlite3`
- **Training of CNN** with `pytorch`
- **Testing Loop for Pretrained ViLT models** from [huggingface](https://huggingface.co/dandelin/vilt-b32-finetuned-vqa)

## Data Availability
![Data Availability](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/044a5642-d3a7-47c1-b1ad-36eb43bbfc2e)


## Model Choice
hCaptcha has different tasks for which different ML models will be used.
- For the v1 ("Click each image that contains `item`") self-trained CNN models will be used to click the correct images.
- For the v2 ("Click on the `animal` in the image"), a YOLO model will be chosen under the same aspects.
- For the v3 ("Is this `animal` a 1. 2. 3. ?"), a self-trained CNN will be used to choose the correct answer.

Currently only the v1 version is ready-to-use; other tasks are skipped. The Program is capable of automatically solving several captcha types.

## Model Performance (v1)
![CNN Labeling Accuracy](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/4eb5d025-56a7-4e5d-91b9-5364a248f200)


_(updated 12 Aug. 2023)_
