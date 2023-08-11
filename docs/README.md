> _**This project is not in a ready-to-use state.** It is currently being overhauled and will soon be usable as a python package_

## Intended functionality
`CaptchaSolver` is the parent class from which one can call:
- `is_captcha_present(selenium.webdriver)`: returns True if a solvable hCaptcha is present, otherwise False
- `solve_captcha(selenium.webdriver)`: navigates to an available hCaptcha and solves it by clicking the correct images

## Features
AI is used to solve the captchas, although it is not yet decided which one. Possibilities are:
- **Pretrained ViLT model:** https://huggingface.co/dandelin/vilt-b32-finetuned-vqa \
  -> has bad accuracy in some tasks (_see Figure "ViLT Accuracy on labeled data"_)
- **Finetuned ViLT model:** will still be slow and have lots of unwanted functionality
- **Freshly trained CNNs:** can be suited perfectly to the task, but need more data

In order to obtain the data, webscrapers and a manual classifier are used (those are already in-use).

## Figures

### Current Data Availability
![Current Data](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/7d061d03-a03e-4051-8f6c-12bdf83a8cb5)

### ViLT Accuracy on labeled data
![ViLT Accuracy](https://github.com/xTerradon/hcaptcha-solver/assets/64305142/95eedb67-e5d6-4c25-8620-f2a8d3d0ae6c){#fig:vilt-acc}

_(updated 10 Aug. 2023)_
