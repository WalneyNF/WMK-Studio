@echo off
setlocal
call "D:\one\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
if errorlevel 1 exit /b 1
cd /d "%~dp0"
rustup run 1.95.0-x86_64-pc-windows-msvc rustc --version >nul 2>&1
if errorlevel 1 (
 echo ERRO: falta instalar Rust 1.95.0 x86_64-pc-windows-msvc.
 echo Instale antes de compilar: rustup toolchain install 1.95.0-x86_64-pc-windows-msvc --profile minimal
 exit /b 2
)
echo Compilando o codigo-fonte local do WMK Studio...
cargo +1.95.0-x86_64-pc-windows-msvc build --release -p figcraft --locked
if errorlevel 1 (
 echo ERRO: a compilacao falhou. O executavel WMK Studio nao foi atualizado.
 exit /b 1
)
copy /Y "%~dp0target\release\figcraft.exe" "%~dp0target\release\WMK-Studio.exe" >nul
if errorlevel 1 (
 echo ERRO: nao foi possivel copiar o executavel WMK-Studio.exe.
 exit /b 3
)
echo SUCESSO: %~dp0target\release\WMK-Studio.exe
exit /b 0
