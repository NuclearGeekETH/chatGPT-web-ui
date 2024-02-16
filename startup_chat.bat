@echo off

If Not Exist "%~dp0%\.venv\Scripts\activate.bat" (
	python -m venv .venv
	call "%~dp0%\.venv\Scripts\activate"
	pip install -r requirements.txt
)

call "%~dp0%\.venv\Scripts\activate"
python chat_interface.py
pause