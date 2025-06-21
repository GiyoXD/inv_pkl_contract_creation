@echo off
setlocal
title Python & Git Dependency Installer

:: ============================================================================
::  Configuration
:: ============================================================================
REM Set the version of Git to download.
REM Check for the latest version here: https://git-scm.com/download/win
set "GIT_VERSION=2.45.1"
set "GIT_INSTALLER=Git-%GIT_VERSION%-64-bit.exe"
set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v%GIT_VERSION%.windows.1/%GIT_INSTALLER%"
set "TEMP_DIR=%TEMP%\installer_temp"


:: ============================================================================
::  Introduction
:: ============================================================================
cls
echo #######################################################
echo #        Python & Git Dependency Installer          #
echo #######################################################
echo.
echo This script will automatically check for and install all required dependencies.
echo It will run without asking for further input.
echo.
echo Press any key to begin...
pause >nul
echo.


:: ============================================================================
::  Section 1: Python Library Installation
:: ============================================================================
echo =======================================================
echo  1. Checking for required Python libraries...
echo =======================================================
echo.
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 'pip' was not found. Please ensure Python is installed correctly.
    goto :error_exit
)
call :check_and_install_pylib "openpyxl"
call :check_and_install_pylib "python-dateutil"
goto :git_check


:: ============================================================================
::  Section 2: Automated Git Installation
:: ============================================================================
:git_check
echo =======================================================
echo  2. Checking for Git installation...
echo =======================================================
echo.

where git >nul 2>&1
if %errorlevel% equ 0 (
    echo - Git is already installed.
    for /f "delims=" %%v in ('git --version') do echo   (%%v)
    goto :success_exit
)

echo - Git is not found.
echo - The script will now attempt to download and install it automatically.
echo - This may take a few minutes. Please be patient.
echo.

REM Create a temporary directory for the download
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo Downloading Git from: %GIT_URL%
powershell -Command "Start-BitsTransfer -Source '%GIT_URL%' -Destination '%TEMP_DIR%\%GIT_INSTALLER%'"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download the Git installer. Please check your internet connection.
    goto :error_exit
)

echo Download complete. Starting silent installation...

REM Create a configuration file for silent installation.
REM This ensures Git is added to the PATH so it can be used from the command line.
set "INF_FILE=%TEMP_DIR%\git_install.inf"
(
    echo [Setup]
    echo Lang=English
    echo Group=Git
    echo NoIcons=0
    echo SetupType=default
    echo PathOption=Cmd
    echo SSLEngine=OpenSSL
    echo CRLFE=CRLFAlways
) > "%INF_FILE%"

REM Run the installer silently with the configuration file.
start /wait "" "%TEMP_DIR%\%GIT_INSTALLER%" /SILENT /LOADINF="%INF_FILE%"
if %errorlevel% neq 0 (
    echo [ERROR] Git installation failed.
    goto :error_exit
)

echo Git has been installed successfully.
echo.
echo [IMPORTANT] You must close and reopen this command window before Git will be recognized.
echo If that does not work, please restart your computer.
echo.

goto :success_exit


:: ============================================================================
::  Subroutines and Exit Points
:: ============================================================================
:check_and_install_pylib
    echo Checking for '%1'...
    pip show %1 >nul 2>&1
    if %errorlevel% equ 0 (
        echo   - '%1' is already installed.
    ) else (
        echo   - Installing '%1'...
        pip install %1 >nul
        echo   - Done.
    )
    echo.
    goto :eof

:error_exit
echo.
echo =======================================================
echo  Script finished with ERRORS.
echo =======================================================
goto :cleanup_and_end

:success_exit
echo.
echo =======================================================
echo  Dependency check finished successfully.
echo =======================================================

:cleanup_and_end
REM Clean up the downloaded installer and temp directory
if exist "%TEMP_DIR%" (
    rmdir /s /q "%TEMP_DIR%"
)
echo.
endlocal
pause