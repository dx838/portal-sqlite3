@echo off

cd /d %~dp0

@REM git init
@REM git config user.email "bingk3069@gmail.com"
@REM git config user.name "dx838"

@REM git add *
@REM git commit -m "first commit"
@REM git branch -M main
@REM git remote add origin https://github.com/dx838/fluttermusic.git
@REM git push -u origin main





@REM git remote add origin https://github.com/dx838/fluttermusic.git
@REM git branch -M main


git add *
git commit -m "commit  %date% %time%"
git push -u origin main



rem java keytool.exe -genkeypair -v -storetype JKS -keyalg RSA -keysize 2048 -validity 10000   -keystore bbmusic-keystore.jks   -alias bbmusic   -keypass passwd   -storepass passwd   -dname "CN=GD, OU=CN, O=None, L=MM, ST=NN, C=CN"

rem base64 -i  bbmusic-keystore.jks


pause
