@echo off
title 彩票数据统计与可视化系统
cd /d "%~dp0"

echo ========================================
echo   彩票数据统计与可视化系统 v1.2.0
echo ========================================
echo.
echo 正在启动，请稍候...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
