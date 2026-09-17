@echo off

IF %VIRTUAL_ENV%. == . GOTO activate

:loop
python boxes\scripts\boxesserver.py

goto loop

:activate

echo Activating ...
call venv-win-native\Scripts\activate
goto loop