@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: REPOSITORY UPDATER
:: ============================================================================
:: --- This script updates the local repository with the latest changes ---
:: --- from the main branch of the remote repository. ---

:: --- Configuration ---
:: --- Assumes 'origin' is the name of your remote repository ---
:: --- and 'main' is the branch you want to update from. ---
set "REMOTE_NAME=origin"
set "BRANCH_NAME=main"

:: --- Set Paths to Portable Tools ---
:: --- These paths must match the ones in your setup script ---
set "GIT_EXECUTABLE=%~dp0portable-git\bin\git.exe"
set "REPO_DIR=%~dp0"
:: --- Sanitize the repository path by removing any trailing backslash ---
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"

:: ============================================================================
:: SCRIPT LOGIC
:: ============================================================================
echo.
echo =======================================
echo  Repository Updater
echo =======================================
echo.

:: --- Step 1: Verify it's a Git repository ---
echo [1/4] Checking for Git repository...
:: --- Check for the .git directory in the sanitized path ---
if not exist "%REPO_DIR%\.git" (
    echo   - ERROR: This is not a Git repository.
    echo   - Please ensure this script is in the root of your project folder.
    goto :error_exit
)
echo   - Git repository found.

:: --- Step 2: Fetch latest updates from the remote ---
echo [2/4] Fetching latest updates from the remote repository...
:: --- Call git.exe by its full path to avoid environment conflicts ---
"%GIT_EXECUTABLE%" -C "%REPO_DIR%" fetch %REMOTE_NAME%
if %errorlevel% neq 0 (
    echo   - ERROR: Failed to fetch updates from the remote.
    echo   - Please check your internet connection and Git configuration.
    goto :error_exit
)
echo   - Fetch successful.

:: --- Step 3: Check status ---
echo [3/4] Checking local status...
"%GIT_EXECUTABLE%" -C "%REPO_DIR%" status -uno
echo.

:: --- Step 4: Pull changes from the main branch ---
echo [4/4] Merging changes from the '%BRANCH_NAME%' branch...
"%GIT_EXECUTABLE%" -C "%REPO_DIR%" pull %REMOTE_NAME% %BRANCH_NAME%
if %errorlevel% neq 0 (
    echo   - ERROR: Failed to merge changes. You may have local conflicts.
    echo   - Please resolve any conflicts manually and then commit your changes.
    goto :error_exit
)
echo   - Merge successful.

echo.
echo =======================================
echo  Update Complete!
echo =======================================
echo Your local repository is now up-to-date with the '%BRANCH_NAME%' branch.
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
