@echo off
echo ====================================
echo MC-BLOATWARE TOOL - Build Script
echo ====================================
echo.

REM Verificar si adb.exe existe en la carpeta actual
if not exist "adb.exe" (
    echo ERROR: No se encontro adb.exe en la carpeta actual
    echo Por favor, descarga los archivos de Android SDK Platform Tools:
    echo - adb.exe
    echo - AdbWinApi.dll
    echo - AdbWinUsbApi.dll
    echo.
    echo Coloca estos archivos en la misma carpeta que este script.
    pause
    exit /b 1
)

echo [1/3] Verificando archivos ADB...
if exist "adb.exe" echo   - adb.exe encontrado
if exist "AdbWinApi.dll" echo   - AdbWinApi.dll encontrado
if exist "AdbWinUsbApi.dll" echo   - AdbWinUsbApi.dll encontrado
echo.

echo [2/3] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "MC-BLOATWARE-TOOL.spec" del /q MC-BLOATWARE-TOOL.spec
echo.

echo [3/3] Creando ejecutable con PyInstaller...
pyinstaller --onedir --windowed --name "MC-BLOATWARE-TOOL" ^
    --icon=icono.ico ^
    --add-data "adb.exe;." ^
    --add-data "AdbWinApi.dll;." ^
    --add-data "AdbWinUsbApi.dll;." ^
    --add-data "base_de_datos.txt;." ^
    --add-data "malware_list.txt;." ^
    --add-data "icono.png;." ^
    --hidden-import=PyQt5 ^
    busqyrei.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo BUILD COMPLETADO EXITOSAMENTE!
    echo ====================================
    echo.
    echo El ejecutable se encuentra en:
    echo .\dist\MC-BLOATWARE-TOOL\
    echo.
    echo Archivos incluidos:
    echo - MC-BLOATWARE-TOOL.exe
    echo - adb.exe
    echo - AdbWinApi.dll
    echo - AdbWinUsbApi.dll
    echo - icono.png
    echo - base_de_datos.txt
    echo - malware_list.txt
    echo.
    echo Puedes copiar toda la carpeta MC-BLOATWARE-TOOL
    echo a cualquier computadora Windows y funcionara
    echo sin necesidad de tener ADB instalado.
    echo.
) else (
    echo.
    echo ====================================
    echo ERROR DURANTE EL BUILD
    echo ====================================
    echo.
    echo Verifica que tengas instaladas las dependencias:
    echo pip install pyinstaller pyqt5
    echo.
)

pause
