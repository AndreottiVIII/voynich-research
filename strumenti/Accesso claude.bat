@echo off
rem Accesso del programma claude da riga di comando (serve all'esperimento e3d02).
rem Si apre il browser: accedi con il tuo account Claude e conferma. Poi torna qui.
"%USERPROFILE%\.local\bin\claude.exe" auth login
echo.
"%USERPROFILE%\.local\bin\claude.exe" auth status
echo.
echo Fatto. Puoi chiudere questa finestra.
pause
