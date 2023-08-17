@echo off

:: Step 1: Build the package
echo Step 1: Building the package...
poetry build

:: Step 2: Uninstall the package (if it exists)
echo Step 2: Uninstalling the package...
pip uninstall hcaptcha-solver -y

:: Step 3: Install the built package
echo Step 3: Installing the built package...
set "whl_file="
for %%f in (dist\hcaptcha_solver*.whl) do (
    if not defined whl_file (
        set "whl_file=%%f"
    )
)

if defined whl_file (
    pip install %whl_file%
) else (
    echo No matching .whl file found.
)

:: Step 4: Run the testing script
echo Step 4: Running the testing script...
python testing\test.py