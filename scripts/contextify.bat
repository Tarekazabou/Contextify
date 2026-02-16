@echo off
setlocal
pushd "%~dp0\.."
set "PYTHONPATH=%cd%;%PYTHONPATH%"
set "VENV_PY=%cd%\.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    "%VENV_PY%" -m contextify.main %*
) else (
    python -m contextify.main %*
)
popd
endlocal
