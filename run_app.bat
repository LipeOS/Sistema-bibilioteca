@echo off
REM Navegar até o diretório do projeto
cd C:\Users\Bibli\Downloads\Biblioteca

REM Ativando o ambiente virtual, se houver um
call venv\Scripts\activate

REM Iniciando a aplicação Flask
python app.py

pause
