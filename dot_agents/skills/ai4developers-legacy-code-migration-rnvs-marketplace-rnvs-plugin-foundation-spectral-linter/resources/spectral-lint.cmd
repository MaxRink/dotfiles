@echo off
REM Spectral Linting Skill (Windows)
REM Purpose: Validate OpenAPI specifications against security standards and API guidelines
REM Supports: OWASP API Security Top 10, Deutsche Telekom G-API guidelines
REM
REM The script expects to live inside a "spectral\" directory alongside the ruleset files.
REM The parent directory of "spectral\" is treated as the specs directory.
REM
REM Usage: spectral-lint.cmd <path-to-spec> [OPTIONS]
REM
REM Examples:
REM   spectral-lint.cmd ..\FNCallnumberPortingMgmt\spec\FNCallnumberPortingMgmt.yaml
REM   spectral-lint.cmd .. --all --ruleset gapi
REM   spectral-lint.cmd ..\FNCallnumberPortingMgmtBff\spec\FNCallnumberPortingMgmtBff.yaml --verbose

setlocal enabledelayedexpansion

REM Script directory (where this script and rulesets live)
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
if "!SCRIPT_DIR:~-1!"=="\" set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"

REM Specs directory is the parent of the spectral\ folder
for %%A in ("!SCRIPT_DIR!\..") do set "SPECS_DIR=%%~fA"

REM Rulesets are co-located with this script
set "OWASP_RULESET=!SCRIPT_DIR!\owasp-linter-rules.spectral.yaml"
set "GAPI_RULESET=!SCRIPT_DIR!\gapi-linter-rules.spectral.yaml"
set "RULESET=!OWASP_RULESET!"

REM Display help if no arguments
if "%~1"=="" (
    call :show_help
    exit /b 1
)

if "%~1"=="--help" (
    call :show_help
    exit /b 0
)

REM Parse arguments
set "SPEC_PATH=%~1"
set "VERBOSE=false"
set "LINT_ALL=false"
set "RULESET_CHOICE=owasp"

:parse_args
shift
if not "%~1"=="" (
    if "%~1"=="--verbose" (
        set "VERBOSE=true"
        goto parse_args
    )
    if "%~1"=="--all" (
        set "LINT_ALL=true"
        goto parse_args
    )
    if "%~1"=="--ruleset" (
        if "%~2"=="" (
            echo [ERROR] Missing ruleset value
            call :show_help
            exit /b 1
        )
        set "RULESET_CHOICE=%~2"
        shift
        goto parse_args
    )
    if "%~1"=="--help" (
        call :show_help
        exit /b 0
    )
    echo [ERROR] Unknown option: %~1
    call :show_help
    exit /b 1
)

REM Select ruleset based on choice
if "!RULESET_CHOICE!"=="owasp" (
    set "RULESET=!OWASP_RULESET!"
) else if "!RULESET_CHOICE!"=="gapi" (
    set "RULESET=!GAPI_RULESET!"
) else (
    echo [ERROR] Unknown ruleset: !RULESET_CHOICE! ^(use 'owasp' or 'gapi'^)
    call :show_help
    exit /b 1
)

REM Check prerequisites
echo [INFO] Checking prerequisites...
call :check_spectral
if errorlevel 1 exit /b 1

call :check_ruleset
if errorlevel 1 exit /b 1

echo.

REM Convert relative path to absolute
for %%P in ("!SPEC_PATH!") do set "SPEC_PATH=%%~fP"

REM Lint
if "!LINT_ALL!"=="true" (
    echo [INFO] Linting all specs in directory: !SPECS_DIR!
    call :lint_all_specs
    exit /b !ERRORLEVEL!
) else (
    if exist "!SPEC_PATH!\*" (
        REM It's a directory — override SPECS_DIR and lint all
        set "SPECS_DIR=!SPEC_PATH!"
        echo [INFO] Linting all specs in directory: !SPECS_DIR!
        call :lint_all_specs
        exit /b !ERRORLEVEL!
    ) else (
        call :lint_spec "!SPEC_PATH!"
        exit /b !ERRORLEVEL!
    )
)

REM ===== FUNCTIONS =====

