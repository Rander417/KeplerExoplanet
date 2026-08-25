@echo off
rem Double-click to start the Kepler KOI explorer in your browser.
rem Needs uv (see CLAUDE.md, "Environment"); the first run creates .venv, later runs are instant.
cd /d "%~dp0"
where uv >nul 2>nul || (echo uv is not installed. See CLAUDE.md, section "Environment". & pause & exit /b 1)
uv run streamlit run app\app.py --server.headless false
pause
