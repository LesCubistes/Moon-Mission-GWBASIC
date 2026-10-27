@ECHO OFF
REM MAKEBOOT - make the Moon Mission START disk boot straight into the game.
REM Usage: MAKEBOOT drive: path\GWBASIC.EXE     for example  MAKEBOOT B: C:\DOS\GWBASIC.EXE
IF "%1"=="" GOTO HELP
IF "%2"=="" GOTO HELP
IF NOT EXIST %1MOON.BAS GOTO NOTSTART
IF NOT EXIST %2 GOTO NOBASIC
ECHO Putting DOS on the START disk in %1 ...
SYS %1
COPY %COMSPEC% %1
COPY %2 %1GWBASIC.EXE
ECHO @ECHO OFF> %1AUTOEXEC.BAT
ECHO GWBASIC MOON>> %1AUTOEXEC.BAT
ECHO.
ECHO Done. Boot from the START disk to play.
ECHO If SYS said there is no room for the system, see README.TXT.
GOTO END
:NOTSTART
ECHO %1 does not hold the Moon Mission START disk.
GOTO END
:NOBASIC
ECHO Can't find %2. Give the full path to your GWBASIC.EXE.
GOTO END
:HELP
ECHO Makes the Moon Mission START disk boot straight into the game.
ECHO Run it from DOS with the START disk in a drive:
ECHO.
ECHO    MAKEBOOT B: C:\DOS\GWBASIC.EXE
ECHO.
ECHO B: is the START disk's drive, then the path to your own GWBASIC.EXE.
ECHO It needs SYS.COM from your DOS. GW-BASIC and DOS are not included.
:END
