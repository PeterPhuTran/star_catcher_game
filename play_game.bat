@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHON_CMD="

for /f "delims=" %%P in ('where py.exe 2^>nul') do (
    set "PYTHON_CMD=%%P"
    goto :run
)

for %%P in (
    "%LocalAppData%\Programs\Python\Python313\python.exe"
    "%LocalAppData%\Programs\Python\Python312\python.exe"
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "%LocalAppData%\Programs\Python\Python310\python.exe"
    "%LocalAppData%\Programs\Python\Python39\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python39\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%~P"
        goto :run
    )
)

for /f "delims=" %%P in ('where python.exe 2^>nul') do (
    echo %%P | find /i "WindowsApps" >nul
    if errorlevel 1 (
        set "PYTHON_CMD=%%P"
        goto :run
    )
)

echo.
echo Python could not be found from this launcher.
echo Windows may only be seeing the Microsoft Store alias instead of a real install.
echo.
echo Try this in Command Prompt:
echo 1. where py
echo 2. where python
echo.
echo If your real Python path appears there, I can wire the launcher to it directly.
pause
goto :end

:run
"%PYTHON_CMD%" main.py
if errorlevel 1 goto :python_error
goto :end

:python_error
echo.
echo The game closed because Python reported an error.
echo Read the message above, then press any key to close this window.
pause

:end
endlocal
