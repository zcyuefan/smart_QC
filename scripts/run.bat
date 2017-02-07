REM: Use this script to start/stop/restart server.(not valid, just start as dev now)
REM: for example:
REM: "run.bat --sign=start --env=dev" or "run.bat /S start /E dev"
REM: "run.bat --sign=stop" or "run.bat /S stop"
REM: "run.bat --sign=restart --env=dev" or "run.bat /S restart /E dev"
@echo off
D:\05-python-projects\venv_django_xadmin\Scripts\activate
python ..\manage.py runserver --settings=django_smart_QC.settings.dev