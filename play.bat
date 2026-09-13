@echo off
REM play.bat -- launch the Alien remake (graphical, pygame).
REM
REM Double-click it, or run "play.bat" from a terminal in this folder.
REM Any arguments are passed straight through to `python -m alien_remake`, e.g.:
REM   play.bat --mode short --death random
REM   play.bat --headless 200      (no window, prints the final state)
REM
REM B3: launched with NO arguments -- the double-click and the Steam case --
REM it uses pythonw.exe, which is not a console application, so Windows does
REM not put a console window behind the game. What that window used to say now
REM appears on the game's own boot screen instead (B1/B2), and an unhandled
REM exception goes to logs\crash.log beside the settings file (B4), because
REM pythonw discards stdout and stderr entirely and a silent crash would be
REM worse than the window ever was.
REM
REM Passing ANY argument keeps python.exe and its console. --headless, --help
REM and --derive-assets are console programs whose whole output is the point,
REM and guessing which flags are which would be a rule to get wrong; "you asked
REM for something specific, so you get a terminal" is one a reader can hold.

setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No .venv found in this folder.
    echo Run the one-time setup first, per README -- Setup
    echo   python -m venv .venv
    echo   .venv\Scripts\python -m pip install -e ".[remake]"
    pause
    exit /b 1
)

if "%~1"=="" (
    if exist ".venv\Scripts\pythonw.exe" (
        start "" ".venv\Scripts\pythonw.exe" -m alien_remake
        endlocal
        exit /b 0
    )
)

".venv\Scripts\python.exe" -m alien_remake %*
if errorlevel 2 (
    echo.
    echo pygame isn't installed in this .venv. To install the graphical extra:
    echo   .venv\Scripts\python -m pip install -e ".[remake]"
    pause
)

endlocal
