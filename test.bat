@echo off

:: Step 1: Build the package
echo Step 1: Building the package...
poetry build

:: Step 2: Uninstall the package (if it exists)
echo Step 2: Uninstalling the package...
pip uninstall hcaptcha-solver -y

:: Step 3: Install the built package
echo Step 3: Installing the built package...
pip install dist\hcaptcha_solver-0.2.12-py2.py3-none-any.whl

:: Step 4: Run the testing script
echo Step 4: Running the testing script...
python testing\test.py

:: Pause to see the output
pause
