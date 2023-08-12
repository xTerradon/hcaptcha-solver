> _**This project is not in a ready-to-use state.** It is currently being overhauled and will soon be usable as a python package_

## Intended Functionality
`CaptchaSolver` is the parent class from which one can call:
- `is_captcha_present(selenium.webdriver)`: returns True if a solvable hCaptcha is present, otherwise False
- `solve_captcha(selenium.webdriver)`: navigates to an available hCaptcha and solves it by clicking the correct images

## Current Functionality
- **Automated Captcha Scraping** with `selenium`
- **Manual Labeling Interface** with `tkinter`
- **Data Storage / Retrieval** with `sqlite3`
- **Training of CNN** with `pytorch`
- **Testing Loop for Pretrained ViLT models** from [huggingface](https://huggingface.co/dandelin/vilt-b32-finetuned-vqa)

## Data Availability
<img src="https://github.com/xTerradon/hcaptcha-solver/assets/64305142/8e1e78ce-7476-437b-8a1d-69c50174a5e3" alt="Data Availability">

## Model Choice
hCaptcha has different tasks for which different ML models will be used.
For the v1 ("Click each image that contains ..."), the options are:
- **Pretrained ViLT model:** https://huggingface.co/dandelin/vilt-b32-finetuned-vqa \
  -> is slow has bad accuracy in some tasks (_see Figure "ViLT Accuracy on labeled data"_)
- **Finetuned ViLT model:** is slow and will take lots of time to train
- **Freshly trained CNNs:** can be suited perfectly to the task, but needs sufficient data

For the v2 (click  on the ... in the image), a YOLO model will be chosen under the same aspects.

## Model Performance (v1)
<img src="https://github.com/xTerradon/hcaptcha-solver/assets/64305142/3b882156-6beb-4b53-ac0c-b4eac555b45e" alt="Model Accuracy">

_(updated 12 Aug. 2023)_
