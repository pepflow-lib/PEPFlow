@echo off
rem
rem This script builds the project documentation and optionally serves it
rem on a local web server for previewing.
rem
rem Usage:
rem   scripts/build_doc               (Builds the documentation)
rem   scripts/build_doc --serve       (Builds and then serves the documentation)
rem   scripts/build_doc --serve-only  (Serves the documentation without building)

rem --- Configuration ---
rem Enables local scope for variables. Changes are discarded when the script ends.
setlocal

rem --- Variables ---
rem Define directories and server port for easy modification.
set "DOCS_DIR=docs"
set "BUILD_DIR=%DOCS_DIR%\build\html"
set "PORT=8000"

rem --- Main Logic ---

rem Set default flag values.
set "BUILD_FLAG=true"
set "SERVE_FLAG=false"

rem Argument Parsing Loop.
:ParseArgs
rem Check if there are any arguments left to parse.
if "%~1"=="" goto Execute

if "%~1"=="--serve" (
    set "SERVE_FLAG=true"
    shift
    goto ParseArgs
)

if "%~1"=="--serve-only" (
    set "BUILD_FLAG=false"
    set "SERVE_FLAG=true"
    shift
    goto ParseArgs
)

if "%~1"=="-h" (
    call :Usage
    goto :End
)
if "%~1"=="--help" (
    call :Usage
    goto :End
)

echo Unknown option: %1
call :Usage
goto :End


rem --- Execution ---
:Execute
if "%BUILD_FLAG%"=="true" (
    call :BuildDocs
    rem Check the error code from the BuildDocs function.
    if %ERRORLEVEL% neq 0 (
        echo ❌ Build failed. Aborting. >&2
        goto :End
    )
)

if "%SERVE_FLAG%"=="true" (
    call :ServeDocs
)

goto :End


rem --- Functions ---

:Usage
    echo.
    echo Usage: %~n0 [OPTIONS]
    echo.
    echo Builds and/or serves the project documentation.
    echo Default action is to build only.
    echo.
    echo Options:
    echo   --serve         Build the documentation and then serve it locally.
    echo   --serve-only    Serve existing documentation locally without building.
    echo   -h, --help      Display this help message and exit.
    echo.
    goto :EOF


:BuildDocs
    echo ^>^>^> Building documentation...
    rem The 'make' command. This requires 'make' to be in your system's PATH.
    call "%DOCS_DIR%\make.bat" html
    rem Capture the exit code of the last command.
    if %ERRORLEVEL% neq 0 (
        echo ❌ Error: Documentation build failed. >&2
        exit /b 1
    )
    echo ✅ Documentation built successfully in '%BUILD_DIR%'
    exit /b 0


:ServeDocs
    rem Check if the build directory exists before trying to serve.
    if not exist "%BUILD_DIR%\" (
        echo ❌ Error: Build directory '%BUILD_DIR%' not found. >&2
        echo     Please run the build first or check your DOCS_DIR configuration. >&2
        exit /b 1
    )
    echo ^>^>^> Starting local server at http://localhost:%PORT%
    echo     Serving files from '%BUILD_DIR%'
    echo     Press Ctrl+C to stop the server.
    rem This requires 'python' to be in your system's PATH.
    python -m http.server --directory "%BUILD_DIR%" %PORT%
    exit /b 0


rem --- Cleanup ---
:End
rem Discard local variables and return the script's exit code.
endlocal