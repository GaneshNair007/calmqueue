@echo off
title CalmQueue - DEV Article Publisher
cd /d "%~dp0"
python scripts\publish_dev_article.py
pause
