@echo off
chcp 65001 >nul
title TOOL TRUYỆN AUDIO ONESHOT - AUTO SETUP & RUN

echo ===============================================================================
echo     TOOL TỰ ĐỘNG SẢN XUẤT TRUYỆN AUDIO ONESHOT (YOUTUBE + TIKTOK)
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Kiem tra Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [LOI] Khong tim thay Python tren he thong!
        echo Vui long cai dat Python 3.10 tro len tai: https://www.python.org/downloads/
        echo LUU Y: Nho tich chon vao o "Add Python to PATH" khi cai dat!
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py -3
    )
) else (
    set PYTHON_CMD=python
)

echo [1/5] Kiem tra moi truong Python...
%PYTHON_CMD% --version

:: 2. Kiem tra va khoi tao moi truong ao (.venv)
if not exist ".venv\Scripts\activate.bat" (
    echo [2/5] Chua co moi truong ao .venv. Dang tu dong tao .venv...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [CANH BAO] Khong the tao .venv, se dung truc tiep Python he thong.
        set VENV_PYTHON=%PYTHON_CMD%
    ) else (
        echo [+] Da tao xong thu muc .venv!
        call .venv\Scripts\activate.bat
        set VENV_PYTHON=python
    )
) else (
    echo [2/5] Kich hoat moi truong ao .venv...
    call .venv\Scripts\activate.bat
    set VENV_PYTHON=python
)

:: 3. Cai dat thu vien tu requirements.txt
echo [3/5] Kiem tra va cai dat thu vien (requirements.txt)...
%VENV_PYTHON% -m pip install --upgrade pip --quiet
%VENV_PYTHON% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [LOI] Cai dat requirements.txt that bai!
    pause
    exit /b 1
)
echo [+] Thu vien da san sang!

:: 4. Tu dong cai dat Playwright Chromium
echo [4/5] Kiem tra va cai dat Playwright Chromium Browser...
%VENV_PYTHON% -m playwright install chromium
echo [+] Playwright Chromium da duoc cai dat!

:: 5. Kiem tra file cau hinh .env
echo [5/5] Kiem tra file cau hinh .env...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [+] Da tu dong tao file .env tu .env.example.
        echo [!] CHU Y: Vui long mo file .env de dien GEMINI_API_KEY cua ban neu muon dung AI tao kich ban.
    )
)

echo.
echo ===============================================================================
echo     MOI TRUONG SAN SANG! KHOI CHAY HE THONG...
echo ===============================================================================
echo.

%VENV_PYTHON% main.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [THONG BAO] Tien trinh da dung voi ma loi: %ERRORLEVEL%
    pause
)
