@echo off

SET "CONDA_PATH=D:\anaconda\condabin\conda.bat"

CALL "%CONDA_PATH%" activate crypto_bot
IF ERRORLEVEL 1 (
    echo Failed to activate the conda environment 'crypto_bot'.
    pause
    exit /b 1
)

cd /d D:\PycharmProjects\coin\1028\crypto_trading\
IF ERRORLEVEL 1 (
    echo Failed to change directory. Check if the path is correct.
    pause
    exit /b 1
)

python main.py
IF ERRORLEVEL 1 (
    echo Failed to run main.py. Please check for errors in the Python script.
    pause
    exit /b 1
)


