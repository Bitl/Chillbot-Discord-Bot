@ECHO off
cls

:start
cls
ECHO Chillbot Launcher
ECHO.
ECHO 1 - Start Chillbot
ECHO 2 - Update Dependencies (Do this before starting the bot for the first time!
ECHO.
ECHO 0 - Exit
ECHO.
ECHO.
SET "A="
SET /P A=Select a game:
IF "%A%"=="1" goto startbot
IF "%A%"=="2" goto updatedeps
IF "%A%"=="0" EXIT
EXIT

:startbot
cls
pushd %~dp0

::Attempts to start py launcher without relying on PATH
%SYSTEMROOT%\py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO attempt_startbot
%SYSTEMROOT%\py.exe -3.5 chillbot.py
PAUSE
GOTO end_startbot

::Attempts to start py launcher by relying on PATH
:attempt_startbot
py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO lastattempt_startbot
py.exe -3.5 chillbot.py
PAUSE
GOTO end_startbot

::As a last resort, attempts to start whatever Python there is
:lastattempt_startbot
python.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO message_startbot
python.exe chillbot.py
PAUSE
GOTO end_startbot

:message_startbot
echo Couldn't find a valid Python ^>3.5 installation. Python needs to be installed and available in the PATH environment
echo variable.
pause

:end_startbot
GOTO start

:updatedeps
cls
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
pushd %~dp0

::Attempts to start py launcher without relying on PATH
%SYSTEMROOT%\py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO attempt
%SYSTEMROOT%\py.exe -3.5 -m pip install --upgrade -r requirements.txt
PAUSE
GOTO end

::Attempts to start py launcher by relying on PATH
:attempt
py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO lastattempt
py.exe -3.5 -m pip install --upgrade -r requirements.txt
PAUSE
GOTO end

::As a last resort, attempts to start whatever Python there is
:lastattempt
python.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO message
python.exe -m pip install --upgrade -r requirements.txt
PAUSE
GOTO end

:message
echo Couldn't find a valid Python ^>3.5 installation. Python needs to be installed and available in the PATH environment
echo variable.
PAUSE

:end
GOTO start
