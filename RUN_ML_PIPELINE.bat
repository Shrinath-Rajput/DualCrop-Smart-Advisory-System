@echo off
REM Crop Disease Prediction System - ML Pipeline Startup Script

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ========================================================
echo  CROP DISEASE PREDICTION SYSTEM - ML PIPELINE
echo ========================================================
echo.
echo 1. Install Dependencies
echo 2. Train Model
echo 3. Test Model  
echo 4. Predict Single Image
echo 5. View Model Information
echo 6. Exit
echo.
echo ========================================================

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto train
if "%choice%"=="3" goto test
if "%choice%"=="4" goto predict
if "%choice%"=="5" goto info
if "%choice%"=="6" goto exit

echo Invalid choice. Press any key to continue...
pause >nul
goto menu

:install
echo.
echo Installing dependencies...
pip install -r requirements_ml.txt
echo.
echo Installation completed!
pause
goto menu

:train
echo.
echo Starting model training...
echo.
python train_model.py
echo.
pause
goto menu

:test
echo.
echo Starting model testing...
echo.
python test_model.py
echo.
pause
goto menu

:predict
echo.
set /p image_path="Enter image path to predict: "
if exist "%image_path%" (
    python predict.py "%image_path%"
) else (
    echo Error: File not found: %image_path%
)
echo.
pause
goto menu

:info
echo.
echo ========================================================
echo  MODEL INFORMATION
echo ========================================================
echo.
python -c "from predict import CropDiseasePredictor; p = CropDiseasePredictor(); info = p.get_model_info(); print('\nModel Info:'); [print(f'{k}: {v}') for k, v in info.items()]" 2>nul || echo Model not found. Please train the model first.
echo.
pause
goto menu

:exit
echo.
echo Goodbye!
exit /b 0
