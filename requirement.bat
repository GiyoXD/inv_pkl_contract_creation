@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: CONFIGURATION
:: ============================================================================
:: --- This script installs required tools (Python, Git) and libraries. ---
:: --- Run this script once before using update_repo.bat. ---

:: --- Configuration for portable tools (no installation needed) ---
:: --- Using %~dp0 to make paths relative to the script's location for reliability ---
set "PYTHON_VERSION=3.11.4"
set "PYTHON_DIR=%~dp0python-embed"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
set "PYTHON_ZIP_FILE=%~dp0python-embed.zip"

set "GIT_DIR=%~dp0portable-git"
set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.3/PortableGit-2.41.0.3-64-bit.7z.exe"
set "GIT_EXTRACTOR_FILE=%~dp0portable-git-installer.exe"

set "REQUIREMENTS_FILE=%~dp0requirements.txt"


:: ============================================================================
:: SCRIPT LOGIC
:: ============================================================================
echo.
echo =======================================
echo  Dependency Installer
echo =======================================
echo.
echo This script will set up Python, Git, and required libraries
echo without needing a system-wide installation.
echo.

:: --- Step 1: Check and Set Up Python ---
echo [1/3] Checking for Python...
if exist "%PYTHON_DIR%\python.exe" (
    echo   - Portable Python found.
) else (
    echo   - Python not found.
    echo   - Downloading embeddable Python...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP_FILE%'"
    if %errorlevel% neq 0 (
        echo   - ERROR: Failed to download Python. Please check your internet connection.
        goto :error_exit
    )
    echo   - Unzipping Python...
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP_FILE%' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%PYTHON_ZIP_FILE%"
    
    echo   - Setting up pip for portable Python...
    set "PATH=%PYTHON_DIR%;%PATH%"
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%~dp0get-pip.py'"
    "%PYTHON_DIR%\python.exe" "%~dp0get-pip.py" >nul
    if %errorlevel% neq 0 (
        echo   - ERROR: Failed to set up pip.
        goto :error_exit
    )
    del "%~dp0get-pip.py"
)
echo   - Python is ready.
set "PATH=%PYTHON_DIR%;%PATH%"


:: --- Step 2: Check and Set Up Git ---
echo [2/3] Checking for Git...
if exist "%GIT_DIR%\bin\git.exe" (
    echo   - Portable Git found.
    goto :Git_Ready
)

echo   - Git not found.
echo   - Downloading portable Git...
powershell -Command "Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_EXTRACTOR_FILE%'"
if %errorlevel% neq 0 (
    echo   - ERROR: Failed to download Git. Please check your internet connection.
    goto :error_exit
)
echo   - Download complete.
echo   - Extracting Git... (This may take a moment. Please wait.)

:: Use start /wait to robustly run the extractor and wait for it to finish.
start /wait "" "%GIT_EXTRACTOR_FILE%" -o"%GIT_DIR%" -y

if %errorlevel% neq 0 (
    echo   - ERROR: Git extraction failed. The installer may have had an issue.
    if exist "%GIT_EXTRACTOR_FILE%" del "%GIT_EXTRACTOR_FILE%"
    goto :error_exit
)

echo   - Extraction complete. Deleting installer file.
if exist "%GIT_EXTRACTOR_FILE%" del "%GIT_EXTRACTOR_FILE%"

:Git_Ready
echo   - Portable Git is ready.


:: --- Step 3: Install Python Requirements ---
echo [3/3] Installing Python libraries...
if exist "%REQUIREMENTS_FILE%" (
    echo   - %REQUIREMENTS_FILE% found. Installing packages...
    "%PYTHON_DIR%\python.exe" -m pip install -r "%REQUIREMENTS_FILE%"
    if %errorlevel% neq 0 (
        echo   - ERROR: Failed to install Python packages.
        goto :error_exit
    )
    echo   - Python libraries installed successfully.
) else (
    echo   - No %REQUIREMENTS_FILE% file found. Skipping.
)

echo.
echo =======================================
echo  Setup Complete!
echo =======================================
echo You can now run update_repo.bat to get your project files.
echo.
goto :end

:error_exit
echo.
echo ***************************************
echo  An error occurred. Please review the messages above.
echo ***************************************
echo.

:end
pause
endlocal
