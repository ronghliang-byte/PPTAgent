@echo off
echo 正在激活 conda trainppt 环境...
call E:\anaconda\Scripts\activate.bat trainppt
if errorlevel 1 (
    echo 激活环境失败，请检查 conda 安装路径
    pause
    exit /b 1
)

echo 当前 Python 环境：%CONDA_DEFAULT_ENV%
echo Python 路径：%PYTHONHOME%

echo 正在安装后端依赖...
pip install -r backend\requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo 安装后端依赖失败
    pause
    exit /b 1
)

echo 正在安装前端依赖...
cd frontend
call npm install
if errorlevel 1 (
    echo 安装前端依赖失败
    pause
    exit /b 1
)
cd ..

echo 正在启动服务...
python start.py

pause
