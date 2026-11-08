@echo off
setlocal
if "%~1"=="" (
 echo Uso: wmk-exportar-react.cmd arquivo.wmk pasta_saida [bindings.json]
 exit /b 2
)
if "%~2"=="" (
 echo Informe a pasta de saida.
 exit /b 2
)
if "%~3"=="" (
 python "%~dp0tools\wmk-app-bridge\export.py" "%~1" --out "%~2"
) else (
 python "%~dp0tools\wmk-app-bridge\export.py" "%~1" --bindings "%~3" --out "%~2"
)
exit /b %errorlevel%
