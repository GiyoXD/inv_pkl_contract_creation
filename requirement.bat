@echo off
REM This batch file installs the required Python libraries for the project.

echo Installing required Python libraries...

REM Install openpyxl for reading and writing Excel files
pip install openpyxl

REM Install python-dateutil for parsing date strings
pip install python-dateutil

echo.
echo All necessary libraries have been installed.
pause
