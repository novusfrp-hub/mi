# Instrucciones para crear el ejecutable de MC-BLOATWARE TOOL

## Requisitos previos

1. **Python 3.x** instalado en tu sistema
2. **PyInstaller** y **PyQt5** instalados:
   ```bash
   pip install pyinstaller pyqt5
   ```

3. **Archivos ADB** (Android Debug Bridge):
   - Descarga Android SDK Platform Tools desde: https://developer.android.com/studio/releases/platform-tools
   - Extrae los siguientes archivos en la misma carpeta que `busqyrei.py`:
     - `adb.exe`
     - `AdbWinApi.dll`
     - `AdbWinUsbApi.dll`

4. **Icono** (opcional pero recomendado):
   - Convierte `icono.png` a formato `.ico` usando una herramienta online
   - Guarda el archivo como `icono.ico` en la misma carpeta

## Método 1: Usando el script batch (Recomendado para Windows)

1. Coloca todos los archivos en una carpeta:
   ```
   tu_carpeta/
   ├── busqyrei.py
   ├── adb.exe
   ├── AdbWinApi.dll
   ├── AdbWinUsbApi.dll
   ├── icono.png
   ├── icono.ico (si lo tienes)
   ├── base_de_datos.txt
   ├── malware_list.txt
   └── build_exe.bat
   ```

2. Ejecuta `build_exe.bat` haciendo doble clic

3. El ejecutable se creará en: `dist/MC-BLOATWARE-TOOL/`

## Método 2: Usando comando manual

Ejecuta este comando en la terminal desde la carpeta del proyecto:

```bash
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
```

**Para Linux/Mac**, usa `:` en lugar de `;` en `--add-data`:
```bash
pyinstaller --onedir --windowed --name "MC-BLOATWARE-TOOL" \
    --add-data "adb.exe:." \
    --add-data "AdbWinApi.dll:." \
    --add-data "AdbWinUsbApi.dll:." \
    busqyrei.py
```

## ¿Por qué usar --onedir en lugar de --onefile?

- **--onedir**: Crea una carpeta con el ejecutable y todos los archivos necesarios
  - ✅ Los archivos DLL de ADB funcionan correctamente
  - ✅ Mejor rendimiento al iniciar
  - ✅ Más fácil de actualizar archivos individuales
  
- **--onefile**: Empaqueta todo en un solo .exe
  - ❌ Problemas con archivos DLL externos
  - ❌ Más lento al iniciar (desempaqueta todo en temporal)
  - ❌ Dificultad para acceder a archivos adjuntos

## Distribución

Una vez creado el ejecutable:

1. La carpeta `dist/MC-BLOATWARE-TOOL/` contiene TODO lo necesario
2. Puedes copiar esa carpeta completa a cualquier computadora Windows
3. **No se necesita tener ADB instalado previamente** en el sistema destino
4. El programa buscará `adb.exe` en su propia carpeta automáticamente

## Estructura final de la carpeta distribuida

```
MC-BLOATWARE-TOOL/
├── MC-BLOATWARE-TOOL.exe    (Tu aplicación)
├── adb.exe                   (ADB incluido)
├── AdbWinApi.dll            (DLL de ADB)
├── AdbWinUsbApi.dll         (DLL de ADB)
├── icono.png                (Recursos)
├── base_de_datos.txt        (Base de datos)
└── malware_list.txt         (Lista de malware)
```

## Notas importantes

1. **Primera ejecución**: El antivirus puede marcar el ejecutable como sospechoso (falso positivo común con PyInstaller). Puedes agregarlo a las excepciones.

2. **Drivers ADB**: En algunos dispositivos, es posible que necesites instalar los drivers USB del fabricante del teléfono.

3. **Depuración USB**: El dispositivo Android debe tener la "Depuración USB" activada en Opciones de desarrollador.

4. **Actualizaciones**: Si necesitas actualizar el programa, simplemente vuelve a ejecutar el script de build y reemplaza la carpeta en los equipos destino.
