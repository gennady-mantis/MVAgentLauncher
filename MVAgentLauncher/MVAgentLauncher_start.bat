@if not defined INCLUDE echo off

pushd .

set PYTHON=
call :get_python_path PYTHON

    for %%I in (%PYTHON%) do set PPNP=%%~dpI
    echo [%PPNP%]

set TOOL_SCRIPT=%PPNP%Scripts\MVAgentLauncher-tool.exe

REM  echo [%TOOL_SCRIPT%]

set SCRIPT_DIR=%PPNP%Lib\site-packages\MVAgentLauncher

REM echo [%SCRIPT_DIR%]

cd /D "%SCRIPT_DIR%"

call "%TOOL_SCRIPT%" -g  &  exit /B 2

popd
if %errorlevel% NEQ 0 exit /B 2

REM PROCEDURE:
REM PARAMETERS:
REM DESCRIPTION:
:get_python_path outpath
setlocal

	set EXEPATH=
	call :get_path python.exe EXEPATH

 
	if not exist "%EXEPATH%" (
		set EXEPATH=c:\Python38\python.exe
	)
	if not exist "%EXEPATH%" (
		echo [%~nx0:%0] ERROR: python.exe path not found & exit /B 2
	)


	if "%~1" EQU "" echo [%~nx0:%0]: Python path found [%EXEPATH%]
endlocal & if "%~1" NEQ "" set "%1=%EXEPATH%"
goto :eof

REM PROCEDURE:
REM PARAMETERS:
REM DESCRIPTION:
:get_path exe outpath
setlocal

	set EXEPATH=%~$PATH:1

endlocal & set "%2=%EXEPATH%"
goto :eof
