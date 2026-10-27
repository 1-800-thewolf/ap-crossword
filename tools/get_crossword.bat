@echo off
rem Double-click to download a crossword and make an Archipelago player YAML.
rem xword-dl doesn't install on Python 3.14 yet, so pin 3.13 (or older).
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if %errorlevel%==0 (
  uv run --quiet --no-project --python 3.13 --with xword-dl python get_crossword.py %*
  goto done
)

if not exist ".venv\Scripts\python.exe" (
  echo First run: setting up Python environment...
  for %%V in (3.13 3.12 3.11 3.10) do (
    if not exist ".venv\Scripts\python.exe" py -%%V -m venv .venv >nul 2>nul
  )
  if not exist ".venv\Scripts\python.exe" (
    echo Could not find Python 3.10-3.13. Install Python 3.13 from python.org, then run this again.
    goto done
  )
  ".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check xword-dl
)
".venv\Scripts\python.exe" get_crossword.py %*

:done
echo.
pause
