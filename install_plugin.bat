@echo off
REM Cadastral Automation Plugin - Installation Script for Windows
REM This script copies the plugin to your QGIS plugins directory

echo ========================================
echo Cadastral Automation Plugin Installer
echo ========================================
echo.

REM Set the QGIS plugins directory
set QGIS_PLUGINS_DIR=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins

REM Check if QGIS plugins directory exists
if not exist "%QGIS_PLUGINS_DIR%" (
    echo ERROR: QGIS plugins directory not found at:
    echo %QGIS_PLUGINS_DIR%
    echo.
    echo Please ensure QGIS 3 is installed.
    pause
    exit /b 1
)

echo QGIS plugins directory found:
echo %QGIS_PLUGINS_DIR%
echo.

REM Check if plugin folder already exists
if exist "%QGIS_PLUGINS_DIR%\cadastral_automation" (
    echo WARNING: Plugin folder already exists.
    echo This will overwrite the existing installation.
    echo.
    set /p CONTINUE="Continue? (Y/N): "
    if /i not "%CONTINUE%"=="Y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
    echo.
    echo Removing old version...
    rmdir /s /q "%QGIS_PLUGINS_DIR%\cadastral_automation"
)

REM Copy plugin folder
echo Installing plugin...
xcopy /E /I /Y "cadastral_automation" "%QGIS_PLUGINS_DIR%\cadastral_automation"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Plugin installed successfully.
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Restart QGIS
    echo 2. Go to: Plugins ^> Manage and Install Plugins
    echo 3. Click 'Installed' tab
    echo 4. Find 'Cadastral Automation' and check the box
    echo 5. Access via: Vector ^> Cadastral Automation
    echo.
) else (
    echo.
    echo ERROR: Installation failed.
    echo Please try manual installation.
    echo See PLUGIN_INSTALLATION.md for instructions.
    echo.
)

pause
