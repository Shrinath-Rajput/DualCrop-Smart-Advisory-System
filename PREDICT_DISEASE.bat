@echo off
REM Quick Disease Prediction for Brinjal and Grapes
REM This script allows anyone to quickly test disease predictions

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo   DUALCROP DISEASE PREDICTION SYSTEM - QUICK START
echo ============================================================
echo.

if "%1"=="" (
    echo Usage:
    echo   PREDICT_DISEASE.bat [image_path]
    echo.
    echo Examples:
    echo   PREDICT_DISEASE.bat path\to\brinjal_leaf.jpg
    echo   PREDICT_DISEASE.bat path\to\grape_leaf.jpg
    echo   PREDICT_DISEASE.bat --examples
    echo.
    echo Or just drag and drop an image file onto this batch file!
    echo.
    pause
    exit /b
)

if "%1"=="--examples" (
    echo Available test images:
    echo.
    for /d %%D in (artifacts\test\*) do (
        echo   %%~nxD
        for %%F in ("%%D\*.*") do (
            echo     - %%~nxF
            exit /b
        )
    )
    pause
    exit /b
)

REM Run prediction
echo Running prediction...
echo.

python quick_predict.py "%~1"

if errorlevel 1 (
    echo.
    echo ERROR: Prediction failed!
    echo Make sure:
    echo   1. Python is installed
    echo   2. Dependencies are installed: pip install -r requirements.txt
    echo   3. Image path is correct
    echo.
)

echo.
pause
