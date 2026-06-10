@echo off
set PYTHON_EXE="C:\Users\sarav\AppData\Local\Programs\Python\Python311\python.exe"

cd backend
if not exist venv (
    %PYTHON_EXE% -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
%PYTHON_EXE% init_db.py
%PYTHON_EXE% app.py
