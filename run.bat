@echo off
REM Sobe o Langflow localmente com os componentes da CMAA e as chaves do .env
cd /d "%~dp0"
if not exist .env (
  echo Crie o arquivo .env antes. Veja o README.
  exit /b 1
)
if not exist .venv\Scripts\python.exe (
  echo Criando ambiente .venv com Python 3.13...
  py -3.13 -m venv .venv || exit /b 1
  .venv\Scripts\python.exe -m pip install -q --upgrade pip uv
)
if not exist .venv\Scripts\langflow.exe (
  echo Instalando Langflow, a primeira vez demora alguns minutos...
  .venv\Scripts\python.exe -m uv pip install --python .venv\Scripts\python.exe -r requirements.txt || exit /b 1
)
set LANGFLOW_AUTO_LOGIN=true
.venv\Scripts\langflow.exe run --host 127.0.0.1 --port 7860 --components-path components --env-file .env