:show_help
echo Spectral Linting Skill - Validate OpenAPI Specifications
echo.
echo USAGE:
echo     spectral-lint.cmd ^<spec-path^> [OPTIONS]
echo.
echo ARGUMENTS:
echo     ^<spec-path^>    Path to OpenAPI spec file or directory
echo                    Examples: ..\FNCallnumberPortingMgmt\spec\FNCallnumberPortingMgmt.yaml
echo.
echo OPTIONS:
echo     --verbose      Enable verbose output from spectral
echo     --all          Lint all OpenAPI specifications in the specs directory
echo     --ruleset      Choose ruleset: 'owasp' (default) or 'gapi'
echo                    OWASP: API Security Top 10 by OWASP
echo                    GAPI: Deutsche Telekom G-API guidelines (v2.11.1)
echo     --help         Display this help message
echo.
echo EXAMPLES:
echo     spectral-lint.cmd ..\FNCallnumberPortingMgmt\spec\FNCallnumberPortingMgmt.yaml
echo     spectral-lint.cmd .. --all
echo     spectral-lint.cmd .. --all --ruleset gapi
echo     spectral-lint.cmd ..\FNCallnumberPortingMgmtBff\spec\FNCallnumberPortingMgmtBff.yaml --ruleset gapi --verbose
echo.
echo RULESETS:
echo     OWASP (default): !OWASP_RULESET!
echo     G-API:           !GAPI_RULESET!
echo.
echo REQUIREMENTS:
echo     - Node.js and npm must be installed
echo     - Run 'npm install' in the spectral\ directory to install dependencies
exit /b 0

:check_spectral
pushd "!SCRIPT_DIR!"
npx spectral --version >nul 2>&1
if errorlevel 1 (
    popd
    echo [ERROR] Spectral CLI is not installed
    echo Install it with: cd !SCRIPT_DIR! ^&^& npm install
    exit /b 1
)
for /f "tokens=*" %%i in ('npx spectral --version 2^>nul') do set "SPECTRAL_VERSION=%%i"
popd
echo [SUCCESS] Spectral CLI found: !SPECTRAL_VERSION!
exit /b 0

:check_ruleset
if not exist "!RULESET!" (
    echo [ERROR] Ruleset not found at: !RULESET!
    exit /b 1
)
for %%R in ("!RULESET!") do echo [SUCCESS] Ruleset found: %%~nxR
exit /b 0

:lint_spec
set "LSP_SPEC_PATH=%~1"

if not exist "!LSP_SPEC_PATH!" (
    echo [ERROR] Spec file not found: !LSP_SPEC_PATH!
    exit /b 1
)

for %%F in ("!LSP_SPEC_PATH!") do set "LSP_FILENAME=%%~nxF"
echo [INFO] Linting: !LSP_FILENAME!

pushd "!SCRIPT_DIR!"
if "!VERBOSE!"=="true" (
    npx spectral lint "!LSP_SPEC_PATH!" --ruleset "!RULESET!" --verbose
) else (
    npx spectral lint "!LSP_SPEC_PATH!" --ruleset "!RULESET!"
)
set "LSP_EXITCODE=!ERRORLEVEL!"
popd

if !LSP_EXITCODE! gtr 0 (
    echo [WARN] x !LSP_FILENAME! failed linting ^(see errors above^)
    exit /b 1
) else (
    echo [SUCCESS] !LSP_FILENAME! passed linting
    exit /b 0
)

:lint_all_specs
set "LAS_PASSED=0"
set "LAS_FAILED=0"
set "LAS_FOUND=0"

echo [INFO] Linting all OpenAPI specifications in: !SPECS_DIR!
echo.

for /r "!SPECS_DIR!" %%F in (*.yaml *.yml *.json) do (
    set "LAS_FILE=%%F"

    REM Skip tooling and generated files
    echo "!LAS_FILE!" | findstr /i /c:"target" /c:"node_modules" /c:"spectral" /c:"owasp" /c:"package.json" /c:"package-lock.json" /c:".openapi-generator-ignore" >nul 2>&1
    if errorlevel 1 (
        set /a LAS_FOUND+=1
        call :lint_spec "!LAS_FILE!"
        if errorlevel 1 (
            set /a LAS_FAILED+=1
        ) else (
            set /a LAS_PASSED+=1
        )
        echo.
    )
)

if !LAS_FOUND! equ 0 (
    echo [WARN] No OpenAPI spec files found in: !SPECS_DIR!
    exit /b 1
)

echo.
echo ==========================================
echo Linting Summary:
echo   Passed: !LAS_PASSED!
echo   Failed: !LAS_FAILED!
if !LAS_FAILED! gtr 0 (
    exit /b 1
) else (
    exit /b 0
)
